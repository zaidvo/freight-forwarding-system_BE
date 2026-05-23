# Backend

FastAPI backend for auth, users, groups, and module access.

## Setup

```powershell
cd Backend
py -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

If `py` is not available, install Python 3.11+ and retry.

## Environment

Create `.env` in `Backend`:

```env
APP_NAME=Backend API
APP_VERSION=0.1.0
API_PREFIX=/api/v1
DEBUG=true
DATABASE_URL=your_database_url
JWT_SECRET_KEY=change-this-secret
ROOT_ADMIN_FULL_NAME=Root Admin
ROOT_ADMIN_EMAIL=admin@example.com
ROOT_ADMIN_PASSWORD=your-password
```

## Database

Run migrations:

```powershell
alembic upgrade head
```

If using the venv executable directly:

```powershell
.\venv\Scripts\alembic.exe upgrade head
```

## Run

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Or:

```powershell
.\venv\Scripts\uvicorn.exe app.main:app --reload --host 127.0.0.1 --port 8000
```

API base URL:

```text
http://127.0.0.1:8000/api/v1
```
