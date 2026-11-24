# Healthcare Backend (Django + DRF + PostgreSQL)

A REST API for a healthcare application. Users can register and log in with JWT,
manage patient and doctor records, and assign doctors to patients.

**Stack:** Django 6, Django REST Framework, djangorestframework-simplejwt, PostgreSQL (psycopg 3), python-dotenv.

## Project structure

```
healthcare-backend/
├── healthcare/          # Project config: settings, root URLs, error handler, permissions
├── accounts/            # Custom email-based User model, register / login (JWT)
├── patients/            # Patient model + CRUD (scoped to the creating user)
├── doctors/             # Doctor model + CRUD (shared directory, creator-only edits)
├── mappings/            # Patient ↔ Doctor assignments
├── postman/             # Postman collection for every endpoint
├── .env.example         # Template for environment variables
├── docker-compose.yml   # Optional local PostgreSQL
└── requirements.txt
```

## Setup

1. **Clone and install**
   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env             # Windows: copy .env.example .env
   ```
   Then set `DJANGO_SECRET_KEY` and the `POSTGRES_*` values in `.env`.

3. **Start PostgreSQL.** Use an existing install (create the DB and user from `.env`), or run it with Docker:
   ```bash
   docker compose up -d
   ```

4. **Migrate and run**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser   # optional, for /admin/
   python manage.py runserver
   ```

The API is now at `http://127.0.0.1:8000/api/`.

## Environment variables

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `DJANGO_SECRET_KEY` | yes | – | Django secret key, also used to sign JWTs |
| `DJANGO_DEBUG` | no | `False` | Debug mode |
| `DJANGO_ALLOWED_HOSTS` | no | `localhost,127.0.0.1` | Comma-separated hosts |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | yes | – | Database credentials |
| `POSTGRES_HOST` / `POSTGRES_PORT` | no | `localhost` / `5432` | Database location |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | no | `60` | Access token lifetime |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | no | `7` | Refresh token lifetime |

## API reference

Every endpoint except register, login and token refresh needs this header:
`Authorization: Bearer <access_token>`

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Register with `name`, `email`, `password`. Returns the user plus `access`/`refresh` tokens |
| POST | `/api/auth/login/` | Log in with `email`, `password`. Returns `access`, `refresh`, `user` |
| POST | `/api/auth/token/refresh/` | Get a new access token from `refresh` *(extra)* |
| GET | `/api/auth/me/` | Current user's profile *(extra)* |

### Patients
Users only see and manage the patients **they created**.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/patients/` | Add a patient |
| GET | `/api/patients/` | List the authenticated user's patients |
| GET | `/api/patients/<id>/` | Patient details |
| PUT | `/api/patients/<id>/` | Update a patient |
| DELETE | `/api/patients/<id>/` | Delete a patient |

Fields: `name`*, `date_of_birth`* (YYYY-MM-DD), `gender`* (`male`/`female`/`other`), `email`, `phone`, `address`, `medical_history`. `age` is computed and read-only.

### Doctors
Doctors are a shared directory. Any authenticated user can list and view them,
but **only the user who added a doctor can update or delete it** (others get 403).

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/doctors/` | Add a doctor |
| GET | `/api/doctors/` | List all doctors |
| GET | `/api/doctors/<id>/` | Doctor details |
| PUT | `/api/doctors/<id>/` | Update a doctor |
| DELETE | `/api/doctors/<id>/` | Delete a doctor |

Fields: `name`*, `specialization`*, `email`* (unique), `phone`, `years_of_experience` (0–70), `hospital`.

### Patient-doctor mappings
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/mappings/` | Assign a doctor to a patient: `{"patient": 1, "doctor": 2, "notes": ""}` |
| GET | `/api/mappings/` | All mappings for the user's patients |
| GET | `/api/mappings/<patient_id>/` | All doctors assigned to that patient |
| DELETE | `/api/mappings/<id>/` | Remove a mapping (by **mapping id**) |

> The spec gives `GET` and `DELETE` the same URL shape, so the number means a **patient id** for GET and a **mapping id** for DELETE. Each assigned doctor in the GET response includes its `mapping_id` to use for DELETE.

Rules: you can only assign doctors to your own patients, and the same doctor can't be assigned to the same patient twice.

### Error format
All errors return a consistent JSON body:
```json
{
  "success": false,
  "error": {
    "status_code": 400,
    "message": "Validation failed.",
    "details": { "email": ["A doctor with this email already exists."] }
  }
}
```
Other responses: `401` when the token is missing or invalid, `403` when editing another user's doctor, `404` for missing records or records owned by someone else.

## Testing

**Automated tests** (20 tests, run against PostgreSQL):
```bash
python manage.py test
```

**Postman:** import `postman/healthcare-backend.postman_collection.json`. Run **Register** or **Login**
first; the collection stores the JWT and the created patient, doctor and mapping ids automatically,
so you can run the remaining requests in order.

**Example with curl:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@example.com", "password": "Demo@12345"}'
```
