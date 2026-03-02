#!/bin/bash
# FinanceTracker - Script de deploy para Ubuntu (Oracle Cloud VPS)
# Executar como root: sudo bash setup.sh

set -e

APP_USER="finance"
APP_DIR="/opt/finance-tracker"
REPO_URL="https://github.com/kblankk/finance-tracker.git"
DOMAIN="_"  # Altere para seu dominio se tiver

echo "=== FinanceTracker - Deploy Setup ==="

# 1. Atualizar sistema e instalar dependencias
echo "[1/8] Atualizando sistema..."
apt update && apt upgrade -y
apt install -y python3 python3-venv python3-pip nginx git

# 2. Criar usuario do app
echo "[2/8] Criando usuario..."
id -u $APP_USER &>/dev/null || useradd -m -s /bin/bash $APP_USER

# 3. Clonar repositorio
echo "[3/8] Clonando repositorio..."
if [ -d "$APP_DIR" ]; then
    cd $APP_DIR && git pull
else
    git clone $REPO_URL $APP_DIR
fi
chown -R $APP_USER:$APP_USER $APP_DIR

# 4. Criar ambiente virtual e instalar dependencias
echo "[4/8] Instalando dependencias Python..."
cd $APP_DIR
su - $APP_USER -c "cd $APP_DIR && python3 -m venv venv && venv/bin/pip install -r requirements.txt"

# 5. Criar arquivo .env de producao
echo "[5/8] Configurando .env..."
if [ ! -f "$APP_DIR/.env" ]; then
    SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    cat > $APP_DIR/.env << EOF
SECRET_KEY=$SECRET
FLASK_APP=run.py
FLASK_ENV=production
EOF
    chown $APP_USER:$APP_USER $APP_DIR/.env
    echo "  .env criado com SECRET_KEY segura"
else
    echo "  .env ja existe, mantendo"
fi

# 6. Criar banco de dados
echo "[6/8] Configurando banco de dados..."
su - $APP_USER -c "cd $APP_DIR && venv/bin/flask db upgrade && python3 seed.py"

# 7. Configurar systemd service
echo "[7/8] Configurando servico systemd..."
cat > /etc/systemd/system/financetracker.service << EOF
[Unit]
Description=FinanceTracker Flask App
After=network.target

[Service]
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 wsgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable financetracker
systemctl start financetracker

# 8. Configurar Nginx
echo "[8/8] Configurando Nginx..."
cat > /etc/nginx/sites-available/financetracker << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias $APP_DIR/app/static;
        expires 30d;
    }
}
EOF

ln -sf /etc/nginx/sites-available/financetracker /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

echo ""
echo "=== Deploy concluido! ==="
echo "App rodando em: http://$(curl -s ifconfig.me)"
echo "Admin: admin@financetracker.com / admin123"
echo ""
echo "Comandos uteis:"
echo "  sudo systemctl status financetracker  - Ver status"
echo "  sudo systemctl restart financetracker - Reiniciar app"
echo "  sudo journalctl -u financetracker -f  - Ver logs"
