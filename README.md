# FinanceTracker

App web pra gerenciar minhas financas pessoais. Feito com Flask + Bootstrap.

Controla receitas, despesas, parcelas, orcamento por categoria e metas de economia. Tem dashboard com graficos, tema dark/light e funciona no celular tambem.

## O que tem

- Login com aprovacao do admin
- Dashboard com resumo do mes, graficos e proximas contas
- Receitas e despesas com filtros (data, categoria, valor, busca)
- Parcelamento que gera as despesas automaticamente
- Orcamento mensal por categoria
- Metas de economia com contribuicoes
- Relatorios comparando meses
- Lembretes de contas a vencer
- Exportar pra CSV
- Tema dark/light
- Navegacao mobile com barra inferior

## Stack

- Python 3.10+ / Flask 3
- SQLAlchemy + SQLite (dev) / PostgreSQL (prod)
- Flask-Login, Flask-Bcrypt, Flask-WTF, Flask-Migrate
- Bootstrap 5.3 + Chart.js 4

## Rodando local

```bash
git clone https://github.com/kblankk/finance-tracker.git
cd finance-tracker
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt
cp .env.example .env      # editar com sua SECRET_KEY
flask db upgrade
python seed.py
flask run
```

Abre `http://localhost:5000` no navegador. Credenciais do admin ficam no `seed.py`.

## Estrutura

```
app/
├── models/           # User, Income, Expense, Category, Budget, etc
├── auth/             # Login, registro, logout
├── main/             # Dashboard
├── income/           # Receitas
├── expenses/         # Despesas
├── installments/     # Parcelas
├── budgets/          # Orcamento
├── savings/          # Metas
├── reports/          # Relatorios
├── admin/            # Painel admin
├── reminders/        # Lembretes
├── static/           # CSS, JS
└── templates/        # HTML (Jinja2)
```

## Producao

```bash
gunicorn --workers 2 --bind 127.0.0.1:8000 wsgi:application
```

## Licenca

MIT
