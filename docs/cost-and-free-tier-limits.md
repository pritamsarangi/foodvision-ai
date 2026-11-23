# FoodVision AI — Infrastructure Cost & Free-Tier Limits

## 1. Budget Mandate

* **Total Budget Target:** **₹0 / $0**
* **Strict Rule:** No paid cloud services, GPU rentals, or metered APIs without explicit prior approval.

---

## 2. Infrastructure Taxonomy & Service Audit

We strictly separate our stack into three distinct categories:
1. **Open-Source Software (OSS):** Fully self-hostable, source code freely available.
2. **Free Hosted Services:** Proprietary cloud platforms offering a free tier for static hosting or code storage.
3. **Free-Tier Managed Infrastructure:** Hosted third-party servers/databases subject to resource quotas and sleep cycles.

### Detailed Service Audit

| Dimension | Neon PostgreSQL | Cloudflare Static Assets | Render Web Service | GitHub Actions |
| :--- | :--- | :--- | :--- | :--- |
| **Category** | Managed Infrastructure | Free Hosted Service | Managed Infrastructure | Free Hosted CI/CD |
| **Software License** | Proprietary platform over OSS PostgreSQL | Proprietary | Proprietary platform over Docker | Proprietary runner over OSS tools |
| **Can be Self-Hosted?** | No (PostgreSQL can be) | No (Caddy / Nginx can be) | No (Docker / VM can be) | No (Act / self-hosted runners can be) |
| **Free-Tier Allocation** | 0.5 GiB storage, 1 compute branch | 100,000 requests/day, unlimited bandwidth | 750 free instance hours/month, 512 MB RAM | 2,000 free build minutes/month for private repos |
| **Behavior When Limit Reached** | Compute suspended / read-only | Requests throttled or blocked | Service spun down until next month | CI jobs fail / queue disabled |
| **Credit Card Required?** | No | No | No | No |
| **Fully Open-Source Alternative**| Self-hosted PostgreSQL container | Caddy serving static build on a Linux VM | Self-hosted Docker Compose on local hardware / VM | Local Git pre-commit hooks + shell test runners |

---

## 3. Resource & Latency Limits

1. **Render Free Tier Spin-Down:**
   * Inactive web services spin down after 15 minutes of idle time.
   * Cold start latency: 30–50 seconds on initial wake-up.
   * *Mitigation:* The Flutter client displays an informative loading indicator if connection takes longer than 5 seconds.
2. **Neon PostgreSQL Free Tier:**
   * Compute automatically enters sleep mode after 5 minutes of inactivity.
   * Reconnection latency on wake: 1–3 seconds.
   * *Mitigation:* SQLAlchemy configured with `pool_pre_ping=True` to gracefully reconnect without raising broken pipe exceptions.
3. **TensorFlow CPU Memory Footprint:**
   * EfficientNet-B0 fine-tuned weights: ~17 MB on disk.
   * In-memory footprint inside Python: ~180–220 MB RAM.
   * Fits comfortably within 512 MB free-tier RAM limits when using single-process Uvicorn with lazy LRU caching.