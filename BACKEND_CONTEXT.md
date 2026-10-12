# Backend Context & Architecture Specification

> **Document Purpose**: Current state specification of the backend codebase for frontend planning and alignment.
> **Code Truth Date**: 2026-10-12
> **Repository Path**: `/home/zaid/Desktop/ff/freight-forwarding-system_BE`

---

## 1. Overview and Git Status

### 1.1 Git Verification Output
The following Git checks were executed against the active repository:

```bash
$ git status
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean

$ git branch --show-current
main

$ git fetch origin
# (Completed with exit code 0)

$ git log --oneline -5
0a9b638 (HEAD -> main, origin/main, origin/HEAD) changes
3b9f42f fixes
f2f0503 phase 2
6e8b91a fix
3cd79c0 more access rules

$ git rev-list --left-right --count HEAD...origin/main
0       0
```

### 1.2 Git State Summary
| Check | Status | Verification Note |
|---|---|---|
| Active Branch | `main` | Verified via `git branch --show-current` |
| Up-to-date with remote | Synchronized | `HEAD...origin/main` is `0 0` (0 commits ahead, 0 behind) |
| Working Tree | Clean | Verified via `git status` prior to OpenAPI export |

---

## 2. Stack and How to Run

### 2.1 Technology Stack & Versions
| Component | Technology | Version | Location / Verification |
|---|---|---|---|
| Language | Python | 3.14.4 | System / runtime |
| Web Framework | FastAPI | 0.143.0 | `requirements.txt`, `venv/lib` |
| ASGI Server | Uvicorn (standard) | 0.54.0 | `requirements.txt`, `venv/lib` |
| Database Engine | PostgreSQL | Remote (Neon DB) | `DATABASE_URL` driver: `postgresql+psycopg://` |
| Database Driver | Psycopg 3 | 3.3.6 (`psycopg-binary`) | `requirements.txt`, `venv/lib` |
| ORM | SQLAlchemy | 2.1.4 | `requirements.txt`, `venv/lib` |
| Migration Tool | Alembic | 1.20.0 | `requirements.txt`, `alembic/` |
| Data Validation | Pydantic / Pydantic-Settings | 2.14.1 / 2.15.0 | `requirements.txt`, `app/core/config.py` |
| Multipart Parser | python-multipart | 0.0.32 | `requirements.txt` |
| File Storage | Local Filesystem | Local Disk | `app/modules/trading_import/storage.py` |

### 2.2 Directory Structure (2-3 Levels Deep)
```text
freight-forwarding-system_BE/
├── alembic/                         # Alembic database migrations environment
│   ├── versions/                    # 8 migration revision scripts
│   ├── env.py                       # Alembic migration execution configuration
│   └── script.py.mako               # Template for new migrations
├── app/                             # Core application source package
│   ├── common/                      # Shared response envelopes and pagination stubs
│   │   ├── enums.py                 # (Empty stub file)
│   │   ├── pagination.py            # (Empty stub file)
│   │   ├── response.py              # Standard response helper `make_response`
│   │   └── utils.py                 # (Empty stub file)
│   ├── core/                        # Core configuration, security, and auth dependencies
│   │   ├── config.py                # Pydantic Settings and environment configuration
│   │   ├── dependencies.py          # (Empty stub file)
│   │   ├── exceptions.py            # (Empty stub file)
│   │   ├── permissions.py           # (Empty stub file)
│   │   └── security.py              # JWT encoding/decoding and PBKDF2 password hashing
│   ├── db/                          # Database connection and model discovery
│   │   ├── base.py                  # SQLAlchemy DeclarativeBase
│   │   ├── base_metadata.py         # Model aggregation for Alembic discovery
│   │   └── session.py               # SessionLocal engine and get_db generator
│   ├── modules/                     # Business domain modules
│   │   ├── access/                  # Access groups and group-to-module assignments
│   │   ├── audit/                   # Activity logging and audit query API
│   │   ├── auth/                    # Login, logout, tokens, password reset, and access dependencies
│   │   ├── health.py                # API healthcheck endpoint
│   │   ├── modules/                 # System modules catalog and database seeder
│   │   ├── trading_import/          # Trading import records, BL documents, forms, invoices, receipts
│   │   └── users/                   # User CRUD, role management, and status deactivation
│   └── main.py                      # FastAPI application entrypoint, CORS, routes, lifespan seeders
├── data/                            # Default upload storage root on local disk
│   └── trading/                     # Default storage directory for trading PDF uploads
│       └── records/                 # Per-record folders: records/{record_id}/{document_type}/
├── alembic.ini                      # Alembic configuration file
├── openapi.json                     # Generated OpenAPI 3.1.0 specification
├── README.md                        # Project setup instructions
└── requirements.txt                 # Python pip dependencies
```

### 2.3 How to Run Locally

#### Commands (Linux / Bash)
```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Execute database migrations
alembic upgrade head

# 4. Start local development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### Environment Variables (Names Only)
| Variable Name | Required | Default Value | Purpose |
|---|---|---|---|
| `DATABASE_URL` | **Yes** | *None* | PostgreSQL database connection string (`postgresql+psycopg://...`) |
| `APP_NAME` | No | `"Backend API"` | Application display name |
| `APP_VERSION` | No | `"0.1.0"` | Application version number |
| `API_PREFIX` | No | `"/api/v1"` | URL prefix for all API routes |
| `DEBUG` | No | `True` | Debug mode (parses 'release'/'prod' to False) |
| `JWT_SECRET_KEY` | No | `[REDACTED]` | HMAC-SHA256 signing secret for JWTs |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `60` | Token expiration duration in minutes |
| `ROOT_ADMIN_FULL_NAME` | No | `"Root Admin"` | Full name for seeded root administrator |
| `ROOT_ADMIN_EMAIL` | No | `"admin@example.com"` | Email address for seeded root administrator |
| `ROOT_ADMIN_PASSWORD` | No | `[REDACTED]` | Initial password for seeded root administrator |
| `BACKEND_CORS_ORIGINS` | No | `["http://localhost:5173", "http://127.0.0.1:5173", "http://82.112.254.202:3020"]` | Allowed CORS frontend origins |
| `TRADING_IMPORT_DATA_DIR` | No | `"data/trading"` | Local filesystem path for file uploads |
| `TRADING_IMPORT_MAX_UPLOAD_MB` | No | `25` | Maximum upload file size in megabytes |

