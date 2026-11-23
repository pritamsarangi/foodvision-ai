# FoodVision AI — Security Architecture & Threat Model

## 1. Authentication & Identity Controls

### Password Hashing (Argon2id)
* **Algorithm:** Argon2id (OWASP recommended password hashing standard).
* **Parameters:** `time_cost=3`, `memory_cost=64MB`, `parallelism=4`.
* **Defense:** Memory-hardness prevents GPU/ASIC accelerated offline brute-force cracking if the database is leaked.

### JWT Access Tokens
* **Algorithm:** HMAC-SHA256 (`HS256`).
* **Lifespan:** 15 minutes (short-lived).
* **Payload:** Minimal claims (`sub` = user UUID, `role` = user/admin, `iat`, `exp`).
* **Transport:** Sent via HTTP `Authorization: Bearer <token>` header.

### Rotating Refresh Tokens & Reuse Detection
* **Lifespan:** 7 days.
* **Storage:** Refresh tokens are hashed using SHA-256 before storage in the `refresh_tokens` table. Plaintext tokens are never stored in the database.
* **Rotation:** When a refresh token is used at `/api/v1/auth/refresh`, it is marked as `revoked = True` and a new token pair is issued.
* **Reuse Detection (Family Revocation):** If an attacker attempts to replay an already-revoked refresh token, the server detects token theft, immediately revokes **all** active tokens for that user, and returns `HTTP 401 Unauthorized`.

---

## 2. Multi-Tenant Authorization & Row-Level Security (RLS)

FoodVision AI enforces a two-layer defense-in-depth model for user data:

### Layer 1: Application-Level Scoping
* All prediction queries in `backend/app/api/predict.py` filter by the authenticated user's ID:
  ```python
  query = select(Prediction).where(Prediction.user_id == current_user.id)
  ```

### Layer 2: Database-Level Row-Level Security (RLS)
* Enabled on the `predictions` table via PostgreSQL:
  ```sql
  ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;
  ALTER TABLE predictions FORCE ROW LEVEL SECURITY;
  ```
* Context is injected per transaction using `SET LOCAL app.current_user_id = :uid`.
* Because `SET LOCAL` is transaction-scoped, it safely prevents context leakage across pooled connections (Neon connection pooler).

---

## 3. Edge & Network Protections

* **Reverse Proxy (Caddy):** Rejects uploads $> 10\text{ MB}$ before the payload reaches Python memory.
* **CORS Restrictions:** Whitelists only approved frontend origins (`FRONTEND_CORS_ORIGINS`).
* **Security Headers:** Enforces `nosniff`, `DENY` clickjacking framing, and `strict-origin`.
* **Zero Host Exposure:** Port 8000 is internal-only; only Caddy is exposed on port 80/443.