# Monitoring

This directory contains Grafana dashboard configurations for monitoring ASR-API.

## Grafana Dashboard

### Import Dashboard

1. Open Grafana UI
2. Go to **Dashboards** → **Import**
3. Upload `grafana-dashboard.json` or paste its contents
4. Select your Prometheus data source
5. Click **Import**

### Dashboard Panels

1. **API Calls Rate** - Shows requests per second over time
2. **P99 Latency** - Shows P99, P95, and P50 latency percentiles over time
3. **Total API Calls** - Cumulative request count
4. **HTTP Status Codes** - Request rate by HTTP status code

### Prometheus Queries Used

- **Request Rate**: `rate(http_server_duration_milliseconds_count{service="asr-api"}[5m])`
- **P99 Latency**: `histogram_quantile(0.99, sum(rate(http_server_duration_milliseconds_bucket{service="asr-api"}[5m])) by (le))`
- **P95 Latency**: `histogram_quantile(0.95, sum(rate(http_server_duration_milliseconds_bucket{service="asr-api"}[5m])) by (le))`
- **P50 Latency**: `histogram_quantile(0.50, sum(rate(http_server_duration_milliseconds_bucket{service="asr-api"}[5m])) by (le))`

### Requirements

- Prometheus data source configured in Grafana
- Prometheus scraping ASR-API service (configured via ServiceMonitor or Service annotations)
- Service label: `service="asr-api"`