### 2.4 File Storage Used for Uploads
- **Storage Type**: Local filesystem disk storage (`TradingImportStorage` in `app/modules/trading_import/storage.py`).
- **Path Template**: `{TRADING_IMPORT_DATA_DIR}/records/{record_id}/{document_type}/{uuid4().hex}.pdf`.
- **Validation**: Enforces `.pdf` extension; enforces max file size (default 25 MB).
- **Cloud / Object Storage**: No S3, MinIO, or Google Cloud Storage client exists in the codebase.

---

## 3. Database Schema

### 3.1 Model and Table Details

#### Table: `users`
| Column | Type | Nullable | Constraints & Defaults | Relationships / Foreign Keys |
|---|---|---|---|---|
| `id` | `INTEGER` | No | Primary Key, Indexed | Target of multiple FKs |
| `full_name` | `VARCHAR(150)` | No | — | — |
| `email` | `VARCHAR(255)` | No | Unique, Indexed | — |
| `password_hash` | `VARCHAR(255)` | No | PBKDF2 hash string | — |
| `role` | `VARCHAR` (`user_role_enum`) | No | Values: `'root'`, `'user'`. Default: `'user'` | — |
| `status` | `VARCHAR` (`user_status_enum`) | No | Values: `'active'`, `'inactive'`. Default: `'active'` | — |
| `last_login_at` | `DATETIME(timezone=True)` | Yes | — | — |
| `created_by` | `INTEGER` | Yes | Indexed | `FK -> users.id (ON DELETE SET NULL)` |
| `created_at` | `DATETIME(timezone=True)` | No | Default: `utcnow` | — |
| `updated_at` | `DATETIME(timezone=True)` | No | Default: `utcnow`, onupdate `utcnow` | — |

*Relationships*: `groups`: secondary relationship to `access_groups` via `user_groups`.

#### Table: `password_reset_tokens`
| Column | Type | Nullable | Constraints & Defaults | Relationships / Foreign Keys |
|---|---|---|---|---|
| `id` | `INTEGER` | No | Primary Key, Indexed | — |
| `user_id` | `INTEGER` | No | Indexed | `FK -> users.id (ON DELETE CASCADE)` |
| `token_hash` | `VARCHAR(255)` | No | Indexed (SHA-256 hash) | — |
| `expires_at` | `DATETIME(timezone=True)` | No | 30 minutes from creation | — |
| `used_at` | `DATETIME(timezone=True)` | Yes | Set upon consumption | — |
| `created_at` | `DATETIME(timezone=True)` | No | Default: `utcnow` | — |

#### Table: `activity_logs`
| Column | Type | Nullable | Constraints & Defaults | Relationships / Foreign Keys |
|---|---|---|---|---|
| `id` | `INTEGER` | No | Primary Key, Indexed | — |
| `actor_user_id` | `INTEGER` | Yes | Indexed | `FK -> users.id (ON DELETE SET NULL)` |
| `action` | `VARCHAR` (`activity_action_enum`) | No | Enum: `'login'`, `'logout'`, `'failed_login'`, `'create_user'`, `'update_user'`, `'deactivate_user'`, `'change_password'`, `'forgot_password'`, `'reset_password'` | — |
| `target_user_id` | `INTEGER` | Yes | Indexed | `FK -> users.id (ON DELETE SET NULL)` |
| `success` | `BOOLEAN` | No | Default: `False` | — |
| `description` | `VARCHAR(500)` | Yes | — | — |
| `ip_address` | `VARCHAR(45)` | Yes | IPv4 / IPv6 string | — |
| `user_agent` | `VARCHAR(500)` | Yes | Request client header | — |
| `created_at` | `DATETIME(timezone=True)` | No | Default: `utcnow` | — |

#### Table: `modules`
| Column | Type | Nullable | Constraints & Defaults | Relationships / Foreign Keys |
|---|---|---|---|---|
| `id` | `INTEGER` | No | Primary Key, Indexed | Target of `group_modules.module_id` |
| `name` | `VARCHAR(100)` | No | — | — |
| `slug` | `VARCHAR(80)` | No | Unique, Indexed | Used in authorization dependencies |
| `icon` | `VARCHAR(80)` | No | Lucide icon name | — |
| `color` | `VARCHAR(20)` | No | Hex color code | — |
| `route` | `VARCHAR(120)` | Yes | Frontend route URL | — |
| `is_active` | `BOOLEAN` | No | Default: `False` | — |
| `sort_order` | `INTEGER` | No | Ordering index | — |

*Relationships*: `groups`: secondary relationship to `access_groups` via `group_modules`.

#### Table: `access_groups`
| Column | Type | Nullable | Constraints & Defaults | Relationships / Foreign Keys |
|---|---|---|---|---|
| `id` | `INTEGER` | No | Primary Key, Indexed | Target of FKs in join tables |
| `name` | `VARCHAR(120)` | No | Unique | — |
| `description` | `VARCHAR(500)` | Yes | — | — |
| `created_at` | `DATETIME(timezone=True)` | No | Default: `utcnow` | — |
| `updated_at` | `DATETIME(timezone=True)` | No | Default: `utcnow`, onupdate `utcnow` | — |

*Relationships*: `modules` via `group_modules`, `users` via `user_groups`.

#### Table: `group_modules` (Join Table)
| Column | Type | Nullable | Constraints & Defaults | Relationships / Foreign Keys |
|---|---|---|---|---|
| `group_id` | `INTEGER` | No | Composite Primary Key | `FK -> access_groups.id (ON DELETE CASCADE)` |
| `module_id` | `INTEGER` | No | Composite Primary Key | `FK -> modules.id (ON DELETE CASCADE)` |

#### Table: `user_groups` (Join Table)
| Column | Type | Nullable | Constraints & Defaults | Relationships / Foreign Keys |
|---|---|---|---|---|
| `user_id` | `INTEGER` | No | Composite Primary Key | `FK -> users.id (ON DELETE CASCADE)` |
| `group_id` | `INTEGER` | No | Composite Primary Key | `FK -> access_groups.id (ON DELETE CASCADE)` |

