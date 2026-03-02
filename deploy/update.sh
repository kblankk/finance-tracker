#!/bin/bash
# FinanceTracker - Script de atualizacao
# Executar como root: sudo bash update.sh

set -e

APP_DIR="/opt/finance-tracker"
APP_USER="finance"

echo "=== Atualizando FinanceTracker ==="

cd $APP_DIR

echo "[1/4] Baixando atualizacoes..."
su - $APP_USER -c "cd $APP_DIR && git pull"

echo "[2/4] Instalando dependencias..."
su - $APP_USER -c "cd $APP_DIR && venv/bin/pip install -r requirements.txt"

echo "[3/4] Migrando banco de dados..."
su - $APP_USER -c "cd $APP_DIR && venv/bin/flask db upgrade"

echo "[4/4] Reiniciando servico..."
systemctl restart financetracker

echo "=== Atualizacao concluida! ==="
