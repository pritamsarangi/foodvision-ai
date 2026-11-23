# FoodVision AI — System Architecture

## 1. System Overview

FoodVision AI is an end-to-end food image classification platform designed to identify 270 food categories from uploaded photographs using a fine-tuned EfficientNet-B0 deep learning model.

The platform is designed to operate within a strict **₹0 / $0 infrastructure budget**, utilizing open-source software, free-tier cloud resources, and local hardware.


## 2. Infrastructure & Single Point of Failure (SPOF) Disclosure

> [!WARNING]
> This architecture is deployed on a **single container/VM instance**. It is **not** highly available (HA). A failure of the host machine, container engine, or upstream cloud network will cause service downtime. True high availability requires multi-region redundancy and database replica failover, which is not feasible under a $0 free-tier budget.

## 3. Implementation Capability Status

| Capability | Current Status | Verification Method |
| :--- | :--- | :--- |
| **Flutter Web UI** | Implemented | Deployed live on Cloudflare Workers Static Assets |
| **EfficientNet-B0 Inference** | Implemented | 80.37% Top-1, 94.30% Top-5 accuracy; verified CPU inference |
| **FastAPI Backend** | Implemented | 23/23 unit tests passing (`backend/tests/`) |
| **Centralized Config** | Implemented | Validated via `backend/app/core/config.py` |
| **Liveness & Readiness Probes** | Implemented | Tested via `/api/v1/health/live` and `/ready` |
| **Database Migrations (Alembic)**| Implemented | Managed via `backend/alembic/` (migrations applied to Neon) |
| **User Authentication & JWT** | Implemented | Argon2id + rotating refresh tokens + reuse detection |
| **PostgreSQL RLS** | Implemented | Defense-in-depth row isolation verified via unit tests |
| **Caddy Reverse Proxy** | Foundation Configured | `infrastructure/caddy/Caddyfile` and `compose.yaml` |
| **Valkey Rate Limiting** | Planned | Phase 3 |
| **Structured JSON Logging** | Planned | Phase 4 |
| **Automated Backups & Restore Drill** | Planned | Phase 4 |
| **Uptime Kuma Monitoring** | Planned | Phase 4 |

## 4. Request Lifecycle

1. **Client Request:** The user selects an image in Flutter Web.
2. **Edge Ingestion:** Caddy receives the request on port 80/443, verifies the payload is under 10MB, adds security headers, and proxies the stream to `api:8000`.
3. **API Validation:** FastAPI checks MIME type (`image/jpeg`, `image/png`, `image/webp`) and enforces byte-length bounds.
4. **Inference Execution:** Image bytes are decoded into a $224 \times 224$ float32 NumPy array and passed to the cached EfficientNet-B0 model via `run_in_threadpool` to prevent blocking the event loop.
5. **Persistence:** The Top-5 categories with confidences are recorded in PostgreSQL asynchronously.
6. **Response:** A JSON payload containing the `prediction_id`, top-1 category, confidence, and top-5 breakdown is returned to the client.