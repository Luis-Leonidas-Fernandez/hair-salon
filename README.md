<p align="center">
  <img src="asset/image.png" alt="FireOps Intelligence banner" width="100%">
</p>


**Peluquería Sergio** is a modular booking platform for a hair salon. It is designed to let clients sign in with Google, browse available services, select one of the salon's two professionals, and book an appointment without double-booking a time slot.

The project is being built as a focused MVP with a clear separation between business rules, application modules, infrastructure, and project documentation.

---

## MVP goals

The first version focuses on:

- Google OAuth authentication for clients;
- internal access for the administrator and two hairdressers;
- service catalog management;
- professional availability management;
- appointment creation, consultation, confirmation, cancellation, and attendance tracking;
- protection against overlapping appointments for the same professional;
- appointment history and auditability;
- optional Google Calendar synchronization as part of the validated MVP direction.

Payments are **not included** in the current scope. WhatsApp integration remains pending a separate decision.

---

## Main users

| User | Main responsibilities |
|---|---|
| Client | Sign in with Google, manage basic information, view services, choose a professional, and book appointments. |
| Hairdresser | View assigned availability and appointments, and update appointment status according to authorization rules. |
| Administrator | Manage services, professionals, schedules, exceptions, users, and operational configuration. |

The system supports two hairdressers and one administrator as internal users.

---

## Booking flow

```text
Client signs in with Google
  ↓
Selects a service
  ↓
Selects a hairdresser
  ↓
Views available time slots
  ↓
Confirms the appointment
  ↓
Receives the configured notification or calendar event
```

Core booking rules include:

- a service has a configured duration and base price;
- the client explicitly chooses the hairdresser;
- appointments use 30-minute scheduling blocks;
- the standard appointment duration is 60 minutes unless the configured service states otherwise;
- the same hairdresser cannot have overlapping appointments;
- cancellation and attendance changes preserve the appointment history;
- notifications are derived from appointments and are not the source of truth.

---

## Architecture

The project follows a modular monolith approach with vertical business modules and explicit separation of concerns.

```text
peluqueria/
├── app/
│   ├── config/
│   ├── infrastructure/
│   │   └── database/
│   ├── modules/
│   │   ├── audit/
│   │   ├── files/
│   │   ├── identity/
│   │   └── services/
│   │       ├── create_booking/
│   │       └── get_service/
│   ├── shared/
│   │   └── errors/
│   └── main.py
├── asset/
│   └── profile.png
├── docs/
├── migrations/
├── scripts/
├── tests/
├── .env.example
├── alembic.ini
├── Makefile
├── pyproject.toml
├── README.md
└── requirements.txt
```

### Responsibility boundaries

| Area | Responsibility |
|---|---|
| `app/config/` | Environment-backed application settings. |
| `app/infrastructure/` | Database sessions, metadata, persistence, and external integrations. |
| `app/modules/` | Business capabilities organized by vertical slice. |
| `app/shared/` | Reusable cross-cutting concerns, including application errors. |
| `docs/` | Requirements, validations, models, rules, ADRs, traceability, and change requests. |
| `migrations/` | Versioned PostgreSQL schema changes. |
| `tests/` | Unit, integration, API, and architecture tests. |

---

## Technology stack

| Category | Technology |
|---|---|
| Language | Python 3.14 |
| API framework | FastAPI |
| ASGI server | Uvicorn |
| Validation | Pydantic and Pydantic Settings |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2 |
| Migrations | Alembic |
| PostgreSQL driver | asyncpg |
| Authentication | Google OAuth and JWT-based application security |
| Testing | pytest, pytest-asyncio, HTTPX |
| Linting and formatting | Ruff |
| Static typing | mypy |
| Planned frontend | React + Vite + TypeScript |

---

## Documentation map

The documentation is organized by project phase and change impact:

```text
docs/
├── change-requests/       # New client requests and impact analysis
└── phase_01/
    ├── adr/               # Architecture Decision Records
    ├── business-rules/    # Validated business rules
    ├── data-modeling/     # Conceptual, logical, physical, and ORM mapping models
    ├── requirements/      # Functional and non-functional requirements
    ├── scope/             # MVP boundary and exclusions
    ├── traceability/      # Requirement-to-design coverage
    ├── use-cases/         # Main system interactions
    └── validations/       # Business validation meetings and results
```

When a new feature is requested, register it first under `docs/change-requests/`. Only the documents affected by the change should receive a new version.

---

## Requirements

Install the following tools locally:

- Python 3.14;
- PostgreSQL;
- Git;
- Make.

Verify the installed versions:

```bash
python --version
psql --version
git --version
make --version
```

---

## Local setup

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Set the local database and application values in `.env`. Never commit secrets or local credentials.

### 4. Create the PostgreSQL database

Create a local database for the application, then configure its connection string in `.env`.

### 5. Run migrations

```bash
alembic upgrade head
```

### 6. Start the unified application (Frontend + Backend)

To build the Astro frontend and start the unified server on port 8000:

```bash
make run
```

The unified application is available at:

```text
http://127.0.0.1:8000/           # Astro Landing Page
http://127.0.0.1:8000/registro/  # Client registration with Google OAuth
http://127.0.0.1:8000/reservas/  # Service bookings
http://127.0.0.1:8000/health     # Health check
http://127.0.0.1:8000/docs       # Interactive API documentation (Swagger)
```

---

## Development commands

```bash
make run       # Start the development server
make test      # Run the test suite
make lint      # Check code quality
make format    # Format the codebase
```

---

## Error handling

The API uses centralized exception handling and a custom application error hierarchy:

```text
Exception
└── ApplicationError
    ├── BusinessRuleError
    ├── ConflictError
    └── NotFoundError
```

This keeps business behavior independent from framework-specific response construction.

---

## Testing strategy

The project should grow with tests at several levels:

- unit tests for booking rules and state transitions;
- use-case tests for appointment creation and service retrieval;
- repository and database integration tests;
- FastAPI endpoint tests;
- migration tests;
- architecture-boundary tests.

The most important first safety property is preventing overlapping appointments for the same hairdresser.

---

## Project status

**Current stage:** In production on Render (`after-look-app`).

Completed milestones:

- Full-stack unified architecture (FastAPI backend + Astro frontend compiled in multi-stage Docker).
- Production deployment on Render cloud with managed PostgreSQL database.
- Google OAuth 2.0 / OpenID Connect authentication with dynamic role routing (Staff vs. Client).
- Multi-hairdresser availability and booking system with database-level overlap protection.
- Hairdresser agenda and real-time appointment management (`/peluquero/turnos`).
- Direct Google registration home (`/`) and mobile-optimized booking UX.
- 56 automated tests passing with 100% test coverage and 0 lint issues.
- Architectural decision records documented up to [ADR-017](docs/phase_01/adr/ADR-017-despliegue-continuo-en-render-con-docker-unificado-y-resolucion-dinamica-de-roles.md).
- Implementation state tracked in [Estado_implementacion_Peluqueria_Sergio_v1.6.md](docs/phase_01/implementation/Estado_implementacion_Peluqueria_Sergio_v1.6.md).

---

## Design principles

- Keep the appointment as the central business entity.
- Make business states explicit and validated.
- Preserve history instead of silently overwriting important changes.
- Keep external integrations behind clear boundaries.
- Do not add payments or other out-of-scope features without a registered change request.
- Update only the documentation affected by a new requirement.

---

## License

A license has not yet been selected.
