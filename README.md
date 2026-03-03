# FinanceTracker

Sistema web de controle financeiro pessoal desenvolvido com Python e Flask. O objetivo do projeto e facilitar o acompanhamento de receitas, despesas, parcelas e metas de economia no dia a dia.

## Sobre o Projeto

O FinanceTracker nasceu da necessidade de ter um controle financeiro simples e visual, sem depender de planilhas. A aplicacao permite cadastrar receitas e despesas, acompanhar parcelas, definir orcamentos mensais por categoria e criar metas de economia, tudo com um dashboard que mostra a situacao financeira do mes.

### Principais funcionalidades

- **Dashboard** com resumo do mes, graficos interativos e proximas contas a vencer
- **Receitas e Despesas** com categorias, filtros avancados e exportacao em CSV
- **Parcelas** que geram as despesas automaticamente com valor adicional configuravel
- **Orcamento mensal** por categoria, com barras de progresso mostrando o quanto ja foi gasto
- **Metas de economia** com contribuicoes e acompanhamento do progresso
- **Relatorios** comparando receitas e despesas entre meses diferentes
- **Lembretes** para nao esquecer contas proximas do vencimento
- **Tema dark/light** e layout responsivo com navegacao adaptada para celular

### Capturas de tela

*Em breve*

## Tecnologias utilizadas

- **Backend:** Python 3.10+, Flask 3, SQLAlchemy, Flask-Migrate
- **Banco de dados:** SQLite (desenvolvimento) / PostgreSQL (producao)
- **Autenticacao:** Flask-Login, Flask-Bcrypt, Flask-WTF (CSRF)
- **Frontend:** Bootstrap 5.3, Chart.js 4, Jinja2
- **Deploy:** Gunicorn + Nginx

## Como contribuir

1. Faca um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas alteracoes (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licenca

Distribuido sob a licenca MIT.
