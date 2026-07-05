# QuickPoll — 3-Tier App for Practicing on kind

A polling app built specifically to practice deploying a 3-tier
application to a **kind** (Kubernetes-in-Docker) cluster: no cloud
account needed, everything runs on your own machine.

## How it works

```
Browser
   |
   v
Ingress (ingress-nginx, reachable at http://localhost)
   |
   v
presentation (nginx, :8080)
   |  serves the UI directly
   |  proxies /api/* and /health internally to ->
   v
application (Flask, :5000)
   |
   v
mysql (StatefulSet, :3306, persistent volume)
```

- **Tier 1 — Presentation** (`presentation/`): static HTML/CSS/JS. Its nginx
  does double duty — it serves the UI *and* silently proxies `/api/*` calls
  to the Application tier. That means the browser only ever talks to ONE
  origin, so there's zero CORS configuration anywhere in this stack.
- **Tier 2 — Application** (`application/`): a Flask API, split into
  `logic.py` (pure functions - percentage math, validation, no Flask/SQL)
  and `data_access.py` (SQL only, no business rules). `app.py`'s routes are
  thin - they just call one, then the other.
- **Tier 3 — Data** (`data/schema.sql`): MySQL, two tables (`polls`,
  `poll_options`). No logic here at all.

### The "basic logic" in this app
Open `application/logic.py`:
- `compute_results` — turns raw vote counts into percentages and figures out which option is "leading" (`max()` + a comparison)
- `validate_poll_input` — several conditions chained together (question non-empty, at least 2 options, no empty option text, max 8 options)

## Folder structure
```
quickpoll-app/
├── presentation/
│   ├── index.html, style.css, app.js, config.js
│   ├── nginx.conf        <- serves UI + proxies /api to application
│   └── Dockerfile
├── application/
│   ├── app.py, logic.py, data_access.py, config.py
│   ├── requirements.txt
│   └── Dockerfile
├── data/
│   └── schema.sql
├── k8s/
│   ├── 00-namespace.yaml
│   ├── 01-configmap.yaml
│   ├── 02-secret.yaml
│   ├── 03-mysql-init-configmap.yaml
│   ├── 04-mysql-statefulset.yaml   <- persistent volume via kind's built-in storage class
│   ├── 05-application-deployment.yaml
│   ├── 06-presentation-deployment.yaml
│   └── 07-ingress.yaml
├── kind-config.yaml                 <- maps host ports 80/443 into the cluster
├── docker-compose.yml               <- optional: test locally before kind
└── .env.example
```

---

## Step-by-step: deploy to kind

### 0. Install prerequisites
- [Docker](https://docs.docker.com/get-docker/) (kind runs cluster nodes as Docker containers)
- [kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

Verify:
```bash
docker --version
kind --version
kubectl version --client
```

### 1. (Optional but recommended) Test locally with docker-compose first
This confirms the app itself works before you add Kubernetes into the mix:
```bash
cp .env.example .env
docker compose up --build
```
Visit **http://localhost:8080** — vote on a poll, create one. Once you're
happy, `docker compose down` and move on to kind.

### 2. Create the kind cluster
```bash
kind create cluster --name quickpoll --config kind-config.yaml
kubectl cluster-info --context kind-quickpoll
```

### 3. Install ingress-nginx (kind's official recipe)
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml


### 4. Build the two application images
```bash
docker build -t quickpoll-application:latest ./application
docker build -t quickpoll-presentation:latest ./presentation
```

### 5. Load the images into the kind cluster
kind doesn't pull from a registry by default — you load locally-built
images directly into its nodes:
```bash
kind load docker-image quickpoll-application:latest --name quickpoll
kind load docker-image quickpoll-presentation:latest --name quickpoll
```

### 6. Apply the Kubernetes manifests
```bash
kubectl apply -f k8s/
```
(The filename prefixes `00-`, `01-`, etc. keep them applied in the right order.)

Watch everything come up:
```bash
kubectl get pods -n quickpoll -w
```
Press Ctrl+C once all pods show `Running` and `1/1` or `2/2` Ready.

### 7. Open the app
**http://localhost** — no port-forward needed, because `kind-config.yaml`
already mapped the cluster's ingress to your host's port 80.

### 8. Try the "basic logic" exercise
Open `application/logic.py`, change `validate_poll_input` to require at
least 3 options instead of 2. Rebuild and reload just that one image:
```bash
docker build -t quickpoll-application:latest ./application
kind load docker-image quickpoll-application:latest --name quickpoll
kubectl rollout restart deployment/application -n quickpoll
```
Notice you never touched `presentation/` or the k8s YAML for the other
tiers — that's the point of keeping tiers (and their manifests) separate.

## 9. Try Canary Deployment

I have created two HTML pages, so I will build two separate Docker images:

- `stable-presentation` → Stable version (v1)
- `canary-presentation` → Canary version (v2)

These represent two versions of the same application:
- Stable handles most of the traffic
- Canary is used to test new changes

Run commands -

```bash
docker build -t quickpoll-presentation:latest ./presentation
docker build -t quickpoll-presentation-canary:latest ./presentation

#Load images in kind cluster => quickpoll cluster

kind load docker-image quickpoll-presentation:latest --name quickpoll
kind load docker-image quickpoll-presentation-canary:latest --name quickpoll
```
Deploy or re-apply the rollout deployments, then access the website. You should observe that the same version appears for several refreshes, and occasionally (e.g., every 5–6 requests), a different version is served, indicating canary traffic distribution.


## Useful commands while practicing
```bash
kubectl get all -n quickpoll                     # see everything at once
kubectl logs -f deployment/application -n quickpoll
kubectl describe pod <pod-name> -n quickpoll     # debug a stuck/crashing pod
kubectl exec -it mysql-0 -n quickpoll -- mysql -u root -p polldb
kubectl port-forward svc/application 5000:5000 -n quickpoll   # bypass ingress to test the API directly
```

## Cleanup
```bash
kind delete cluster --name quickpoll
```
