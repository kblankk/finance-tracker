# FinanceTracker

Aplicacao web de gerenciamento financeiro pessoal desenvolvida com Flask e Python.
Permite controle de receitas, despesas, contas a pagar, lembretes e dashboard com graficos.

## Funcionalidades

- **Multi-usuario** com sistema de registro e login
- **Aprovacao pelo admin** - novos usuarios precisam ser aprovados
- **Receitas** - CRUD completo com categorias, fontes e recorrencia
- **Despesas/Contas** - CRUD com data de vencimento, status de pagamento e prioridade
- **Dashboard** - Cards resumo + graficos interativos (Chart.js)
- **Lembretes** - Notificacoes in-app para contas proximas ao vencimento
- **Painel Admin** - Gerenciamento de usuarios (aprovar, desativar, remover)
- **Exportar CSV** - Download de receitas e despesas em planilha
- **Tema Dark/Light** - Alternancia de tema com persistencia local
- **Responsivo** - Interface adaptada para desktop e mobile

## Tecnologias

| Tecnologia | Uso |
|---|---|
| Python 3.10+ | Linguagem principal |
| Flask 3.x | Framework web |
| SQLAlchemy | ORM para banco de dados |
| SQLite | Banco de dados |
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

# Criar banco de dados
flask db init
flask db migrate -m "initial"
flask db upgrade

# Criar admin e categorias padrao
python seed.py

# Executar
flask run
```

### Acesso
- Abra o navegador em `http://localhost:5000`
- Login admin padrao: `admin@financetracker.com` / `admin123`

## Estrutura do Projeto

```
finance-tracker/
├── app/
│   ├── __init__.py       # Application factory
│   ├── extensions.py     # Flask extensions
│   ├── models/           # Modelos do banco (User, Income, Expense, Category, Reminder)
│   ├── auth/             # Login, registro, logout
│   ├── main/             # Dashboard e API dos graficos
│   ├── income/           # CRUD de receitas
│   ├── expenses/         # CRUD de despesas/contas
│   ├── admin/            # Painel administrativo
│   ├── reminders/        # Sistema de lembretes
│   ├── static/           # CSS e JavaScript
│   └── templates/        # Templates HTML (Jinja2)
├── config.py             # Configuracoes (Dev/Prod/Test)
├── run.py                # Entry point
├── seed.py               # Seed do banco de dados
└── requirements.txt      # Dependencias Python
```

## Screenshots

*Em breve*

## Licenca

Este projeto e open source sob a licenca MIT.
