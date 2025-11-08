# Hospital_bd — Sistema de Gerenciamento Hospitalar (Django)

Este repositório contém um projeto Django simples para gerenciar usuários e recursos hospitalares. O objetivo é servir como base para um sistema de cadastro/login e gerenciamento básico de dados (pacientes, profissionais, consultas, etc.).

## Visão geral rápida

- Framework: Django (Python)
- Banco de dados em desenvolvimento: SQLite (arquivo `db.sqlite3`)
- Organização mínima: uma app principal chamada `app` e o pacote de configuração `projeto`.

## Estrutura do projeto

```
projeto/
├── manage.py            # Script de gerenciamento do Django
├── db.sqlite3           # Banco de dados SQLite (desenvolvimento)
├── app/                 # App principal do projeto
│   ├── admin.py         # Registro de models no admin
│   ├── apps.py          # Configurações da app
│   ├── models.py        # Modelos (tabelas) do Django
│   ├── views.py         # Views / lógica de apresentação
│   ├── urls.py          # Rotas da app
│   ├── templates/       # Templates HTML
│   │   └── usuarios/    # Templates de autenticação (base, cadastro, login)
│   └── tests.py         # Testes da app
└── projeto/             # Configurações do projeto Django
    ├── settings.py     # Configurações (INSTALLED_APPS, DB, static, templates)
    ├── urls.py         # URLs de nível de projeto (include das apps)
    ├── wsgi.py         # Entrada para servidores WSGI
    └── asgi.py         # Entrada para servidores ASGI
```

## Descrição das principais pastas/arquivos

- `app/models.py` — contém as classes que definem as tabelas do banco (ex.: Usuário estendido, Paciente, Consulta).
- `app/views.py` — contém as funções/classes que processam requisições e retornam respostas (templates ou JSON).
- `app/urls.py` — mapeia endpoints da app para as views correspondentes.
- `app/templates/usuarios/` — templates HTML para cadastro e login. `base.html` normalmente contém o layout base.
- `projeto/settings.py` — arquivo central de configuração (debug, caminhos, apps instaladas, banco de dados, staticfiles, templates).
- `manage.py` — utilitário para rodar comandos Django (migrate, runserver, createsuperuser, test).

## Requisitos

- Python 3.8+ (recomendo 3.11)
- pip
- Virtualenv recomendado para isolar dependências

## Instalação e execução (PowerShell)

1. Crie e ative um ambiente virtual (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instale dependências (se houver `requirements.txt`) ou apenas Django:

```powershell
pip install -r requirements.txt  # se existir
# ou
pip install django
```

3. Rode as migrações e crie um superusuário (opcional):

```powershell
python manage.py migrate
python manage.py createsuperuser
```

4. Inicie o servidor de desenvolvimento:

```powershell
python manage.py runserver
```

5. Abra no navegador:

http://127.0.0.1:8000/

## Testes

Execute a suíte de testes da app:

```powershell
python manage.py test
```

## Boas práticas e dicas de desenvolvimento

- Use `requirements.txt` ou `pyproject.toml` para travar dependências.
- Mantenha configurações sensíveis (SECRET_KEY, DB credentials) fora do repositório — use variáveis de ambiente ou um arquivo `.env` (e não comite esse arquivo).
- Sempre rode `makemigrations` e `migrate` ao alterar modelos:

```powershell
python manage.py makemigrations
python manage.py migrate
```

## Como contribuir

1. Fork ou clone este repositório
2. Crie uma branch para sua feature: `git checkout -b feature/minha-feature`
3. Faça commits claros e pequenos
4. Abra um Pull Request descrevendo sua alteração

## Próximos passos sugeridos (features)

- Adicionar models para Paciente, Médico, Consulta e Agendamento
- Implementar views e formulários para CRUD dessas entidades
- Adicionar autenticação por tokens (DRF) e uma API REST
- Criar testes unitários para models e views

## Licença

Adicione aqui a licença do projeto (por exemplo MIT) ou remova esta seção se não aplicar.

---

Se quiser, eu posso também:

- Gerar um `requirements.txt` com as dependências atuais (se você me disser quais pacotes estão instalados)
- Adicionar instruções específicas de deploy (Docker, Gunicorn + Nginx)
- Criar um arquivo `CONTRIBUTING.md` ou `LICENSE`

Arquivo atualizado: `README.md` — atualizado para fornecer instruções completas de uso e contribuição.
