# FinanceTracker

Aplicacao web para gerenciamento de financas pessoais, feita com Flask e Bootstrap.

## Funcionalidades

- Sistema de login com aprovacao de novos usuarios pelo admin
- Dashboard com resumo mensal, graficos de receitas vs despesas e despesas por categoria
- Cadastro de receitas e despesas com filtros por data, categoria, valor e busca
- Parcelamento automatico que gera as despesas mes a mes
- Orcamento mensal por categoria com barra de progresso
- Metas de economia com contribuicoes e acompanhamento visual
- Relatorios com comparacao entre meses
- Lembretes para contas proximas do vencimento
- Exportacao de dados em CSV
- Tema dark e light com alternancia
- Layout responsivo com navegacao inferior no celular

## Tecnologias

- Python 3.10+ com Flask 3
- SQLAlchemy + Flask-Migrate (SQLite em dev, PostgreSQL em prod)
- Flask-Login, Flask-Bcrypt, Flask-WTF
- Bootstrap 5.3 e Chart.js 4