#### Table: `trading_sales_import_records`
| Column | Type | Nullable | Constraints & Defaults | Relationships / Foreign Keys |
|---|---|---|---|---|
| `id` | `INTEGER` | No | Primary Key, Indexed | Target of parent record FKs |
| `reference_no` | `VARCHAR(80)` | Yes | Unique, Indexed | Human-facing record identifier |
| `title` | `VARCHAR(180)` | Yes | Free text | — |
| `customer` | `VARCHAR(180)` | Yes | Plain text string | **No FK / No customer table** |
| `salesperson` | `VARCHAR(150)` | Yes | Plain text string | — |
| `company` | `VARCHAR(180)` | Yes | Plain text string | — |
| `expected_arrival_date` | `DATE` | Yes | ETA date | — |
| `remarks` | `VARCHAR(1000)` | Yes | Free text notes | — |
| `status` | `VARCHAR` (`trading_import_record_status_enum`) | No | Enum: `'draft'`, `'in_progress'`, `'ready_for_invoice'`, `'invoiced'`, `'paid'`, `'detention'`. Default: `'draft'` | — |
| `created_by` | `INTEGER` | Yes | Indexed | `FK -> users.id (ON DELETE SET NULL)` |
| `created_at` | `DATETIME(timezone=True)` | No | Default: `utcnow` | — |
| `updated_at` | `DATETIME(timezone=True)` | No | Default: `utcnow`, onupdate `utcnow` | — |

*Child Relationships*:
- `documents`: 1-to-many `TradingSalesDocument` (`cascade="all, delete-orphan"`)
- `forms`: 1-to-many `TradingSalesForm` (`cascade="all, delete-orphan"`)
- `freight_invoice`: 1-to-1 `TradingSalesFreightInvoice` (`uselist=False`, `cascade="all, delete-orphan"`)
- `payment_receipts`: 1-to-many `TradingSalesPaymentReceipt` (`cascade="all, delete-orphan"`)
- `detention_invoice`: 1-to-1 `TradingSalesDetentionInvoice` (`uselist=False`, `cascade="all, delete-orphan"`)

#### Table: `trading_sales_documents`
| Column | Type | Nullable | Constraints & Defaults | Relationships / Foreign Keys |
|---|---|---|---|---|
| `id` | `INTEGER` | No | Primary Key, Indexed | — |
| `record_id` | `INTEGER` | No | Indexed | `FK -> trading_sales_import_records.id (ON DELETE CASCADE)` |
| `document_type` | `VARCHAR` (`trading_import_document_type_enum`) | No | Values: `'draft_bl'`, `'house_bl'`, `'master_bl'` | Unique with `record_id` (`uq_trading_sales_document_record_type`) |
| `original_filename` | `VARCHAR(255)` | No | Uploaded filename | — |
| `stored_filename` | `VARCHAR(255)` | No | UUID filename | — |
| `storage_path` | `VARCHAR(600)` | No | Relative filesystem path | — |
| `content_type` | `VARCHAR(120)` | Yes | MIME type | — |
| `file_size` | `INTEGER` | No | Bytes | — |
| `uploaded_by` | `INTEGER` | Yes | Indexed | `FK -> users.id (ON DELETE SET NULL)` |
| `uploaded_at` | `DATETIME(timezone=True)` | No | Default: `utcnow` | — |
| `created_at` | `DATETIME(timezone=True)` | No | Default: `utcnow` | — |

#### Table: `trading_sales_forms`
| Column | Type | Nullable | Constraints & Defaults | Relationships / Foreign Keys |
|---|---|---|---|---|
| `id` | `INTEGER` | No | Primary Key, Indexed | — |
| `record_id` | `INTEGER` | No | Indexed | `FK -> trading_sales_import_records.id (ON DELETE CASCADE)` |
| `document_type` | `VARCHAR` (`trading_import_document_type_enum`) | No | Values: `'draft_bl'`, `'house_bl'`, `'master_bl'` | Unique with `record_id` (`uq_trading_sales_form_record_type`) |
| `data` | `JSON` (`JSONB` in PG) | No | Default: `{}` | Arbitrary document form fields |
| `canonical_data` | `JSON` (`JSONB` in PG) | No | Default: `{}` | Normalized aliases mapped automatically |
| `completed_by` | `INTEGER` | Yes | Indexed | `FK -> users.id (ON DELETE SET NULL)` |
| `completed_at` | `DATETIME(timezone=True)` | Yes | Nullable timestamp | Marks form completion |
| `created_at` | `DATETIME(timezone=True)` | No | Default: `utcnow` | — |
| `updated_at` | `DATETIME(timezone=True)` | No | Default: `utcnow`, onupdate `utcnow` | — |

#### Table: `trading_sales_freight_invoices`
| Column | Type | Nullable | Constraints & Defaults | Relationships / Foreign Keys |
|---|---|---|---|---|
| `id` | `INTEGER` | No | Primary Key, Indexed | — |
| `record_id` | `INTEGER` | No | Unique, Indexed | `FK -> trading_sales_import_records.id (ON DELETE CASCADE)` |
| `invoice_no` | `VARCHAR(80)` | Yes | Unique, Indexed | Invoice number |
| `charges` | `JSON` (`JSONB` in PG) | No | Default: `[]` | List of charge line objects |
| `manual_fields` | `JSON` (`JSONB` in PG) | No | Default: `{}` | Custom header entries |
| `render_data` | `JSON` (`JSONB` in PG) | No | Default: `{}` | Precomputed print / display payload |
| `created_by` | `INTEGER` | Yes | Indexed | `FK -> users.id (ON DELETE SET NULL)` |
| `created_at` | `DATETIME(timezone=True)` | No | Default: `utcnow` | — |
| `updated_at` | `DATETIME(timezone=True)` | No | Default: `utcnow`, onupdate `utcnow` | — |

#### Table: `trading_sales_payment_receipts`
| Column | Type | Nullable | Constraints & Defaults | Relationships / Foreign Keys |
|---|---|---|---|---|
| `id` | `INTEGER` | No | Primary Key, Indexed | — |
| `record_id` | `INTEGER` | No | Indexed | `FK -> trading_sales_import_records.id (ON DELETE CASCADE)` |
| `receipt_no` | `VARCHAR(80)` | Yes | Unique, Indexed | Receipt number |
| `tid` | `VARCHAR(120)` | No | Transaction reference | — |
| `amount` | `NUMERIC(14, 2)` | No | Amount paid | — |
| `currency` | `VARCHAR(10)` | No | Default: `'PKR'` | Currency code |
| `payment_date` | `DATE` | Yes | Date paid | — |
| `render_data` | `JSON` (`JSONB` in PG) | No | Default: `{}` | Precomputed receipt presentation payload |
| `created_by` | `INTEGER` | Yes | Indexed | `FK -> users.id (ON DELETE SET NULL)` |
| `created_at` | `DATETIME(timezone=True)` | No | Default: `utcnow` | — |

