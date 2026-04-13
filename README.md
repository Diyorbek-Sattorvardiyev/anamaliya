# NetSentinel AI: Real-Time Network Anomaly Detection Platform

Full-stack system for real-time network anomaly detection using FastAPI, SQLite, Celery, Isolation Forest, and a CPU-friendly autoencoder built with scikit-learn.

## 1. Architecture

- Backend: FastAPI + SQLAlchemy (clean architecture: API -> service -> repository -> DB)
- Database: SQLite (`users`, `traffic_logs`, `anomaly_results`, `alerts`)
- Queue/Tasks: Celery in eager/local-memory mode for simple local runs
- Background jobs: Celery workers
- ML models:
1. Isolation Forest (unsupervised)
2. Autoencoder (CPU-friendly `MLPRegressor`)
- Frontend: HTML/CSS/JS + Chart.js
- Alert channels: web notifications + email via SMTP

## 2. Project Structure

```text
.
├── app.py
├── .env.example
├── backend
│   ├── requirements.txt
│   ├── app
│   │   ├── main.py
│   │   ├── api/routes
│   │   ├── core
│   │   ├── db
│   │   ├── ml
│   │   ├── repositories
│   │   ├── schemas
│   │   ├── services
│   │   ├── utils
│   │   └── workers
│   └── tests
├── frontend
│   ├── index.html
│   ├── css/styles.css
│   └── js/app.js
└── scripts
    ├── simulate_traffic.py
    └── evaluate_models.py
```

## 3. Core Features Implemented

### Data ingestion
- `POST /traffic/ingest` accepts packet events or simulated traffic.
- Input includes source/destination IP, protocol, packet size, time interval, request frequency.
- Optional asynchronous ingestion via Celery queue.

### Feature engineering
- Numerical protocol encoding
- Time-based cyclic features (`hour_sin`, `hour_cos`)
- Throughput estimate (`bytes_per_second`)
- Standard scaling before model inference

### AI models
- Isolation Forest trained on normal traffic
- CPU-friendly autoencoder (`scikit-learn` `MLPRegressor`) trained on normal traffic reconstruction
- Ensemble anomaly score from both models

### Real-time detection
- Ingested packets are scored and stored in DB
- Results are persisted in `anomaly_results`
- Alerts auto-trigger on threshold breach

### Dashboard
- Live traffic chart
- Anomaly timeline
- Protocol distribution chart
- Risk heatmap
- Top suspicious IP list
- Alert stream

### Alerts
- Web alerts in dashboard
- Email alerts through Celery background task

### Security
- JWT authentication
- Input validation (Pydantic)
- Rate limiting via `slowapi`

## 4. Database Design

### `users`
- `id` (PK), `email` (unique,index), `full_name`, `hashed_password`, `role`, `created_at`

### `traffic_logs`
- `id` (PK), `src_ip` (index), `dst_ip` (index), `protocol` (index), `packet_size`, `interval_ms`, `request_frequency`, `timestamp` (index)
- Composite indexes: `(src_ip, timestamp)`, `(dst_ip, timestamp)`

### `anomaly_results`
- `id` (PK), `traffic_log_id` (FK), `model_name` (index), `anomaly_score`, `is_anomaly` (index), `detected_at` (index)
- Composite index: `(model_name, detected_at)`

### `alerts`
- `id` (PK), `anomaly_result_id` (FK), `user_id` (FK nullable), `severity` (index), `channel`, `message`, `status`, `created_at` (index)
- Composite index: `(status, created_at)`

## 5. API Endpoints

Works both with and without `/api/v1` prefix.

- `POST /traffic/ingest`
- `GET /traffic/live`
- `GET /anomalies`
- `POST /train-model`
- `GET /alerts`
- `POST /auth/login`

## 6. Local Run

```bash
cd /home/diyorbek/Downloads/network_anomaly_project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Open:
- API docs: http://127.0.0.1:8000/docs
- Dashboard: http://127.0.0.1:8000/

Default seeded account:
- Email: `admin@netsentinel.local`
- Password: `Admin12345`

## 7. Model Training and Evaluation

### Train models from API

```bash
curl -X POST http://localhost:8000/train-model \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"samples":7000,"epochs":20}'
```

### Simulate mixed normal + DDoS traffic

```bash
PYTHONPATH=backend python scripts/simulate_traffic.py
```

### Offline evaluation (accuracy/precision/recall)

```bash
PYTHONPATH=backend python scripts/evaluate_models.py
```

## 8. Testing

```bash
PYTHONPATH=backend pytest backend/tests -q
```

## 9. Notes for Production Hardening

- Replace synthetic traffic with live PCAP ingestion (`app/utils/pcap.py`) or streaming collector.
- Store model versions and metadata in a model registry.
- Add migration workflow (Alembic revisions).
- Add SIEM integration (Kafka/Elastic/Splunk).
- If you later move away from SQLite, add a production-grade database service.
- Restrict CORS and rotate JWT secret.
- Add per-user RBAC policies and audit logs.
