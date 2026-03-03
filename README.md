# FinanceTracker

Aplicacao web de gerenciamento financeiro pessoal desenvolvida com Flask e Python.
Permite controle de receitas, despesas, parcelas, orcamentos, metas de economia e muito mais.

## Funcionalidades

- **Multi-usuario** com sistema de registro, login e aprovacao pelo admin
- **Dashboard** - Cards resumo, graficos interativos (Chart.js), proximas contas e transacoes recentes
- **Receitas** - CRUD completo com categorias, fontes e recorrencia
- **Despesas/Contas** - CRUD com vencimento, status de pagamento, prioridade e filtros avancados
- **Parcelas** - Parcelamento automatico com geracao de despesas mensais e valor adicional por mes
- **Orcamento Mensal** - Limite de gastos por categoria com barras de progresso
- **Metas de Economia** - Metas com contribuicoes, progresso visual e prazos
- **Relatorios** - Comparacao mensal lado a lado com variacoes percentuais
- **Lembretes** - Notificacoes in-app para contas proximas ao vencimento
- **Filtros** - Busca por data, categoria, valor e texto em receitas e despesas
- **Painel Admin** - Gerenciamento de usuarios (aprovar, desativar, remover)
- **Exportar CSV** - Download de receitas e despesas em planilha
- **Tema Dark/Light** - Alternancia de tema com persistencia local
- **Responsivo** - Interface adaptada para desktop e mobile com navegacao inferior

## Tecnologias

| Tecnologia | Uso |
|---|---|
| Python 3.10+ | Linguagem principal |
| Flask 3.x | Framework web |
| SQLAlchemy | ORM para banco de dados |
| SQLite / PostgreSQL | Banco de dados (dev / prod) |
| Flask-Login | Autenticacao de usuarios |
| Flask-Bcrypt | Hash de senhas |
| Flask-WTF | Formularios e CSRF |
| Flask-Migrate | Migracoes do banco |
| Bootstrap 5.3 | Framework CSS (dark mode nativo) |
| Chart.js 4 | Graficos interativos |

## Como Executar

### Pre-requisitos
- Python 3.10 ou superior
- pip

### Instalacao

```bash
# Clonar o repositorio
git clone https://github.com/kblankk/finance-tracker.git
cd finance-tracker

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variaveis de ambiente
cp .env.example .env
# Edite o .env com sua SECRET_KEY e DATABASE_URL

# Criar banco de dados
flask db upgrade

# Criar admin e categorias padrao
python seed.py

# Executar
flask run
```

### Acesso
- Abra o navegador em `http://localhost:5000`
- As credenciais do admin sao definidas no arquivo `seed.py`

## Estrutura do Projeto

```
finance-tracker/
├── app/
│   ├── __init__.py       # Application factory
│   ├── extensions.py     # Flask extensions
│   ├── models/           # Modelos (User, Income, Expense, Category, Budget, etc)
│   ├── auth/             # Login, registro, logout
│   ├── main/             # Dashboard e API dos graficos
│   ├── income/           # CRUD de receitas
│   ├── expenses/         # CRUD de despesas/contas
│   ├── installments/     # Parcelamentos
│   ├── budgets/          # Orcamento mensal por categoria
│   ├── savings/          # Metas de economia
│   ├── reports/          # Relatorios mensais
│   ├── admin/            # Painel administrativo
│   ├── reminders/        # Sistema de lembretes
│   ├── static/           # CSS e JavaScript
│   └── templates/        # Templates HTML (Jinja2)
├── config.py             # Configuracoes (Dev/Prod/Test)
├── run.py                # Entry point (dev)
├── wsgi.py               # Entry point (producao)
├── seed.py               # Seed do banco de dados
└── requirements.txt      # Dependencias Python
```

## Deploy

Para deploy em producao com Gunicorn + Nginx:

```bash
gunicorn --workers 2 --bind 127.0.0.1:8000 wsgi:application
```

## Licenca

Este projeto e open source sob a licenca MIT.
