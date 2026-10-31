# Hospital Management System

[![CI](https://github.com/BernardoFerrazG/Hospital_bd/actions/workflows/ci.yml/badge.svg)](https://github.com/BernardoFerrazG/Hospital_bd/actions/workflows/ci.yml)

A web application for running a hospital's day-to-day resources. It handles staff and patient registration, operating rooms, surgical and ICU beds, consultations and department assignments, with a separate workspace for each role. It was built with **Django** on a **PostgreSQL** schema designed from scratch for a Databases course at UFSJ. The UI is in Portuguese; this README is in English.

## Features

| Role | What they can do |
| --- | --- |
| **Administrator** | Register doctors, nurses and other administrators; assign staff to departments |
| **Doctor** | Book and release operating rooms; allocate and free surgical and ICU beds for patients; view their consultations |
| **Nurse** | View their assignments: rooms, beds and the administrator responsible |
| **Patient** | Self-register and access the patient area |

Access is **role-based**. Every page checks the signed-in user's role and returns `403 Forbidden` for any other role. Clinical staff can only be registered by an administrator. The very first administrator can register themselves, to bootstrap a fresh installation.

## Architecture

```
schema.sql                  # PostgreSQL schema (source of truth for the tables)
projeto/
├── projeto/settings.py     # Configuration via environment variables
└── app/
    ├── models.py           # Django models mapped onto the SQL schema (managed = False)
    ├── permissoes.py       # Role resolution and @requer_papel(...) access control
    ├── views.py            # Landing page, sign-up, sign-in
    ├── administrador/      # Admin views
    ├── medico/             # Doctor views: rooms, beds, consultations
    ├── enfermeiro/         # Nurse views
    ├── paciente/           # Patient views
    ├── templates/
    ├── tests.py            # Access-control and sign-up tests
    └── test_runner.py      # Creates the unmanaged tables for the test database
```

### Data model

The schema is normalised around **generalisation/specialisation**. `PESSOA` holds the data shared by everyone. `FUNCIONARIO` (staff) and `PACIENTE` (patient) specialise it, and `FUNCIONARIO` is further specialised into `MEDICO`, `ENFERMEIRO` and `ADMINISTRADOR`. Resources include `SALA_CIRURGIA` (operating room), `LEITO_CIRURGICO` (surgical bed), `LEITO_UTI` (ICU bed) and `CONSULTORIO` (consulting room). Events include `CONSULTA` (consultation) and `CIRURGIA` (surgery). Many-to-many assignment tables link staff to departments, rooms and beds.

The tables are created by [`schema.sql`](schema.sql), and Django maps onto them with `managed = False`. That keeps the relational design, which is the focus of the course, independent of the ORM.

## Getting started

Requires Python 3.11+ and PostgreSQL.

```bash
git clone https://github.com/BernardoFerrazG/Hospital_bd.git
cd Hospital_bd
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

createdb hospital_bd
psql -d hospital_bd -f schema.sql

cp .env.example .env          # set POSTGRES_PASSWORD and DJANGO_SECRET_KEY
set -a && source .env && set +a

cd projeto
python manage.py migrate      # Django's own tables (auth, sessions)
python manage.py runserver
```

Open http://localhost:8000, register the first administrator, and use that account to register doctors and nurses.

## Tests

```bash
cd projeto
python manage.py test
```

The tests run on an in-memory SQLite database. A custom test runner creates the tables of the unmanaged models, so PostgreSQL isn't needed. They cover:

- role detection for every user type;
- anonymous users being redirected to the sign-in page;
- a patient receiving `403` on administrator, doctor and nurse pages;
- the public being unable to register doctors or administrators once an administrator exists;
- the first-administrator bootstrap;
- an administrator registering a doctor;
- invalid roles being rejected without leaving partial records.

CI runs `manage.py check` and the tests on every push.

## Security fixes in this revision

- **Privilege escalation.** Anyone could sign up as an administrator or doctor, because the role was a free choice on the public sign-up form. Staff registration now requires an administrator.
- **Missing authorization.** Pages only required *a* login, so a patient could open the administrator and doctor screens. Every page now checks the user's role.
- **Broken login redirect.** Protected pages sent anonymous users to `/auth/login/`, which doesn't exist. They now go to `/login/`.
- **Secrets in the repository.** The Django `SECRET_KEY` and the database password were hard-coded in `settings.py`. They now come from environment variables (see [`.env.example`](.env.example)).
- **Committed database.** A `db.sqlite3` file with test records, plus a `views.py.bak` backup, were removed from version control.

## Team

Built at UFSJ by:

- [Bernardo Ferraz](https://github.com/BernardoFerrazG)
- Carlos Gabriel Teixeira
- [João Pedro Tozetto da Cunha](https://github.com/joaopedrotozettodacunha)
