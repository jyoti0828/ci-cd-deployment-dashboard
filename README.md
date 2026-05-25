# Flask → Docker → GitHub Actions → AWS EC2

A complete DevOps pipeline: Flask app containerised with Docker, automated CI/CD via GitHub Actions, and optional deployment to AWS EC2.

---

## Project Structure

```
flask-docker-project/
├── app.py                          # Flask application
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Multi-stage Docker build
├── docker-compose.yml              # Local development
├── .dockerignore
├── .gitignore
├── ec2-setup.sh                    # One-time EC2 bootstrap script
└── .github/
    └── workflows/
        └── ci-cd.yml               # GitHub Actions pipeline
```

---

## Step 1 — Run Locally

```bash
# Option A: plain Python
pip install -r requirements.txt
python app.py

# Option B: Docker Compose (recommended)
docker compose up --build
```

Visit → http://localhost:5000  
Health check → http://localhost:5000/health

---

## Step 2 — Dockerize Manually

```bash
# Build
docker build -t flask-docker-app .

# Run
docker run -d -p 5000:5000 --name flask-app flask-docker-app

# Logs
docker logs -f flask-app
```

---

## Step 3 — Push to GitHub

```bash
git init
git add .
git commit -m "feat: flask app with Docker + CI/CD"

# Create a repo on GitHub, then:
git remote add origin https://github.com/<your-username>/flask-docker-project.git
git branch -M main
git push -u origin main
```

---

## Step 4 — GitHub Actions CI/CD

The pipeline (`.github/workflows/ci-cd.yml`) runs automatically on every push to `main`:

| Job | What it does |
|-----|-------------|
| **test** | Installs deps, runs `pytest` |
| **build-and-push** | Builds Docker image, pushes to Docker Hub |
| **deploy** | SSH into EC2, pulls new image, restarts container |

### Required GitHub Secrets

Go to **Settings → Secrets and variables → Actions → New repository secret**:

| Secret | Value |
|--------|-------|
| `DOCKER_HUB_USERNAME` | Your Docker Hub username |
| `DOCKER_HUB_TOKEN` | Docker Hub access token (not password) |
| `EC2_HOST` | Public IP or DNS of your EC2 instance |
| `EC2_USER` | `ubuntu` (Ubuntu) or `ec2-user` (Amazon Linux) |
| `EC2_SSH_KEY` | Contents of your `.pem` private key file |

### Get a Docker Hub token
1. hub.docker.com → Account Settings → Security → New Access Token

---

## Step 5 — Deploy to AWS EC2 (Optional)

### 5a. Launch EC2
- AMI: **Ubuntu 22.04 LTS** or Amazon Linux 2023
- Instance type: `t2.micro` (free tier)
- Security Group — open inbound ports:
  - `22` (SSH) — your IP only
  - `80` (HTTP) — 0.0.0.0/0
- Download the `.pem` key pair

### 5b. Bootstrap the server

```bash
# Copy and run the setup script
scp -i your-key.pem ec2-setup.sh ubuntu@<EC2_IP>:~/
ssh -i your-key.pem ubuntu@<EC2_IP>
chmod +x ec2-setup.sh && sudo ./ec2-setup.sh
```

### 5c. Trigger a deploy

Push any commit to `main` — the Actions pipeline will:
1. Test → Build → Push to Docker Hub → SSH into EC2 → Pull & restart container

Your app will be live at: **http://\<EC2_PUBLIC_IP\>**

---

## Pipeline Flow

```
git push main
     │
     ▼
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Test Job  │────▶│ Build & Push Job  │────▶│   Deploy Job    │
│  (pytest)   │     │ (Docker Hub)      │     │ (SSH → EC2)     │
└─────────────┘     └──────────────────┘     └─────────────────┘
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | `development` | Set to `production` in containers |
| `PORT` | `5000` | Port Flask listens on |

---

## Useful Commands

```bash
# Watch GitHub Actions logs
gh run watch   # requires GitHub CLI

# Check running container on EC2
docker ps
docker logs -f flask-app

# Force re-deploy without a code change
git commit --allow-empty -m "chore: trigger deploy" && git push
```