#### Table: `trading_sales_detention_invoices`
| Column | Type | Nullable | Constraints & Defaults | Relationships / Foreign Keys |
|---|---|---|---|---|
| `id` | `INTEGER` | No | Primary Key, Indexed | — |
| `record_id` | `INTEGER` | No | Unique, Indexed | `FK -> trading_sales_import_records.id (ON DELETE CASCADE)` |
| `invoice_no` | `VARCHAR(80)` | Yes | Unique, Indexed | Detention invoice identifier |
| `detention_start` | `DATE` | No | Start of detention period | — |
| `detention_end` | `DATE` | No | End of detention period | — |
| `free_days` | `INTEGER` | No | Default: `0` | Number of allowed free days |
| `chargeable_days` | `INTEGER` | No | Default: `0` | Computed chargeable days |
| `per_day_amount` | `NUMERIC(14, 2)` | No | Default: `0` | Daily detention rate |
| `detention_amount` | `NUMERIC(14, 2)` | No | Default: `0` | Computed total detention charge |
| `security_deposit` | `NUMERIC(14, 2)` | No | Default: `0` | Pre-collected security deposit |
| `refund_amount` | `NUMERIC(14, 2)` | No | Default: `0` | Computed net refund / balance |
| `currency` | `VARCHAR(10)` | No | Default: `'PKR'` | Currency code |
| `manual_fields` | `JSON` (`JSONB` in PG) | No | Default: `{}` | Custom header data |
| `render_data` | `JSON` (`JSONB` in PG) | No | Default: `{}` | Precomputed detention invoice payload |
| `created_by` | `INTEGER` | Yes | Indexed | `FK -> users.id (ON DELETE SET NULL)` |
| `created_at` | `DATETIME(timezone=True)` | No | Default: `utcnow` | — |
| `updated_at` | `DATETIME(timezone=True)` | No | Default: `utcnow`, onupdate `utcnow` | — |

---

### 3.2 Migrations Status
- **Latest Migration Revision**: `e4c2a91f7d35` (`alembic/versions/e4c2a91f7d35_add_trading_import_record_metadata.py`)
- **Migration History Order**:
  1. `cc759478dba2`: `create minimal user auth audit models`
  2. `016fab54b66f`: `add users password_reset_tokens activity_logs`
  3. `9b7f2d4c1a83`: `create minimal tables`
  4. `4a9c2e7b8f01`: `rename super_admin role to root`
  5. `a2f3c5d9e781`: `create and seed modules`
  6. `b7c4f92a10d2`: `create access groups`
  7. `d8f1b42c6a90`: `create trading import sales tables`
  8. `e4c2a91f7d35` (*HEAD*): `add trading import record metadata`
- **Schema Alignment Verification**: The models match the database schema. When checked against the live PostgreSQL database with `alembic check`, all 13 tables, columns, constraints, and sequences are present. The only difference flagged by Alembic is a dialect-level detail: columns created as PostgreSQL native `JSONB` in migration `d8f1b42c6a90` vs SQLAlchemy generic `JSON()` in the Python model declarations.

---

### 3.3 Seed Data on First Run
Seed routines execute inside the application lifespan in `app/main.py`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        seed_root_admin(db, ...)
        seed_modules(db)
    finally:
        db.close()
    yield
```

1. **Root Administrator** (`seed_root_admin` in `app/modules/users/seed.py`):
   - Creates root user if not existing: `full_name=settings.root_admin_full_name`, `email=settings.root_admin_email`, `password_hash=hash_password(settings.root_admin_password)`, `role=UserRole.ROOT`.
   - If user exists by email, forces `role=UserRole.ROOT`.
2. **Modules** (`seed_modules` in `app/modules/modules/seed.py`):
   - Upserts 5 system modules:
     | Name | Slug | Icon | Color | Route | Is Active | Sort Order |
     |---|---|---|---|---|---|---|
     | Account Management | `account-management` | `users` | `#3b82f6` | `/accounts` | `True` | 1 |
     | Operations | `operations` | `ship` | `#0ea5e9` | `None` | `False` | 2 |
     | Finance | `finance` | `wallet` | `#059669` | `None` | `False` | 3 |
     | Sales | `sales` | `shopping-cart` | `#f59e0b` | `None` | `False` | 4 |
     | Marketing | `marketing` | `bar-chart-3` | `#c026d3` | `None` | `False` | 5 |
3. **Access Groups Seed**:
   - **None seeded**. `app/modules/access/seed.py` is empty (0 bytes). No access groups or module group associations are created automatically. Groups must be created manually via `POST /api/v1/groups`.

---

## 4. API Endpoints

