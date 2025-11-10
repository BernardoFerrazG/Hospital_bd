# Hospital_bd — Sistema de Gerenciamento Hospitalar (Django)

Este repositório contém um projeto Django para gerenciar usuários e recursos hospitalares. O sistema implementa autenticação de usuários, cadastro de diferentes tipos de profissionais (médicos, enfermeiros, administradores) e pacientes, com papéis e níveis de acesso diferenciados.

## Visão geral rápida

- **Framework**: Django 5.2.8
- **Linguagem**: Python 3.11+
- **Banco de dados (desenvolvimento)**: SQLite (`db.sqlite3`)
- **Autenticação**: Integrada com Django User + modelos customizados
- **Estrutura**: Uma app principal (`app`) e pacote de configuração (`projeto`)

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

### Modelos (`app/models.py`)
- **Pessoa** — Entidade base com CPF, nome, sexo, telefone, email e data de nascimento
- **Funcionario** — Estende Pessoa, adiciona salário e horas trabalhadas
- **Medico** — Funcionário com CRM (Conselho Regional de Medicina)
- **Enfermeiro** — Funcionário com COREN (Conselho Regional de Enfermagem)
- **Paciente** — Pessoa que recebe atendimento
- **Administrador** — Funcionário com permissões administrativas
- **Consultorio** — Espaço identificado por andar/número, vinculado a departamento e médico
- **Sala_Cirurgia** — Sala para procedimentos cirúrgicos
- **Departamento** — Unidade organizacional gerenciada por administrador

### Views (`app/views.py`)
- **cadastro()** — Permite registro de novos usuários (suporta múltiplos papéis: médico, enfermeiro, etc.)
- **login()** — Autentica usuários Django existentes
- **home()** — Página inicial protegida por login
- **home_med()** — Dashboard específico para médicos
- **home_enf()** — Dashboard específico para enfermeiros
- **home_admin()** — Dashboard específico para administradores
- **plataforma()** — Página da plataforma

### Arquivos de Configuração
- `app/urls.py` — Mapeia endpoints da app para as views correspondentes
- `app/admin.py` — Registro de models no painel administrativo Django
- `proyecto/settings.py` — Configurações centrais (DEBUG, INSTALLED_APPS, banco de dados, templates)
- `proyecto/urls.py` — URLs de nível de projeto
- `manage.py` — Utilitário para rodar comandos Django (migrate, runserver, createsuperuser)

### Templates (`app/templates/usuarios/`)
- `base.html` — Template base com layout geral
- `cadastro.html` — Formulário de cadastro de novos usuários
- `login.html` — Formulário de autenticação
- `home.html` — Página inicial pós-login
- `home_med.html` — Dashboard para médicos
- `home_enf.html` — Dashboard para enfermeiros
- `home_admin.html` — Dashboard para administradores

### Banco de Dados
- `schema.sql` — Schema completo do banco (tabelas, chaves estrangeiras, relacionamentos)
- `db.sqlite3` — Arquivo do banco de dados SQLite (desenvolvimento)

## Requisitos

- Python 3.8+ (recomendado 3.11+)
- pip
- Virtual Environment (venv) - recomendado para isolar dependências

## Dependências do Projeto

- Django 5.2.8
- Outras dependências conforme listadas no `requirements.txt` (se existir)

## Instalação e execução (PowerShell)

### 1. Clonar o repositório

```powershell
git clone https://github.com/BernardoFerrazG/Hospital_bd.git
cd Hospital_bd
```

### 2. Criar e ativar ambiente virtual

```powershell
# Criar
python -m venv venv

# Ativar (PowerShell)
.\venv\Scripts\Activate.ps1
```

### 3. Instalar dependências

```powershell
pip install -r requirements.txt
```

Se não existir `requirements.txt`, instale manualmente:

```powershell
pip install django==5.2.8
```

### 4. Aplicar migrações

```powershell
cd projeto
python manage.py migrate
```

### 5. Criar superusuário (admin)

```powershell
python manage.py createsuperuser
```

### 6. Executar servidor de desenvolvimento

```powershell
python manage.py runserver
```

O servidor estará disponível em `http://127.0.0.1:8000/`

## URLs principais

Após iniciar o servidor:

- `http://127.0.0.1:8000/admin/` — Painel administrativo Django
- `http://127.0.0.1:8000/auth/cadastro/` — Cadastro de novos usuários
- `http://127.0.0.1:8000/auth/login/` — Página de login
- `http://127.0.0.1:8000/auth/home/` — Dashboard inicial (requer autenticação)
- `http://127.0.0.1:8000/auth/home_med/` — Dashboard de médicos (requer autenticação)
- `http://127.0.0.1:8000/auth/home_enf/` — Dashboard de enfermeiros (requer autenticação)
- `http://127.0.0.1:8000/auth/home_admin/` — Dashboard administrativo (requer autenticação)

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
