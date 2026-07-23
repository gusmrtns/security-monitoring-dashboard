# Security Monitoring Dashboard

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)
![Pytest](https://img.shields.io/badge/Tests-9%20passing-brightgreen)
![Status](https://img.shields.io/badge/Status-Conclu%C3%ADdo-brightgreen)

Dashboard web em Flask para visualização e triagem de achados de segurança, com autenticação de usuário, filtros combináveis e gráficos interativos.

## Por que este projeto

Um SOC não trabalha só com terminal e SIEM — a triagem do dia a dia acontece em dashboards web: filtrar por severidade, acompanhar tendência ao longo do tempo, mudar o status de um achado depois de investigar. Este projeto implementa essa camada, com foco em fazer bem-feito o básico de uma aplicação web em produção: autenticação segura, proteção CSRF, hash de senha, e separação de responsabilidades via Blueprints — não em UI sofisticada (isso fica para uma fase futura de melhorias).

## Arquitetura

```
seed_data.py (gera usuários + achados sintéticos, seed fixa)
        ↓
   SQLite (security_dashboard.db)
        ↓
   Blueprints Flask (auth / dashboard / findings)
        ↓
   Templates Jinja2 + Chart.js (via endpoints JSON internos /api/charts/*)
```

Application factory (`create_app()`) em vez de uma instância global de Flask — facilita testes isolados e evita imports circulares entre blueprints e extensões (`db`, `login_manager`, `csrf` ficam centralizados em `extensions.py`).

```
security-dashboard/
├── app.py                     # Application factory + entrypoint
├── config.py                  # Configuração (SECRET_KEY, DB URI)
├── extensions.py              # Instâncias compartilhadas: db, login_manager, csrf
├── seed_data.py                # Gera usuários + achados sintéticos para teste
├── models/
│   ├── user.py                 # Usuário + hash de senha (Werkzeug)
│   └── finding.py              # Achado de segurança
├── blueprints/
│   ├── auth/                   # /auth/login, /auth/logout
│   ├── dashboard/               # /dashboard + /api/charts/* (JSON p/ Chart.js)
│   └── findings/                # /findings (lista + filtros) + /findings/<id>
├── templates/                  # Jinja2 (base + auth/dashboard/findings)
├── static/
│   ├── css/style.css
│   └── js/dashboard-charts.js   # fetch() nos endpoints JSON + renderização Chart.js
└── tests/
    └── test_routes.py           # pytest: auth, filtros, atualização de status
```

## Funcionalidades

- **Autenticação**: login/logout com Flask-Login, senha com hash (Werkzeug `generate_password_hash`, nunca texto puro), proteção CSRF em todos os formulários (Flask-WTF)
- **Visão geral**: cards de resumo (total, em aberto, severidade Alta) + 4 gráficos (severidade, categorias, linha do tempo de 14 dias, top 8 IPs de origem)
- **Listagem de achados**: filtros combináveis via query string (severidade, categoria, status, técnica MITRE, busca livre) — URL compartilhável/bookmarkável, com paginação
- **Detalhe do achado**: visualização completa + atualização de status (`novo` → `investigando` → `resolvido`)

## Modelo de dados

Duas tabelas, propositalmente simples — o foco do projeto é a camada web, não modelagem de banco:

- **`User`**: `username`, `password_hash`, `role`
- **`SecurityFinding`**: `timestamp`, `severity`, `category`, `title`, `description`, `source_ip`, `mitre_technique`, `status`

O vocabulário de severidade e categorias (`brute_force`, `endpoint_scan`, `account_creation` etc.) segue o mesmo padrão do [Log Security Analyzer](https://github.com/gusmrtns/log-security-analyzer), mantendo os projetos consistentes entre si mesmo sem integração automática ainda.

## Instalação

```bash
git clone https://github.com/gusmrtns/security-dashboard.git
cd security-dashboard
pip install -r requirements.txt
```

## Uso

Popular o banco com dados sintéticos (usuários + achados de teste):

```bash
python seed_data.py --reset --count 100
```

Isso cria dois usuários de teste:

| Usuário   | Senha        | Papel   |
| --------- | ------------ | ------- |
| `admin`   | `admin123`   | admin   |
| `analyst` | `analyst123` | analyst |

> Credenciais apenas para ambiente local de portfólio — nunca use senhas fixas como essas em produção.

Rodar a aplicação:

```bash
python app.py
```

Acessar em `http://127.0.0.1:5000`.

## Testes

```bash
pytest -v
```

9 testes cobrindo autenticação (login obrigatório, credenciais inválidas, logout), filtros de achados e atualização de status.

## Validação com dados sintéticos

O banco é populado por `seed_data.py` (seed fixa para reprodutibilidade) com 100 achados distribuídos nos últimos 30 dias, cobrindo as 7 categorias e as 3 severidades em proporções realistas (força bruta e varredura de endpoints tendem a Alta; acesso fora de horário tende a Média). Validação end-to-end feita via requisições HTTP diretas (login com token CSRF real, consumo dos 4 endpoints de gráfico, filtro por severidade, atualização de status) confirmando que todo o fluxo funciona de ponta a ponta antes da entrega.

## Próximos passos

- Integração real com os dados do Wazuh Home Lab e do Log Security Analyzer (hoje os 3 projetos rodam de forma independente, propositalmente, para entrega no curto prazo)
- Frontend mais elaborado (hoje o CSS é propositalmente simples)
- Papéis de usuário com permissões diferenciadas (`admin` vs `analyst`)
- Deploy (Docker + banco além de SQLite)

## Stack

Python 3.10+, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, SQLite, Chart.js, pytest, GitHub Actions (CI).

## Projetos relacionados

- [Wazuh SIEM Home Lab](https://github.com/gusmrtns/wazuh-home-lab) — ambiente de SIEM completo com detecção de 5 técnicas MITRE ATT&CK
- [Log Security Analyzer](https://github.com/gusmrtns/log-security-analyzer) — CLI em Python para análise automatizada de logs de segurança

## Autor

Francisco Gustavo Martins de Sousa — Estudante de Ciência da Computação (UFC), foco em Segurança Defensiva.
[LinkedIn](https://linkedin.com/in/gus-martins) · [GitHub](https://github.com/gusmrtns)
