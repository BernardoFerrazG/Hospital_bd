# 🏥 Hospital_bd — Sistema de Gerenciamento Hospitalar

Um projeto Django robusto para gerenciamento de recursos hospitalares, com sistema de autenticação multi-papel, cadastro de profissionais e pacientes, e gerenciamento de departamentos.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Modelos de Dados](#modelos-de-dados)
- [Funcionalidades](#funcionalidades)
- [Fluxos de Trabalho](#fluxos-de-trabalho)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Endpoints da API](#endpoints-da-api)
- [Modelos de Papel (Roles)](#modelos-de-papel-roles)

---

## 👀 Visão Geral

| Aspecto            | Detalhe                                   |
| ------------------ | ----------------------------------------- |
| **Framework**      | Django 5.2.8                              |
| **Linguagem**      | Python 3.11+                              |
| **Banco de Dados** | SQLite (`db.sqlite3`)                     |
| **Autenticação**   | Django User + Modelos customizados        |
| **Arquitetura**    | App Django modular com papéis específicos |

---

## 📁 Estrutura do Projeto

```
Hospital_bd/
│
├── README.md              # Este arquivo
├── schema.sql             # Schema do banco de dados (SQL puro)
│
└── projeto/               # Raiz do projeto Django
    ├── manage.py          # CLI do Django
    ├── db.sqlite3         # Banco de dados (desenvolvimento)
    │
    ├── app/               # App principal
    │   ├── __init__.py
    │   ├── admin.py       # Registro de modelos no admin do Django
    │   ├── apps.py        # Configurações da app
    │   ├── models.py      # Modelos ORM (Pessoa, Funcionario, Medico, etc)
    │   ├── views.py       # Views principais (cadastro, login, landing)
    │   ├── urls.py        # Rotas da app
    │   ├── tests.py       # Testes unitários
    │   │
    │   ├── medico/        # Módulo específico para Médicos
    │   │   ├── __init__.py
    │   │   └── views.py   # Views: cadastro_medico, home_med
    │   │
    │   ├── enfermeiro/    # Módulo específico para Enfermeiros
    │   │   ├── __init__.py
    │   │   └── views.py   # Views: cadastro_enfermeiro, home_enf
    │   │
    │   ├── administrador/ # Módulo específico para Administradores
    │   │   ├── __init__.py
    │   │   └── views.py   # Views: cadastro_admin, home_admin, alocar
    │   │
    │   ├── paciente/      # Módulo específico para Pacientes
    │   │   ├── __init__.py
    │   │   └── views.py   # Views: cadastro_paciente, home
    │   │
    │   ├── templates/     # Templates HTML
    │   │   └── usuarios/
    │   │       ├── base.html           # Template base (layout comum)
    │   │       ├── landing.html        # Página inicial (sem login)
    │   │       ├── login.html          # Formulário de login
    │   │       ├── cadastro.html       # Formulário principal de cadastro
    │   │       ├── cadastro_medico.html       # Cadastro específico: Médico
    │   │       ├── cadastro_enfermeiro.html  # Cadastro específico: Enfermeiro
    │   │       ├── cadastro_admin.html       # Cadastro específico: Administrador
    │   │       ├── cadastro_paciente.html    # Cadastro específico: Paciente
    │   │       ├── home.html          # Dashboard genérico pós-login
    │   │       ├── home_med.html      # Dashboard para Médicos
    │   │       ├── home_enf.html      # Dashboard para Enfermeiros
    │   │       ├── home_admin.html    # Dashboard para Administradores
    │   │       └── alocar.html        # Página de alocação (Admin)
    │   │
    │   ├── migrations/    # Migrações do banco de dados
    │   │   ├── __init__.py
    │   │   ├── 0001_initial.py        # Criação inicial de tabelas
    │   │   ├── 0002_remove_usuario_*.py
    │   │   ├── 0003_pessoa_medico_*.py
    │   │   ├── 0004_departamento_*.py
    │   │   └── __pycache__/
    │   │
    │   ├── __pycache__/   # Cache Python (ignorar)
    │   └── views.py.bak   # Backup de views (ignorar)
    │
    ├── projeto/           # Configurações globais do Django
    │   ├── __init__.py
    │   ├── settings.py    # Configurações: INSTALLED_APPS, DATABASES, TEMPLATES
    │   ├── urls.py        # URL routing de nível de projeto
    │   ├── wsgi.py        # Entry point para WSGI (produção)
    │   ├── asgi.py        # Entry point para ASGI (produção)
    │   ├── __pycache__/   # Cache Python (ignorar)
```

---

## 🗄️ Modelos de Dados

### Hierarquia de Modelos

```
Pessoa (Base)
  ├── Funcionario
  │   ├── Medico
  │   ├── Enfermeiro
  │   └── Administrador
  └── Paciente

Departamento
Consultorio
Sala_Cirurgia
Leito_Cirurgico
Leito_UTI
Consulta
Cirurgia
FuncionarioTrabalhaEm
```

### Detalhamento dos Modelos

#### **Pessoa** (`app/models.py`)

Tabela base com informações de todas as pessoas no hospital.

| Campo             | Tipo           | Descrição             |
| ----------------- | -------------- | --------------------- |
| `cpf`             | CharField(11)  | CPF (chave primária)  |
| `nome`            | CharField(100) | Nome completo         |
| `sexo`            | CharField(100) | Sexo (M/F)            |
| `telefone`        | CharField(20)  | Telefone para contato |
| `email`           | CharField(100) | Email                 |
| `data_nascimento` | DateField      | Data de nascimento    |

#### **Funcionario**

Estende `Pessoa` com informações laborais.

| Campo               | Tipo                  | Descrição                   |
| ------------------- | --------------------- | --------------------------- |
| `fcpf`              | OneToOneField(Pessoa) | Referência ao CPF da Pessoa |
| `salario`           | DecimalField          | Salário mensal              |
| `horas_trabalhadas` | DecimalField          | Horas trabalhadas           |

#### **Medico**

Profissional que atende pacientes e realiza cirurgias.

| Campo  | Tipo                       | Descrição                                            |
| ------ | -------------------------- | ---------------------------------------------------- |
| `crm`  | CharField(20)              | CRM (Conselho Regional de Medicina) - chave primária |
| `mcpf` | OneToOneField(Funcionario) | Referência ao Funcionario                            |

#### **Enfermeiro**

Profissional de enfermagem que auxilia médicos.

| Campo   | Tipo                       | Descrição                                                |
| ------- | -------------------------- | -------------------------------------------------------- |
| `coren` | CharField(20)              | COREN (Conselho Regional de Enfermagem) - chave primária |
| `ecpf`  | OneToOneField(Funcionario) | Referência ao Funcionario                                |

#### **Administrador**

Funcionário responsável pela gestão do hospital/departamento.

| Campo  | Tipo                       | Descrição                                  |
| ------ | -------------------------- | ------------------------------------------ |
| `acpf` | OneToOneField(Funcionario) | Referência ao Funcionario - chave primária |

#### **Paciente**

Pessoa que recebe atendimento no hospital.

| Campo  | Tipo                  | Descrição                            |
| ------ | --------------------- | ------------------------------------ |
| `pcpf` | OneToOneField(Pessoa) | Referência à Pessoa - chave primária |

#### **Departamento**

Divisão organizacional do hospital.

| Campo               | Tipo          | Descrição                                 |
| ------------------- | ------------- | ----------------------------------------- |
| `dnome`             | CharField(50) | Nome do departamento - chave primária     |
| `cpf_administrador` | CharField(11) | CPF do Administrador responsável (UNIQUE) |

#### **FuncionarioTrabalhaEm**

Relacionamento entre Funcionário e Departamento (controla alocações).

| Campo               | Tipo                       | Descrição                                  |
| ------------------- | -------------------------- | ------------------------------------------ |
| `cpf_funcionario`   | OneToOneField(Funcionario) | CPF do Funcionário - chave primária        |
| `nome_departamento` | ForeignKey(Departamento)   | Nome do departamento                       |
| `data_inicio`       | DateField                  | Data de início na alocação                 |
| `data_fim`          | DateField                  | Data de término da alocação (se aplicável) |

#### **Consultorio**

Espaço para consultas médicas.

| Campo          | Tipo             | Descrição                         |
| -------------- | ---------------- | --------------------------------- |
| `andar`        | Int              | Andar do consultório              |
| `numero`       | Int              | Número do consultório             |
| `departamento` | FK(Departamento) | Departamento responsável          |
| `fmedico`      | FK(Medico)       | Médico associado                  |
| `status`       | CharField(20)    | Status (disponível, ocupado, etc) |

#### **Sala_Cirurgia**

Sala destinada a procedimentos cirúrgicos.

| Campo          | Tipo             | Descrição                        |
| -------------- | ---------------- | -------------------------------- |
| `numero`       | Serial           | ID único - chave primária        |
| `departamento` | FK(Departamento) | Departamento responsável         |
| `fmedico`      | FK(Medico)       | Médico responsável               |
| `fenfermeiro`  | FK(Enfermeiro)   | Enfermeiro assistente            |
| `status`       | CharField(20)    | Status (disponível, em uso, etc) |

#### **Leito_Cirurgico** / **Leito_UTI**

Leitos para pacientes após cirurgia ou em UTI.

| Campo          | Tipo             | Descrição              |
| -------------- | ---------------- | ---------------------- |
| `numero`       | Serial           | ID único               |
| `departamento` | FK(Departamento) | Departamento           |
| `fenfermeiro`  | FK(Enfermeiro)   | Enfermeiro responsável |
| `fpaciente`    | FK(Paciente)     | Paciente internado     |
| `status`       | CharField(20)    | Status                 |

#### **Consulta**

Registro de consultas médicas.

| Campo             | Tipo         | Descrição                  |
| ----------------- | ------------ | -------------------------- |
| `nmr_consulta`    | Serial       | ID único                   |
| `horario`         | Time         | Horário da consulta        |
| `data`            | Date         | Data da consulta           |
| `fpaciente`       | FK(Paciente) | Paciente                   |
| `fmedico`         | FK(Medico)   | Médico                     |
| `andar`, `numero` | Int          | Localização do consultório |

#### **Cirurgia**

Registro de procedimentos cirúrgicos.

| Campo          | Tipo              | Descrição             |
| -------------- | ----------------- | --------------------- |
| `nmr_cirurgia` | Serial            | ID único              |
| `horario`      | Time              | Horário da cirurgia   |
| `data`         | Date              | Data da cirurgia      |
| `fpaciente`    | FK(Paciente)      | Paciente              |
| `fmedico`      | FK(Medico)        | Cirurgião             |
| `fsala`        | FK(Sala_Cirurgia) | Sala utilizada        |
| `fenfermeiro`  | FK(Enfermeiro)    | Enfermeiro assistente |

---

## ⚙️ Funcionalidades

### Autenticação e Registro

- ✅ **Landing Page** (`/`) — Página inicial sem autenticação
- ✅ **Cadastro Geral** (`/cadastro/`) — Registro básico de pessoa + seleção de papel
- ✅ **Cadastro Específico por Papel**:
  - `/cadastro/medico/` — Dados de médico (CRM)
  - `/cadastro/enfermeiro/` — Dados de enfermeiro (COREN)
  - `/cadastro/admin/` — Dados de administrador
  - `/cadastro/paciente/` — Dados de paciente
- ✅ **Login** (`/login/`) — Autenticação de usuário

### Dashboards Específicos

- 📊 **Home Genérico** (`/home/`) — Para usuários sem papel definido
- 👨‍⚕️ **Home Médico** (`/home_med/`) — Dashboard para médicos
- 👩‍⚕️ **Home Enfermeiro** (`/home_enf/`) — Dashboard para enfermeiros
- 👔 **Home Administrador** (`/home_admin/`) — Dashboard para administradores
- 🏥 **Home Paciente** (via `home_paciente()`) — Dashboard para pacientes

### Gerenciamento de Recursos

- 🔄 **Alocação de Funcionários** (`/alocar/`) — Designar funcionários a departamentos

---

## 🔄 Fluxos de Trabalho

### 1️⃣ Fluxo de Registro (Sign Up)

```
1. Usuário acessa /cadastro/
   ↓
2. Preenche: nome, CPF, sexo, telefone, email, data_nascimento, senha, papel
   ↓
3. Sistema verifica:
   - CPF já existe em Pessoa? (rejeita se sim)
   - Username já existe em User? (rejeita se sim)
   ↓
4. Sistema cria:
   - Pessoa (com CPF)
   - User do Django (com username=nome)
   - Armazena CPF em session
   ↓
5. Redireciona para cadastro específico:
   - Médico → /cadastro/medico/?cpf={cpf}
   - Enfermeiro → /cadastro/enfermeiro/?cpf={cpf}
   - Admin → /cadastro/admin/?cpf={cpf}
   - Paciente → /cadastro/paciente/?cpf={cpf}
   ↓
6. Completa perfil (CRM, COREN, etc.) no cadastro específico
   ↓
7. Usuário criado e pronto para login
```

### 2️⃣ Fluxo de Login (Sign In)

```
1. Usuário acessa /login/
   ↓
2. Insere: nome (username), senha
   ↓
3. Sistema autentica com Django:
   - Busca User por username
   - Verifica senha (hash bcrypt/pbkdf2)
   ↓
4. Se válido:
   - Faz login_django() (cria session)
   - Busca Pessoa associada
   - Determina papéis (Médico? Enfermeiro? Paciente? Admin?)
   ↓
5. Redireciona para dashboard apropriado:
   - Médico → /home_med/
   - Enfermeiro → /home_enf/
   - Admin → /home_admin/
   - Paciente → /home/ (ou /home_paciente/)
   - Genérico → /home/
```

### 3️⃣ Fluxo de Alocação de Funcionário (Admin)

```
1. Administrador acessa /alocar/
   ↓
2. Seleciona: Funcionário, Departamento, Data de Início
   ↓
3. Sistema cria/atualiza FuncionarioTrabalhaEm
   ↓
4. Funcionário vinculado ao departamento
```

---

## 🔐 Modelos de Papel (Roles)

### **Médico** (`app/medico/`)

- **Identificação**: CRM (Conselho Regional de Medicina)
- **Tabelas**: `medico`, `funcionario`, `pessoa`
- **Views**: `cadastro_medico()`, `home_med()`
- **Responsabilidades**:
  - Atender pacientes em consultórios
  - Realizar procedimentos cirúrgicos
  - Gerar prescrições e diagnósticos

### **Enfermeiro** (`app/enfermeiro/`)

- **Identificação**: COREN (Conselho Regional de Enfermagem)
- **Tabelas**: `enfermeiro`, `funcionario`, `pessoa`
- **Views**: `cadastro_enfermeiro()`, `home_enf()`
- **Responsabilidades**:
  - Auxiliar médicos em cirurgias
  - Gerenciar leitos (cirúrgicos e UTI)
  - Monitorar pacientes

### **Administrador** (`app/administrador/`)

- **Tabelas**: `administrador`, `funcionario`, `pessoa`
- **Views**: `cadastro_admin()`, `home_admin()`, `alocar()`
- **Responsabilidades**:
  - Gerenciar departamentos
  - Alocar funcionários a departamentos
  - Acessar relatórios gerenciais

### **Paciente** (`app/paciente/`)

- **Tabelas**: `paciente`, `pessoa`
- **Views**: `cadastro_paciente()`, `home()` (ou `home_paciente()`)
- **Responsabilidades**:
  - Visualizar agendamentos
  - Consultar histórico médico
  - Gerenciar internações (em desenvolvimento)

---

## 📡 Endpoints da API

### Autenticação

| Método   | Endpoint     | Descrição                    |
| -------- | ------------ | ---------------------------- |
| GET/POST | `/`          | Landing page                 |
| GET/POST | `/cadastro/` | Formulário de cadastro geral |
| GET/POST | `/login/`    | Login                        |

### Cadastro Específico

| Método   | Endpoint                | Descrição                 |
| -------- | ----------------------- | ------------------------- |
| GET/POST | `/cadastro/medico/`     | Cadastro de médico        |
| GET/POST | `/cadastro/enfermeiro/` | Cadastro de enfermeiro    |
| GET/POST | `/cadastro/admin/`      | Cadastro de administrador |
| GET/POST | `/cadastro/paciente/`   | Cadastro de paciente      |

### Dashboards (Requerem Login)

| Método | Endpoint       | Descrição            | Papel            |
| ------ | -------------- | -------------------- | ---------------- |
| GET    | `/home/`       | Dashboard genérico   | Qualquer usuário |
| GET    | `/home_med/`   | Dashboard médico     | Médico           |
| GET    | `/home_enf/`   | Dashboard enfermeiro | Enfermeiro       |
| GET    | `/home_admin/` | Dashboard admin      | Administrador    |

### Gerenciamento

| Método   | Endpoint   | Descrição                         | Papel         |
| -------- | ---------- | --------------------------------- | ------------- |
| GET/POST | `/alocar/` | Alocar funcionário a departamento | Administrador |

---

## 📦 Instalação

### Pré-requisitos

- **Python** 3.11+ (verificar: `python --version`)
- **pip** (verificar: `pip --version`)
- **Git** (verificar: `git --version`)

### Passo 1: Clonar o Repositório

```powershell
git clone https://github.com/BernardoFerrazG/Hospital_bd.git
cd Hospital_bd
```

### Passo 2: Criar e Ativar Ambiente Virtual

```powershell
# Criar venv
python -m venv venv

# Ativar (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Se receber erro de execução, execute:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Passo 3: Instalar Dependências

```powershell
pip install django==5.2.8
# Se existir requirements.txt:
# pip install -r requirements.txt
```

### Passo 4: Aplicar Migrações

```powershell
cd projeto
python manage.py migrate
```

### Passo 5: (Opcional) Criar Superusuário

```powershell
python manage.py createsuperuser
# Preencher: username, email, senha
```

### Passo 6: Executar o Servidor

```powershell
python manage.py runserver
```

Acessar em: **http://127.0.0.1:8000/**

---

## 🚀 Como Usar

### Primeira Execução

1. **Acesse a landing page**: `http://localhost:8000/`
2. **Clique em "Cadastro"**: `/cadastro/`
3. **Preencha o formulário** com:
   - Nome
   - CPF (11 dígitos)
   - Sexo
   - Telefone
   - Email
   - Data de nascimento
   - Senha
   - Papel (Médico, Enfermeiro, Admin ou Paciente)
4. **Complete o cadastro específico** (CRM se médico, COREN se enfermeiro, etc.)
5. **Faça login** em `/login/` com nome + senha
6. **Acesse seu dashboard** (página inicial pós-login)

### Teste de Admin

1. No terminal, crie superusuário:

```powershell
python manage.py createsuperuser
```

2. Acesse: `http://localhost:8000/admin/`

3. Faça login com as credenciais do superusuário

4. Visualize/edite modelos (Pessoa, Funcionario, Medico, etc.)

---

## 🗄️ Schema do Banco de Dados

O schema completo está em `schema.sql`. Principais tabelas:

```sql
-- Entidades principais
CREATE TABLE PESSOA(...)        -- Base de dados
CREATE TABLE FUNCIONARIO(...)   -- Herança de Pessoa
CREATE TABLE MEDICO(...)        -- Herança de Funcionario
CREATE TABLE ENFERMEIRO(...)    -- Herança de Funcionario
CREATE TABLE ADMINISTRADOR(...) -- Herança de Funcionario
CREATE TABLE PACIENTE(...)      -- Herança de Pessoa

-- Organização
CREATE TABLE DEPARTAMENTO(...)
CREATE TABLE FUNCIONARIO_TRABALHA_EM(...)

-- Recursos
CREATE TABLE CONSULTORIO(...)
CREATE TABLE SALA_CIRURGIA(...)
CREATE TABLE LEITO_CIRURGICO(...)
CREATE TABLE LEITO_UTI(...)

-- Eventos
CREATE TABLE CONSULTA(...)
CREATE TABLE CIRURGIA(...)
```

---

## 📂 Estrutura de Pastas Importantes

### `app/`

**App principal do Django** — contém toda a lógica de negócio.

- **`models.py`**: Definição de todas as entidades (Pessoa, Funcionario, etc.)

  - Usa `managed=False` porque o schema foi criado manualmente
  - Cada modelo mapeia uma tabela SQL

- **`views.py`**: Lógica de presentação (formulários, autenticação, redirecionamento)

  - `landing()` — página inicial
  - `cadastro()` — cria Pessoa + User
  - `login()` — autentica e redireciona para dashboard

- **`urls.py`**: Mapeia URLs para views

  - Exemplo: `/cadastro/` → `views.cadastro()`

- **`admin.py`**: Registro de modelos no painel Django

  - Permite editar dados via `/admin/`

- **`templates/usuarios/`**: Templates HTML
  - Herança via `base.html`
  - Formulários de cadastro/login
  - Dashboards por papel

### `app/medico/`, `app/enfermeiro/`, `app/administrador/`, `app/paciente/`

**Módulos específicos por papel** — isolam lógica relacionada.

Cada pasta contém:

- **`views.py`**: Funções de cadastro e dashboard
- **`__init__.py`**: Inicialização do módulo

**Exemplo**: `app/medico/views.py` contém:

```python
def cadastro_medico(request):
    # Cria Funcionario + Medico

def home_med(request):
    # Dashboard específico de médico
```

### `projeto/`

**Configurações globais do Django**.

- **`settings.py`**:

  - `INSTALLED_APPS = ['app', ...]` — registro de apps
  - `DATABASES` — configuração do SQLite
  - `TEMPLATES` — caminho para templates
  - `DEBUG = True` — modo desenvolvimento

- **`urls.py`**:

  - `urlpatterns = [include('app.urls'), ...]` — inclui rotas da app

- **`wsgi.py` / `asgi.py`**: Entry points para produção (Gunicorn, Uvicorn, etc.)

---

## 🔧 Comandos Django Úteis

```powershell
# Aplicar migrações
python manage.py migrate

# Criar nova migração (se modificar models.py)
python manage.py makemigrations

# Executar servidor
python manage.py runserver

# Criar superusuário (admin)
python manage.py createsuperuser

# Acessar shell Python com contexto Django
python manage.py shell

# Verificar problemas de projeto
python manage.py check

# Limpar cache
python manage.py clear_cache
```

---

## ⚠️ Notas Importantes

1. **Banco de Dados Manual**: O schema foi criado manualmente em SQL, então `managed=False` em todos os modelos.

2. **Autenticação Dupla**: O sistema usa tanto `User` do Django quanto modelos customizados (`Pessoa`, `Funcionario`, etc.) para maior controle.

3. **CPF na Sessão**: Durante o cadastro, o CPF é armazenado em `request.session` para facilitar o fluxo entre formulários.

4. **Desenvolvimento**: Atualmente usa SQLite. Para produção, considere PostgreSQL ou MySQL.

5. **CORS**: Se integrar com frontend separado, adicionar `django-cors-headers` em `settings.py`.

---

## 🐛 Troubleshooting

### Erro: "No module named 'app'"

```powershell
# Garantir que está no diretório correto
cd projeto
python manage.py runserver
```

### Erro: "relation 'pessoa' does not exist"

```powershell
# Aplicar schema SQL manualmente
python manage.py dbshell
# Dentro do shell: \i schema.sql
```

### Erro: "CSRF token missing"

Garantir que:

- Template tem `{% csrf_token %}`
- `csrf` middleware está em `MIDDLEWARE` em `settings.py`

### Erro: "You have unapplied migrations"

```powershell
python manage.py migrate
```

---

## 📝 Próximos Passos / TODO

- [ ] Integrar agendamento de consultas
- [ ] Criar relatórios de atendimentos
- [ ] Implementar notificações via email
- [ ] Adicionar testes unitários em `app/tests.py`
- [ ] Autenticação 2FA (dois fatores)
- [ ] API REST (Django REST Framework)
- [ ] Frontend separado (React/Vue)
- [ ] Deploy em produção (Heroku/Railway)

---

## 👨‍💻 Contribuição

1. Fazer fork do repositório
2. Criar branch para feature: `git checkout -b feature/NovaFuncionalidade`
3. Commit: `git commit -m "Adiciona nova funcionalidade"`
4. Push: `git push origin feature/NovaFuncionalidade`
5. Abrir Pull Request

---

## 📄 Licença

Este projeto é de código aberto sob a licença **MIT**.

---

## 📧 Contato / Suporte

- **Autor**: Bernardo Ferraz
- **GitHub**: [@BernardoFerrazG](https://github.com/BernardoFerrazG)
- **Issues**: [GitHub Issues](https://github.com/BernardoFerrazG/Hospital_bd/issues)

---

**Última atualização**: 21 de Novembro de 2025
Registro de consultas médicas.
| Campo | Tipo | Descrição |
| ----------------- | ------------ | -------------------------- |
| `nmr_consulta` | Serial | ID único |
| `horario` | Time | Horário da consulta |
| `data` | Date | Data da consulta |
| `fpaciente` | FK(Paciente) | Paciente |
| `fmedico` | FK(Medico) | Médico |
| `andar`, `numero` | Int | Localização do consultório |

#### **Cirurgia**

Registro de procedimentos cirúrgicos.

| Campo          | Tipo              | Descrição             |
| -------------- | ----------------- | --------------------- |
| `nmr_cirurgia` | Serial            | ID único              |
| `horario`      | Time              | Horário da cirurgia   |
| `data`         | Date              | Data da cirurgia      |
| `fpaciente`    | FK(Paciente)      | Paciente              |
| `fmedico`      | FK(Medico)        | Cirurgião             |
| `fsala`        | FK(Sala_Cirurgia) | Sala utilizada        |
| `fenfermeiro`  | FK(Enfermeiro)    | Enfermeiro assistente |

---

## ⚙️ Funcionalidades

### Autenticação e Registro

- ✅ **Landing Page** (`/`) — Página inicial sem autenticação
- ✅ **Cadastro Geral** (`/cadastro/`) — Registro básico de pessoa + seleção de papel
- ✅ **Cadastro Específico por Papel**:
  - `/cadastro/medico/` — Dados de médico (CRM)
  - `/cadastro/enfermeiro/` — Dados de enfermeiro (COREN)
  - `/cadastro/admin/` — Dados de administrador
  - `/cadastro/paciente/` — Dados de paciente
- ✅ **Login** (`/login/`) — Autenticação de usuário

### Dashboards Específicos

- 📊 **Home Genérico** (`/home/`) — Para usuários sem papel definido
- 👨‍⚕️ **Home Médico** (`/home_med/`) — Dashboard para médicos
- 👩‍⚕️ **Home Enfermeiro** (`/home_enf/`) — Dashboard para enfermeiros
- 👔 **Home Administrador** (`/home_admin/`) — Dashboard para administradores
- 🏥 **Home Paciente** (via `home_paciente()`) — Dashboard para pacientes

### Gerenciamento de Recursos

- 🔄 **Alocação de Funcionários** (`/alocar/`) — Designar funcionários a departamentos

---

## 🔄 Fluxos de Trabalho

### 1️⃣ Fluxo de Registro (Sign Up)

```
1. Usuário acessa /cadastro/
   ↓
2. Preenche: nome, CPF, sexo, telefone, email, data_nascimento, senha, papel
   ↓
3. Sistema verifica:
   - CPF já existe em Pessoa? (rejeita se sim)
   - Username já existe em User? (rejeita se sim)
   ↓
4. Sistema cria:
   - Pessoa (com CPF)
   - User do Django (com username=nome)
   - Armazena CPF em session
   ↓
5. Redireciona para cadastro específico:
   - Médico → /cadastro/medico/?cpf={cpf}
   - Enfermeiro → /cadastro/enfermeiro/?cpf={cpf}
   - Admin → /cadastro/admin/?cpf={cpf}
   - Paciente → /cadastro/paciente/?cpf={cpf}
   ↓
6. Completa perfil (CRM, COREN, etc.) no cadastro específico
   ↓
7. Usuário criado e pronto para login
```

### 2️⃣ Fluxo de Login (Sign In)

```
1. Usuário acessa /login/
   ↓
2. Insere: nome (username), senha
   ↓
3. Sistema autentica com Django:
   - Busca User por username
   - Verifica senha (hash bcrypt/pbkdf2)
   ↓
4. Se válido:
   - Faz login_django() (cria session)
   - Busca Pessoa associada
   - Determina papéis (Médico? Enfermeiro? Paciente? Admin?)
   ↓
5. Redireciona para dashboard apropriado:
   - Médico → /home_med/
   - Enfermeiro → /home_enf/
   - Admin → /home_admin/
   - Paciente → /home/ (ou /home_paciente/)
   - Genérico → /home/
```

### 3️⃣ Fluxo de Alocação de Funcionário (Admin)

```
1. Administrador acessa /alocar/
   ↓
2. Seleciona: Funcionário, Departamento, Data de Início
   ↓
3. Sistema cria/atualiza FuncionarioTrabalhaEm
   ↓
4. Funcionário vinculado ao departamento
```

---

## 🔐 Modelos de Papel (Roles)

### **Médico** (`app/medico/`)

- **Identificação**: CRM (Conselho Regional de Medicina)
- **Tabelas**: `medico`, `funcionario`, `pessoa`
- **Views**: `cadastro_medico()`, `home_med()`
- **Responsabilidades**:
  - Atender pacientes em consultórios
  - Realizar procedimentos cirúrgicos
  - Gerar prescrições e diagnósticos

### **Enfermeiro** (`app/enfermeiro/`)

- **Identificação**: COREN (Conselho Regional de Enfermagem)
- **Tabelas**: `enfermeiro`, `funcionario`, `pessoa`
- **Views**: `cadastro_enfermeiro()`, `home_enf()`
- **Responsabilidades**:
  - Auxiliar médicos em cirurgias
  - Gerenciar leitos (cirúrgicos e UTI)
  - Monitorar pacientes

### **Administrador** (`app/administrador/`)

- **Tabelas**: `administrador`, `funcionario`, `pessoa`
- **Views**: `cadastro_admin()`, `home_admin()`, `alocar()`
- **Responsabilidades**:
  - Gerenciar departamentos
  - Alocar funcionários a departamentos
  - Acessar relatórios gerenciais

### **Paciente** (`app/paciente/`)

- **Tabelas**: `paciente`, `pessoa`
- **Views**: `cadastro_paciente()`, `home()` (ou `home_paciente()`)
- **Responsabilidades**:
  - Visualizar agendamentos
  - Consultar histórico médico
  - Gerenciar internações (em desenvolvimento)

---

## 📡 Endpoints da API

### Autenticação

| Método   | Endpoint     | Descrição                    |
| -------- | ------------ | ---------------------------- |
| GET/POST | `/`          | Landing page                 |
| GET/POST | `/cadastro/` | Formulário de cadastro geral |
| GET/POST | `/login/`    | Login                        |

### Cadastro Específico

| Método   | Endpoint                | Descrição                 |
| -------- | ----------------------- | ------------------------- |
| GET/POST | `/cadastro/medico/`     | Cadastro de médico        |
| GET/POST | `/cadastro/enfermeiro/` | Cadastro de enfermeiro    |
| GET/POST | `/cadastro/admin/`      | Cadastro de administrador |
| GET/POST | `/cadastro/paciente/`   | Cadastro de paciente      |

### Dashboards (Requerem Login)

| Método | Endpoint       | Descrição            | Papel            |
| ------ | -------------- | -------------------- | ---------------- |
| GET    | `/home/`       | Dashboard genérico   | Qualquer usuário |
| GET    | `/home_med/`   | Dashboard médico     | Médico           |
| GET    | `/home_enf/`   | Dashboard enfermeiro | Enfermeiro       |
| GET    | `/home_admin/` | Dashboard admin      | Administrador    |

### Gerenciamento

| Método   | Endpoint   | Descrição                         | Papel         |
| -------- | ---------- | --------------------------------- | ------------- |
| GET/POST | `/alocar/` | Alocar funcionário a departamento | Administrador |

---

## 📂 Estrutura de Pastas Importantes

### `app/`

**App principal do Django** — contém toda a lógica de negócio.

- **`models.py`**: Definição de todas as entidades (Pessoa, Funcionario, etc.)

  - Usa `managed=False` porque o schema foi criado manualmente
  - Cada modelo mapeia uma tabela SQL

- **`views.py`**: Lógica de presentação (formulários, autenticação, redirecionamento)

  - `landing()` — página inicial
  - `cadastro()` — cria Pessoa + User
  - `login()` — autentica e redireciona para dashboard

- **`urls.py`**: Mapeia URLs para views

  - Exemplo: `/cadastro/` → `views.cadastro()`

- **`admin.py`**: Registro de modelos no painel Django

  - Permite editar dados via `/admin/`

- **`templates/usuarios/`**: Templates HTML
  - Herança via `base.html`
  - Formulários de cadastro/login
  - Dashboards por papel

### `app/medico/`, `app/enfermeiro/`, `app/administrador/`, `app/paciente/`

**Módulos específicos por papel** — isolam lógica relacionada.

Cada pasta contém:

- **`views.py`**: Funções de cadastro e dashboard
- **`__init__.py`**: Inicialização do módulo

**Exemplo**: `app/medico/views.py` contém:

```python
def cadastro_medico(request):
    # Cria Funcionario + Medico

def home_med(request):
    # Dashboard específico de médico
```

### `projeto/`

**Configurações globais do Django**.

- **`settings.py`**:

  - `INSTALLED_APPS = ['app', ...]` — registro de apps
  - `DATABASES` — configuração do SQLite
  - `TEMPLATES` — caminho para templates
  - `DEBUG = True` — modo desenvolvimento

- **`urls.py`**:

  - `urlpatterns = [include('app.urls'), ...]` — inclui rotas da app

- **`wsgi.py` / `asgi.py`**: Entry points para produção (Gunicorn, Uvicorn, etc.)

---

## 🔧 Comandos Django Úteis

```powershell
# Aplicar migrações
python manage.py migrate

# Criar nova migração (se modificar models.py)
python manage.py makemigrations

# Executar servidor
python manage.py runserver

# Criar superusuário (admin)
python manage.py createsuperuser

# Acessar shell Python com contexto Django
python manage.py shell

# Verificar problemas de projeto
python manage.py check

# Limpar cache
python manage.py clear_cache
```

---

## ⚠️ Notas Importantes

1. **Banco de Dados Manual**: O schema foi criado manualmente em SQL, então `managed=False` em todos os modelos.

2. **Autenticação Dupla**: O sistema usa tanto `User` do Django quanto modelos customizados (`Pessoa`, `Funcionario`, etc.) para maior controle.

3. **CPF na Sessão**: Durante o cadastro, o CPF é armazenado em `request.session` para facilitar o fluxo entre formulários.

4. **Desenvolvimento**: Atualmente usa SQLite. Para produção, considere PostgreSQL ou MySQL.

5. **CORS**: Se integrar com frontend separado, adicionar `django-cors-headers` em `settings.py`.

---

## 🐛 Troubleshooting

### Erro: "No module named 'app'"

```powershell
# Garantir que está no diretório correto
cd projeto
python manage.py runserver
```

### Erro: "relation 'pessoa' does not exist"

```powershell
# Aplicar schema SQL manualmente
python manage.py dbshell
# Dentro do shell: \i schema.sql
```

### Erro: "CSRF token missing"

Garantir que:

- Template tem `{% csrf_token %}`
- `csrf` middleware está em `MIDDLEWARE` em `settings.py`

### Erro: "You have unapplied migrations"

```powershell
python manage.py migrate
```
