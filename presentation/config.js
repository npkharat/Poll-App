// TIER 1: PRESENTATION LAYER — CONFIG
// ============================================================
// - Local docker-compose: application tier published on localhost:5000
// - kind cluster: both tiers are routed through the same ingress-nginx
//   origin, so use "" (relative/same-origin requests) - see k8s/06-ingress.yaml
const API_BASE_URL = "";