The complete OpenAPI specification has been exported to [`openapi.json`](file:///home/zaid/Desktop/ff/freight-forwarding-system_BE/openapi.json) in the project root.

### 4.1 Master Endpoints Table (All 35 Endpoints)

| Method | Path | Purpose | Auth Required | Module Slug / Permission Required |
|---|---|---|---|---|
| **Root & Health** | | | | |
| `GET` | `/` | API welcome message | No | None |
| `GET` | `/api/v1/health` | Health check endpoint | No | None |
| **Auth** | | | | |
| `POST` | `/api/v1/auth/login` | Authenticate user & return JWT token | No | None |
| `POST` | `/api/v1/auth/logout` | Log out current user & record audit log | Yes (Bearer) | None |
| `POST` | `/api/v1/auth/forgot-password` | Generate password reset token | No | None |
| `POST` | `/api/v1/auth/reset-password` | Reset password using reset token | No | None |
| `POST` | `/api/v1/auth/change-password` | Change password for logged-in user | Yes (Bearer) | None |
| `GET` | `/api/v1/auth/me` | Fetch authenticated user profile | Yes (Bearer) | None |
| `GET` | `/api/v1/auth/me/access` | Fetch list of accessible module slugs for user | Yes (Bearer) | None |
| **Activity Logs** | | | | |
| `GET` | `/api/v1/activity-logs` | List audit activity logs (paginated, filtered) | Yes (Bearer) | Module `account-management` (or Root) |
| **Users** | | | | |
| `GET` | `/api/v1/users` | List all users with group IDs | Yes (Bearer) | Module `account-management` (or Root) |
| `GET` | `/api/v1/users/{user_id}` | Get user details by ID | Yes (Bearer) | Module `account-management` (or Root) |
| `POST` | `/api/v1/users` | Create new user (role defaults to `user`) | Yes (Bearer) | Role `root` only (`require_root`) |
| `PUT` | `/api/v1/users/{user_id}` | Update existing non-root user details | Yes (Bearer) | Role `root` only (`require_root`) |
| `DELETE` | `/api/v1/users/{user_id}` | Soft deactivate user (`status='inactive'`) | Yes (Bearer) | Role `root` only (`require_root`) |
| `PATCH` | `/api/v1/users/{user_id}/activate` | Activate user (`status='active'`) | Yes (Bearer) | Role `root` only (`require_root`) |
| **Modules** | | | | |
| `GET` | `/api/v1/modules` | List all system modules | Yes (Bearer) | Role `root` only (`require_root`) |
| **Access Groups** | | | | |
| `GET` | `/api/v1/groups` | List all access groups with module and user IDs | Yes (Bearer) | Role `root` only (`require_root`) |
| `POST` | `/api/v1/groups` | Create new access group | Yes (Bearer) | Role `root` only (`require_root`) |
| `PUT` | `/api/v1/groups/{group_id}` | Update access group and module associations | Yes (Bearer) | Role `root` only (`require_root`) |
| `DELETE` | `/api/v1/groups/{group_id}` | Delete access group | Yes (Bearer) | Role `root` only (`require_root`) |
| `PUT` | `/api/v1/groups/users/{user_id}` | Assign access groups to a user | Yes (Bearer) | Role `root` only (`require_root`) |
| **Trading Import Sales** | | | | |
| `GET` | `/api/v1/trading-import/sales/records` | List all trading import sales records | Yes (Bearer) | Module `sales` (or Root) |
| `POST` | `/api/v1/trading-import/sales/records` | Create new import sales record | Yes (Bearer) | Module `sales` (or Root) |
| `GET` | `/api/v1/trading-import/sales/records/{record_id}` | Get complete record with documents, forms, invoices | Yes (Bearer) | Module `sales` (or Root) |
| `PATCH` | `/api/v1/trading-import/sales/records/{record_id}` | Update record metadata or status override | Yes (Bearer) | Module `sales` (or Root) |
| `POST` | `/api/v1/trading-import/sales/records/{record_id}/documents/{document_type}/upload` | Upload PDF (`draft_bl`, `house_bl`, `master_bl`) | Yes (Bearer) | Module `sales` (or Root) |
| `GET` | `/api/v1/trading-import/sales/records/{record_id}/documents/{document_type}/download` | Download uploaded PDF file | Yes (Bearer) | Module `sales` (or Root) |
| `PUT` | `/api/v1/trading-import/sales/records/{record_id}/forms/{document_type}` | Upsert parsed/entered form data for document type | Yes (Bearer) | Module `sales` (or Root) |
| `GET` | `/api/v1/trading-import/sales/records/{record_id}/suggestions` | Get autocomplete suggestions aggregated across forms | Yes (Bearer) | Module `sales` (or Root) |
| `GET` | `/api/v1/trading-import/sales/records/{record_id}/freight-invoice/render` | Get pre-merged freight invoice render payload | Yes (Bearer) | Module `sales` (or Root) |
| `PUT` | `/api/v1/trading-import/sales/records/{record_id}/freight-invoice` | Upsert freight invoice with line charges | Yes (Bearer) | Module `sales` (or Root) |
| `POST` | `/api/v1/trading-import/sales/records/{record_id}/payment-receipts` | Create payment receipt for import record | Yes (Bearer) | Module `sales` (or Root) |
| `GET` | `/api/v1/trading-import/sales/records/{record_id}/payment-receipts` | List all payment receipts for an import record | Yes (Bearer) | Module `sales` (or Root) |
| `PUT` | `/api/v1/trading-import/sales/records/{record_id}/detention-invoice` | Upsert detention invoice with detention days & deposit | Yes (Bearer) | Module `sales` (or Root) |

---

### 4.2 Standard Response Envelope & Error Format

#### Successful Response Envelope
Constructed via `make_response` in `app/common/response.py`:
```json
{
  "success": true,
  "message": "Operation successful description",
  "data": { ... },         // Optional: Included when data is returned
  "next_action": "..."     // Optional: Present if next workflow step is passed
}
```

*Note on file downloads*: The document download endpoint returns raw binary with `media_type="application/pdf"` via `fastapi.responses.FileResponse`, bypassing the JSON envelope.

#### Error Response Format
Endpoints raise standard FastAPI `HTTPException`. No global custom exception handler overrides this, so errors follow FastAPI's native error format:

- Standard Application Errors (400, 401, 403, 404, 409, 413):
```json
{
  "detail": "Descriptive error message string"
}
```

- Request Validation Errors (HTTP 422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "field_name"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

---

### 4.3 Pagination and Filter Conventions

1. **Activity Logs (`GET /api/v1/activity-logs`)**:
   - Only endpoint in the application featuring pagination and query filtering.
   - Query Parameters:
     - `page`: Integer (default: `1`, minimum: `1`)
     - `page_size`: Integer (default: `10`, minimum: `1`, maximum: `50`)
     - `category`: String pattern `^(important|account|security|auth|all)$` (default: `"important"`)
   - Category filtering behavior:
     - `important`: Excludes `login` and `logout`.
     - `account`: Includes `create_user`, `update_user`, `deactivate_user`.
     - `security`: Includes failed actions (`success == False`) OR `failed_login`, `change_password`, `forgot_password`, `reset_password`.
     - `auth`: Includes `login`, `logout`, `failed_login`.
     - `all`: Unfiltered.
   - Response Payload Structure:
     ```json
     {
       "items": [ ... ],
       "page": 1,
       "page_size": 10,
       "total": 42,
       "total_pages": 5,
       "category": "important"
     }
     ```

2. **All Other List Endpoints**:
   - `GET /api/v1/users`
   - `GET /api/v1/groups`
   - `GET /api/v1/modules`
   - `GET /api/v1/trading-import/sales/records`
   - `GET /api/v1/trading-import/sales/records/{record_id}/payment-receipts`
   - **Convention**: Return full unpaginated flat arrays inside `data`. No query filters or sorting parameters are supported by the backend routers.

---

## 5. Auth and Permissions

### 5.1 Login, Token Type, Expiry, and Logout Behavior
- **Login Endpoint**: `POST /api/v1/auth/login` (`LoginRequest`: `email`, `password`).
- **Password Hashing**: PBKDF2 HMAC-SHA256 with 100,000 iterations and 16-byte cryptographically random salt (`pbkdf2_sha256$100000${salt}${hash}`).
- **Token Type**: Stateless JWT signed via custom HMAC-SHA256 (`alg: HS256`).
- **Token Payload**: `{"sub": "<user_id_string>", "exp": <unix_timestamp>}`.
- **Token Expiry**: Configured via `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 60 minutes).
- **Bearer Authentication**: Handled via `OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")`. Authorization header format: `Bearer <token>`.
- **Logout Behavior**: `POST /api/v1/auth/logout` records an activity log entry (`"User <email> logged out"`). Since tokens are stateless and no token blocklist or database session store exists, token invalidation is client-side (the backend does not reject previously issued valid tokens until expiration).
- **Password Reset**:
  - `POST /api/v1/auth/forgot-password` generates a 32-byte URL-safe token, hashes it with SHA-256 in `password_reset_tokens`, and returns the raw `reset_token` in the HTTP response JSON (`{"data": {"reset_token": "..."}}`). (No email sending service exists).
  - `POST /api/v1/auth/reset-password` accepts `token` and `new_password`, marks the token `used_at`, and updates the password hash.

### 5.2 User Model, Roles, and Status
- **User Roles** (`UserRole`):
  - `root`: Root system administrator. Root bypasses all module permission checks. Root accounts cannot be updated or deactivated (`UserService._ensure_not_root`). Root accounts cannot be created via the user API (only via initial lifespan seeding).
  - `user`: Standard application user.
- **User Status** (`UserStatus`):
  - `active`: Allowed to authenticate and access APIs.
  - `inactive`: Blocked from authenticating (`401 Unauthorized` / `403 Forbidden`). Deactivation via `DELETE /api/v1/users/{id}` sets this status. Re-activation via `PATCH /api/v1/users/{id}/activate` restores `active` status.

### 5.3 Group-to-Module Mapping
- Users belong to zero, one, or more `access_groups` via `user_groups`.
- Groups have access to zero, one, or more `modules` via `group_modules`.
- Effective permissions of a user with role `user` are the union of all `module.slug` values belonging to their assigned groups.
- `GET /api/v1/auth/me/access`:
  - Returns `{"modules": ["account-management", "sales", ...]}`.
  - If user is `root`: Returns ALL slugs existing in the `modules` table.
  - If user is `user`: Returns the sorted list of slugs associated with their groups.

### 5.4 Exact List of Module Slugs in Database
The database seeds exactly 5 module slugs:
1. `account-management` (Active: `True`)
2. `operations` (Active: `False`)
3. `finance` (Active: `False`)
4. `sales` (Active: `False`)
5. `marketing` (Active: `False`)

*Note*: Default groups get **no slugs** because **no default groups are seeded in the database**.

### 5.5 How Module Slugs and Roles Are Enforced
Enforced at the route handler level using FastAPI dependency injection (`Depends(...)`):

1. **Role Enforcement (`require_root`)**:
   ```python
   def require_root(current_user: User = Depends(get_current_user)) -> User:
       if current_user.role != UserRole.ROOT:
           raise HTTPException(status_code=403, detail="Root access required")
       return current_user
   ```
   Used on: all `/api/v1/groups` endpoints, `/api/v1/modules`, and user modification endpoints (`POST`, `PUT`, `DELETE`, `PATCH /activate` on `/api/v1/users`).

2. **Module Enforcement (`require_module_access(module_slug)`)**:
   ```python
   def require_module_access(module_slug: str):
       def dependency(current_user: User = Depends(get_current_user)) -> User:
           if current_user.role == UserRole.ROOT:
               return current_user
           has_access = any(
               module.slug == module_slug
               for group in current_user.groups
               for module in group.modules
           )
           if not has_access:
               raise HTTPException(status_code=403, detail=f"{module_slug} access required")
           return current_user
       return dependency
   ```
   Used on:
   - Module slug `account-management`: Protects `GET /api/v1/activity-logs`, `GET /api/v1/users`, and `GET /api/v1/users/{user_id}`.
   - Module slug `sales`: Protects all `/api/v1/trading-import/sales/...` endpoints.

### 5.6 Activity / Audit Logging
- **Service**: `ActivityLogService` in `app/modules/audit/service.py`.
- **Logged Actions**:
  - `login`: Successful login.
  - `logout`: User logout.
  - `failed_login`: Wrong credentials or inactive user attempt.
  - `create_user`: Root user creates a new user.
  - `update_user`: Root user updates user details or activates user.
  - `deactivate_user`: Root user deactivates a user.
  - `change_password`: Logged-in user changes password.
  - `forgot_password`: Forgot password request submitted.
  - `reset_password`: Token-based password reset completed.
- **Fields Stored**:
  - `actor_user_id`: ID of the initiating user (nullable).
  - `action`: Enum `ActivityAction`.
  - `target_user_id`: ID of the affected user (nullable).
  - `success`: Boolean flag (`True` or `False`).
  - `description`: Human-readable summary string (e.g. `"Root created user John Doe"`).
  - `ip_address`: Client IP address from request.
  - `user_agent`: Client User-Agent header from request.
  - `created_at`: UTC timestamp.
- **Scope Limitation**: Audit logging only records Auth and User Management actions. It does **not** log trading import records, uploads, form saves, or invoices.

---

## 6. Answers to Specific Checks (A to I)

### A. Freight Endpoints (Inquiries, Quotations, Bookings, Shipments, Documents, Finance)
- **Answer**: **NO**.
- **File Evidence**:
  - There are no routers, controllers, or tables for freight inquiries, quotations, bookings, or shipments anywhere in `app/modules/` or `app/main.py`.
  - The only occurrences of the word "freight" in endpoints are the two freight invoice endpoints under trading import:
    - `GET /api/v1/trading-import/sales/records/{record_id}/freight-invoice/render` (`app/modules/trading_import/router.py#L153`)
    - `PUT /api/v1/trading-import/sales/records/{record_id}/freight-invoice` (`app/modules/trading_import/router.py#L163`)
    These are purely for billing charges against a trading import record.

### B. Trading Sales Endpoints (Inquiries, Quotations, Proforma Invoices, Purchase Orders, Deal Confirmation)
- **Answer**: **NO**.
- **File Evidence**:
  - Grepping for `proforma`, `purchase_order`, or `deal_confirmation` in `app/` returns 0 matches.
  - The only trading endpoints in the entire project are the 13 endpoints mounted under `/api/v1/trading-import/sales/records` in `app/modules/trading_import/router.py#L27`.

### C. Customers Table / Endpoint / `customer_id`
- **Answer**: **NO**.
- **File Evidence**:
  - There is **no Customers table** in the schema (`app/db/base_metadata.py`).
  - There is **no Customers endpoint** in `app/main.py` or any module.
  - There is **no `customer_id` foreign key** on any database table.
  - The only representation of a customer is a plain text column:
    ```python
    # app/modules/trading_import/model.py:33
    customer: Mapped[str | None] = mapped_column(String(180))
    ```
    And an alias entry in `CANONICAL_FIELD_ALIASES` mapping `"customer"` to `"bill_to"` (`app/modules/trading_import/service.py#L29`).

### D. Indenting (Parties, Deals, Commissions)
- **Answer**: **NO**.
- **File Evidence**:
  - Grepping `indent` across `app/` and `alembic/` returns 0 results. No models, tables, endpoints, or references exist.

### E. Clearing Agent, Shipper, Consignee Tables or Fields
- **Answer**: **NO relational tables or dedicated columns exist**.
- **File Evidence**:
  - `clearing_agent`, `shipper`, and `consignee` do **not** exist as tables or as columns on `trading_sales_import_records`.
  - They exist solely as string aliases in `CANONICAL_FIELD_ALIASES` (`app/modules/trading_import/service.py#L31-L33`) and `INVOICE_AUTO_FIELD_KEYS` (`app/modules/trading_import/service.py#L80-L87`).
  - They are stored inside the unstructured `canonical_data` JSON dictionary on `TradingSalesForm` and merged into `render_data` JSON for freight/detention invoices.

### F. "trading" Module Slug in Database
- **Answer**: **NO**.
- **File Evidence**:
  - `MODULE_SEED_DATA` in `app/modules/modules/seed.py#L6-L52` defines only 5 slugs:
    1. `account-management`
    2. `operations`
    3. `finance`
    4. `sales`
    5. `marketing`
  - There is no `"trading"` or `"trading-import"` slug.
  - Trading import routes explicitly check the `"sales"` slug (`app/modules/trading_import/router.py#L28`):
    ```python
    require_trading_import_sales = require_module_access("sales")
    ```

### G. Trading Import Module (`/api/v1/trading-import/sales/records`)
- **Document Types Supported**:
  Enum `TradingImportDocumentType`: `'draft_bl'`, `'house_bl'`, `'master_bl'`.
- **Full Tables and Columns**:
  1. `trading_sales_import_records`: `id`, `reference_no`, `title`, `customer`, `salesperson`, `company`, `expected_arrival_date`, `remarks`, `status`, `created_by`, `created_at`, `updated_at`.
  2. `trading_sales_documents`: `id`, `record_id`, `document_type`, `original_filename`, `stored_filename`, `storage_path`, `content_type`, `file_size`, `uploaded_by`, `uploaded_at`, `created_at`.
  3. `trading_sales_forms`: `id`, `record_id`, `document_type`, `data`, `canonical_data`, `completed_by`, `completed_at`, `created_at`, `updated_at`.
  4. `trading_sales_freight_invoices`: `id`, `record_id`, `invoice_no`, `charges`, `manual_fields`, `render_data`, `created_by`, `created_at`, `updated_at`.
  5. `trading_sales_payment_receipts`: `id`, `record_id`, `receipt_no`, `tid`, `amount`, `currency`, `payment_date`, `render_data`, `created_by`, `created_at`.
  6. `trading_sales_detention_invoices`: `id`, `record_id`, `invoice_no`, `detention_start`, `detention_end`, `free_days`, `chargeable_days`, `per_day_amount`, `detention_amount`, `security_deposit`, `refund_amount`, `currency`, `manual_fields`, `render_data`, `created_by`, `created_at`, `updated_at`.
- **How Document Status Is Stored**:
  - `TradingSalesDocument` has **no status column** and no "required" / "missing" flag.
  - `TradingSalesForm` tracks completion via `completed_at` (nullable datetime). When `completed=True` is passed to `PUT .../forms/{document_type}`, `completed_at` is set to current UTC datetime (`app/modules/trading_import/service.py#L256`).
- **How `current_stage` Is Computed**:
  - **`current_stage` does NOT exist in the backend**. Grepping `current_stage` returns 0 results.
  - The record uses `status` (`TradingImportRecordStatus`), which is updated via `_refresh_record_status` (`app/modules/trading_import/service.py#L484`):
    - If `freight_invoice` exists: status is not modified (remains `invoiced`, `paid`, or `detention`).
    - If all 3 document forms (`draft_bl`, `house_bl`, `master_bl`) have `completed_at is not None`: status becomes `ready_for_invoice`.
    - If no documents and no forms exist: status is `draft`.
    - Otherwise: status is `in_progress`.
    - Creating a freight invoice sets status to `invoiced`.
    - Creating a payment receipt sets status to `paid`.
    - Upserting a detention invoice sets status to `detention`.
- **Arrival Notice and Delivery Order Support**:
  - **NO backend support**.
  - Document enum only contains `draft_bl`, `house_bl`, and `master_bl`.
  - There is no Arrival Notice model or document type (only `expected_arrival_date` date column on the record).
  - There is no Delivery Order model or document type (only `"LATE_DO"` in freight invoice charge codes).
- **Is Customer Stored as Plain Text**:
  - **YES**. `customer` is a plain string `VARCHAR(180)` column directly on `trading_sales_import_records` (`app/modules/trading_import/model.py#L33`).
- **Upload / Download Storage**:
  - Files are saved on local disk under `{TRADING_IMPORT_DATA_DIR}/records/{record_id}/{document_type}/{uuid}.pdf`.
  - Only PDF format accepted. Max file size default: 25 MB.
  - Download served using `FileResponse` (`app/modules/trading_import/router.py#L122`).

### H. Support for Currencies or Exchange Rates
- **Answer**: **Minimal storage strings only, no FX engine or calculations**.
- **File Evidence**:
  - `TradingSalesPaymentReceipt.currency`: String(10), default `"PKR"` (`app/modules/trading_import/model.py#L186`).
  - `TradingSalesDetentionInvoice.currency`: String(10), default `"PKR"` (`app/modules/trading_import/model.py#L214`).
  - `FreightChargeLine.currency`: String(10), default `"PKR"` (`app/modules/trading_import/schemas.py#L70`).
  - `exchange_rate`: Exists only as a key in `INVOICE_MANUAL_FIELD_KEYS` (`app/modules/trading_import/service.py#L103`) that can be manually passed inside `manual_fields` JSON for freight invoice rendering. There is no currency conversion logic, exchange rate table, or multi-currency aggregation.

### I. Finance, Profit/Loss, or Payment Tracking Beyond Import Payment Receipts
- **Answer**: **NO**.
- **File Evidence**:
  - The module slug `"finance"` is seeded with `is_active=False` and `route=None` (`app/modules/modules/seed.py#L26-L33`).
  - No finance ledger, accounts, revenue, expenses, or profit/loss models exist.
  - Payment tracking is restricted to recording manual payment receipts against freight invoices on trading import records (`TradingSalesPaymentReceipt`).

---

## 7. Quality and Tooling

### 7.1 Test Suite
- **Test Discovery**: Ran Python standard library unittest:
  ```bash
  $ python -m unittest discover
  ----------------------------------------------------------------------
  Ran 0 tests in 0.000s
  NO TESTS RAN
  ```
- **Pytest**: Not installed in environment; no `tests/` directory or `test_*.py` files exist in the repository.

### 7.2 Linting & Formatting Configuration
- **Status**: No configuration files present.
- **Checked**: `.flake8`, `ruff.toml`, `.ruff.toml`, `pyproject.toml`, `.pylintrc`, `black`, `isort`, `.pre-commit-config.yaml` do not exist.

### 7.3 CI/CD Workflows
- **Status**: None present.
- **Checked**: No `.github/workflows`, `.gitlab-ci.yml`, or other CI configuration directories exist.

### 7.4 Known TODOs and FIXMEs
- **Search Command**: `grep -rnE "TODO|FIXME" app/ alembic/`
- **Result**: **0 occurrences found**. There are no TODO or FIXME comments in the code.

---

## 8. UNVERIFIED Items

| Item | Question / Area of Uncertainty | Source File / Artifact Needed to Resolve |
|---|---|---|
| 1. Production Password Reset Flow | The forgot-password endpoint generates a token and returns it directly in the API JSON response (`{"reset_token": "..."}`). How are production users intended to receive password reset tokens without email integration? | `app/modules/auth/service.py#L104-L119`, `app/modules/auth/router.py#L56` (Requires confirmation of whether an external email service will be integrated). |
| 2. Production Domain CORS Settings | `settings.backend_cors_origins` is initialized to `["http://localhost:5173", "http://127.0.0.1:5173", "http://82.112.254.202:3020"]`. Is this overridden in production via `.env`? | `app/core/config.py#L17-L21` |
| 3. Unstructured JSON Form Schema | Form data in `TradingSalesForm.data` accepts arbitrary nested dictionaries. The backend does not enforce a rigid Pydantic schema for BL extraction. Which fields are strictly expected by frontend forms beyond the aliases in `CANONICAL_FIELD_ALIASES`? | `app/modules/trading_import/service.py#L28-L70` |
| 4. Database Column Type Parity (JSON vs JSONB) | Alembic reports autogenerate diffs because migration `d8f1b42c6a90` created `JSONB` columns while SQLAlchemy models declare `sa.JSON`. Does team intend to standardize models to `postgresql.JSONB`? | `app/modules/trading_import/model.py`, `alembic/versions/d8f1b42c6a90_...py` |

---

## 9. Frontend Integration & Planning Summary

### What the Backend Already Has
1. **Full Authentication & Session Context**: JWT login, logout, current user profile (`/auth/me`), permission slug discovery (`/auth/me/access`), change password, and forgot/reset password.
2. **Role & Module RBAC**:
   - Built-in root administrator and standard user roles.
   - Access group management (`/groups`) with arbitrary module assignments.
   - Module registry (`/modules`) listing icons, routes, colors, and active statuses.
3. **Comprehensive Audit Logs**:
   - Queryable via `/activity-logs` with pagination (`page`, `page_size`) and category filters (`important`, `account`, `security`, `auth`, `all`).
4. **Trading Import Sales Workflow**:
   - Record CRUD (`/trading-import/sales/records`).
   - PDF document upload & download for Draft BL, House BL, and Master BL.
   - Form data storage with canonical alias extraction (`canonical_data`).
   - Autocomplete suggestion endpoint aggregating past form inputs (`/suggestions`).
   - Automatic freight invoice calculation and rendering (`/freight-invoice/render` and `/freight-invoice`).
   - Payment receipts logging (`/payment-receipts`).
   - Detention invoice calculation with free days, daily rates, and security deposit deductions (`/detention-invoice`).

### What Is Missing for Customers and Indenting
1. **No Customers Module / Entity**:
   - There is no `customers` table or endpoint.
   - Customer information is strictly a plain-text string on import records (`customer`) and unstructured text in BL form data.
   - Frontend cannot fetch a customer list, autocomplete existing customers from a relational table, or link records to customer IDs.
2. **No Indenting Module**:
   - Zero backend support for Indenting: no indenting inquiries, indenting parties, supplier/buyer commissions, commission deals, or indenting contracts.

### Frontend Expectation Conflicts & Nuances
1. **Permission Slug for Trading Import**:
   - Frontend developers might look for a `"trading"` or `"trading-import"` permission slug.
   - **Conflict**: The database module slug is `"sales"`, and the endpoint dependency specifically requires `"sales"` (`require_trading_import_sales = require_module_access("sales")`).
2. **`current_stage` vs `status`**:
   - Frontend developers expecting a computed `current_stage` property will find none.
   - **Resolution**: Use the record `status` enum (`draft`, `in_progress`, `ready_for_invoice`, `invoiced`, `paid`, `detention`).
3. **Missing Document Types in Trading Import**:
   - Frontend workflows expecting "Arrival Notice" or "Delivery Order" document upload/storage will fail: the backend only supports `draft_bl`, `house_bl`, and `master_bl`.
4. **No Pagination on Primary Entities**:
   - Frontend must not send `page` or `page_size` to `/users`, `/groups`, or `/trading-import/sales/records`. These endpoints return the full dataset as a plain JSON array in `data`. Only `/activity-logs` supports pagination.
5. **No Soft Delete for Records**:
   - Import records cannot be deleted via API (only updated via `PATCH`).
   - Users are not deleted via `DELETE /users/{id}`; they are soft-deactivated (`status='inactive'`).
