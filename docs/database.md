# FoodVision AI — Database Schema & Migration Guide

## 1. Engine & Hosting

* **Database Engine:** PostgreSQL 16
* **Hosting Platform:** Neon Serverless PostgreSQL (AWS `ap-southeast-1`)
* **Connection Pooling:** SQLAlchemy `pool_pre_ping=True` (handles serverless wake-up latency gracefully).

---

## 2. Schema Architecture

### `users` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | PRIMARY KEY | User UUID |
| `email` | `VARCHAR(255)` | UNIQUE, NOT NULL, INDEX | User email |
| `hashed_password`| `VARCHAR(255)` | NOT NULL | Argon2id hash |
| `role` | `VARCHAR(50)` | NOT NULL, DEFAULT 'user'| RBAC role |
| `is_active` | `BOOLEAN` | NOT NULL, DEFAULT TRUE | Account status |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | Creation timestamp |

### `refresh_tokens` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | PRIMARY KEY | Token record UUID |
| `user_id` | `VARCHAR(36)` | FK -> `users.id` (CASCADE) | Owner user UUID |
| `token_hash` | `VARCHAR(255)` | UNIQUE, NOT NULL, INDEX | SHA-256 token digest |
| `parent_token_hash`| `VARCHAR(255)`| NULLABLE | Rotation family parent |
| `expires_at` | `TIMESTAMPTZ` | NOT NULL | Expiration timestamp |
| `revoked` | `BOOLEAN` | NOT NULL, DEFAULT FALSE | Revocation flag |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | Issue timestamp |

### `predictions` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | PRIMARY KEY | Prediction UUID |
| `user_id` | `VARCHAR(36)` | FK -> `users.id` (SET NULL) | Authenticated owner |
| `food_name` | `VARCHAR(255)` | NOT NULL | Top-1 predicted dish |
| `confidence` | `FLOAT` | NOT NULL | Top-1 confidence score |
| `top_5` | `JSON` | NOT NULL | Top-5 predictions & scores |
| `model_version` | `VARCHAR(100)` | NOT NULL | Model identifier |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | Prediction timestamp |

---

## 3. Migration History (Alembic)

* `df8b401f95f6`: Baseline schema (`predictions` table).
* `edd289f98d7b`: Added `users` table, `refresh_tokens` table, and `predictions.user_id` foreign key.
* `<rls_revision_id>`: Enabled PostgreSQL Row-Level Security (RLS) on `predictions`.