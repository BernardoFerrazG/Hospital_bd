# Hospital Management System

Este é um sistema de gerenciamento hospitalar desenvolvido com Django, projetado para facilitar o gerenciamento de usuários e recursos hospitalares.

## Estrutura do Projeto

```
projeto/
├── manage.py            # Script principal do Django para gerenciamento do projeto
├── db.sqlite3          # Banco de dados SQLite
├── app/                # Aplicação principal
│   ├── admin.py       # Configurações do painel administrativo
│   ├── models.py      # Modelos de dados/tabelas do banco
│   ├── views.py       # Lógica de visualização/controllers
│   ├── urls.py        # Configuração de rotas da aplicação
│   └── templates/     # Templates HTML
└── projeto/           # Configurações do projeto
    ├── settings.py    # Configurações gerais do Django
    ├── urls.py        # Configuração de rotas principais
    └── wsgi.py        # Configuração para deploy
```

## Principais Componentes

### Diretório `app/`
- **models.py**: Define a estrutura do banco de dados através de modelos Django
- **views.py**: Contém a lógica de negócio e processamento das requisições
- **urls.py**: Mapeia as URLs para as respectivas views
- **admin.py**: Configuração da interface administrativa
- **templates/**: Contém os arquivos HTML para renderização das páginas
  - **usuarios/**: Templates específicos para autenticação e gerenciamento de usuários

### Diretório `projeto/`
- **settings.py**: Configurações principais do projeto (banco de dados, apps instalados, etc.)
- **urls.py**: Configuração central de URLs do projeto
- **wsgi.py**: Ponto de entrada para servidores web

## Como Executar o Projeto

1. Certifique-se de ter Python instalado em seu sistema
2. Instale o Django:
   ```
   pip install django
   ```
3. Execute as migrações do banco de dados:
   ```
   python manage.py migrate
   ```
4. Inicie o servidor de desenvolvimento:
   ```
   python manage.py runserver
   ```
5. Acesse http://localhost:8000 no seu navegador

## Funcionalidades

- Sistema de autenticação de usuários (login/cadastro)
- Interface administrativa Django
- Gerenciamento de dados hospitalares
- Templates responsivos

## Tecnologias Utilizadas

- Django
- SQLite
- HTML/CSS
- Python