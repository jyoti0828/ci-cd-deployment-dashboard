# CI/CD Deployment Dashboard

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.x-black?logo=flask)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF?logo=github-actions)
![AWS EC2](https://img.shields.io/badge/AWS-EC2-FF9900?logo=amazonaws)

---

## Overview

A complete end-to-end DevOps project built to demonstrate a production-grade CI/CD pipeline. The project is a lightweight Flask REST API containerised with Docker, automatically tested and built via GitHub Actions, and deployed to an AWS EC2 instance. A static deployment status page is also published to AWS S3 (with optional CloudFront distribution) on every successful pipeline run.

This project serves as a practical reference for anyone learning or implementing modern DevOps practices — from local development all the way to cloud deployment.

---

## Features

- **REST API with Flask** — JSON endpoints for home and health check routes
- **Dockerised application** — multi-stage Dockerfile for clean, reproducible builds
- **Docker Compose** — one-command local development environment
- **Automated CI/CD** — four-job GitHub Actions pipeline triggered on every push to `main`
- **Docker Hub integration** — images tagged with `latest` and commit SHA on every build
- **AWS EC2 deployment** — zero-downtime container replacement via SSH from the pipeline
- **S3 status page** — static deployment dashboard auto-deployed to S3 on every run
- **Optional CloudFront CDN** — cache invalidation step included for CDN-backed deployments
- **Environment-aware** — `APP_ENV` toggles debug mode; configurable port via `PORT`
- **Health endpoint** — `/health` returns `{"status": "healthy"}` for monitoring integrations

---

## Architecture / Workflow Diagram

```
Developer Machine
      │
      │  git push origin main
      ▼
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Actions                          │
│                                                             │
│  ┌──────────┐    ┌──────────────────┐    ┌──────────────┐  │
│  │  test    │───▶│ build-and-push   │───▶│ deploy-ec2   │  │
│  │ (pytest) │    │ (Docker Hub)     │    │ (SSH → EC2)  │  │
│  └──────────┘    └──────────────────┘    └──────────────┘  │
│        │                                                    │
│        └──────────────────────────────────────────────────▶│
│                    ┌──────────────────────┐                 │
│                    │ deploy-status-page   │                 │
│                    │ (S3 + CloudFront)    │                 │
│                    └──────────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
                              │                      │
                              ▼                      ▼
                      ┌─────────────┐     ┌──────────────────┐
                      │  Docker Hub │     │   AWS EC2        │
                      │  Registry   │────▶│  flask-app:80    │
                      └─────────────┘     └──────────────────┘
                                                    │
                                          ┌─────────────────┐
                                          │    AWS S3       │
                                          │  Status Page    │
                                          └─────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Application** | Python 3.12, Flask |
| **Containerisation** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions |
| **Container Registry** | Docker Hub |
| **Cloud Compute** | AWS EC2 (Ubuntu 22.04 LTS) |
| **Static Hosting** | AWS S3 (+ optional CloudFront) |
| **Testing** | pytest |
| **Infrastructure Scripts** | Bash (`ec2-setup.sh`) |

---

## Project Structure

```
ci-cd-deployment-dashboard/
├── app.py                    # Flask application (home + health routes)
├── requirements.txt          # Python dependencies
├── Dockerfile                # Multi-stage Docker build
├── docker-compose.yml        # Local development environment
├── ec2-setup.sh              # One-time EC2 bootstrap script
├── ci-cd.yml                 # GitHub Actions pipeline definition
├── .gitignore.txt            # Git ignore rules
└── files/                    # Supporting assets
```

---

## CI/CD Pipeline Flow

Every `git push` to `main` (or pull request targeting `main`) triggers the following four-job pipeline:

```
git push main
      │
      ▼
┌─────────────┐
│  Job 1      │  Run Tests (pytest)
│   test      │  → Installs deps, runs pytest -v
└──────┬──────┘
       │
       ├────────────────────────────────────────┐
       ▼                                        ▼
┌──────────────────┐                 ┌──────────────────────┐
│  Job 2           │                 │  Job 3               │
│  build-and-push  │                 │  deploy-status-page  │
│  → Docker Hub    │                 │  → AWS S3            │
└──────┬───────────┘                 └──────────────────────┘
       │
       ▼
┌─────────────────┐
│  Job 4          │  SSH into EC2
│  deploy-ec2     │  → docker pull → docker stop → docker run
└─────────────────┘
```

Jobs 2 and 3 run in parallel after Job 1 passes. Job 4 only runs after Job 2 succeeds. All deployment jobs only execute on pushes to `main` (not on pull requests).

---

## Local Setup

### Prerequisites

- Python 3.12+
- pip
- Docker and Docker Compose (for containerised setup)
- Git

### Run Locally

**Option A — Plain Python**

```bash
# Clone the repository
git clone https://github.com/jyoti0828/ci-cd-deployment-dashboard.git
cd ci-cd-deployment-dashboard

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

**Option B — Docker Compose (recommended)**

```bash
docker compose up --build
```

Once running, visit:

- **Home:** `http://localhost:5000`
- **Health check:** `http://localhost:5000/health`

---

## Docker Setup

### Build Docker Image

```bash
docker build -t flask-docker-app .
```

### Run Docker Container

```bash
docker run -d \
  -p 5000:5000 \
  --name flask-app \
  -e APP_ENV=production \
  flask-docker-app
```

**Check the logs:**

```bash
docker logs -f flask-app
```

**Stop and remove the container:**

```bash
docker stop flask-app && docker rm flask-app
```

---

## GitHub Actions CI/CD

### Pipeline Stages

| Job | Trigger | What it does |
|---|---|---|
| `test` | Every push / PR to `main` | Sets up Python 3.12, installs deps, runs `pytest -v` |
| `build-and-push` | After `test` passes, `main` branch only | Logs into Docker Hub, builds image with Buildx (GHA cache), pushes `latest` and `<sha>` tags |
| `deploy-status-page` | After `test` passes, `main` branch only | Configures AWS credentials, uploads `status.html` to S3, optionally invalidates CloudFront distribution |
| `deploy-ec2` | After `build-and-push` passes, `main` branch only | SSHes into EC2, pulls latest image, stops/removes old container, starts new container on port 80 |

### Required GitHub Secrets

Navigate to **Settings → Secrets and variables → Actions → New repository secret** and add the following:

| Secret | Description |
|---|---|
| `DOCKER_HUB_USERNAME` | Your Docker Hub username |
| `DOCKER_HUB_TOKEN` | Docker Hub access token (not your account password) |
| `EC2_HOST` | Public IP address or DNS hostname of your EC2 instance |
| `EC2_USER` | SSH username — `ubuntu` for Ubuntu AMI, `ec2-user` for Amazon Linux |
| `EC2_SSH_KEY` | Full contents of your `.pem` private key file |
| `AWS_ACCESS_KEY_ID` | AWS IAM access key with S3 and CloudFront permissions |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret access key |
| `AWS_REGION` | AWS region where your S3 bucket lives (e.g. `us-east-1`) |
| `S3_BUCKET_NAME` | Name of the S3 bucket for the status page |
| `CLOUDFRONT_DISTRIBUTION_ID` | *(Optional)* CloudFront distribution ID for cache invalidation |

**To generate a Docker Hub access token:**
Docker Hub → Account Settings → Security → Access Tokens → New Access Token

---

## AWS EC2 Deployment

### Launch EC2 Instance

1. Open the AWS Console and navigate to **EC2 → Launch Instance**
2. Choose **Ubuntu Server 22.04 LTS** AMI
3. Select instance type **t2.micro** (eligible for free tier)
4. Create or select a key pair — download the `.pem` file and keep it safe
5. Proceed to configure the security group (see below)

### Configure Security Groups

In the security group settings, add the following inbound rules:

| Type | Port | Source | Purpose |
|---|---|---|---|
| SSH | 22 | Your IP only | Secure remote access |
| HTTP | 80 | 0.0.0.0/0 | Public web traffic |

### Bootstrap Server

Copy the setup script to the EC2 instance and run it once to install Docker:

```bash
# Copy the setup script
scp -i your-key.pem ec2-setup.sh ubuntu@<EC2_PUBLIC_IP>:~/

# SSH into the instance
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>

# Make executable and run
chmod +x ec2-setup.sh
sudo ./ec2-setup.sh
```

This script installs Docker and any other required dependencies on the instance.

### Deploy Application

After bootstrapping, deployment is fully automated. Every push to `main` will:

1. Run tests
2. Build and push a new Docker image to Docker Hub
3. SSH into EC2 and execute:

```bash
docker pull <DOCKER_HUB_USERNAME>/flask-docker-app:latest
docker stop flask-app || true
docker rm flask-app || true
docker run -d \
  --name flask-app \
  --restart unless-stopped \
  -p 80:5000 \
  -e APP_ENV=production \
  <DOCKER_HUB_USERNAME>/flask-docker-app:latest
docker image prune -f
```

Your application will then be live at: **`http://<EC2_PUBLIC_IP>`**

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | Set to `production` to disable Flask debug mode |
| `PORT` | `5000` | Port that Flask listens on |

In Docker, these are passed via the `-e` flag at runtime or defined in `docker-compose.yml`.

---

## Screenshots / Demo

> [Add screenshots here after running the project. Suggested captures are listed below.]

### Application Running

```
# Expected response from http://localhost:5000
{
  "message": "Hello from Flask + Docker!",
  "host": "<container-hostname>",
  "env": "development"
}
```

[_Add a screenshot of the browser or curl output here._]

### Docker Container Running

```bash
docker ps
# Expected output:
# CONTAINER ID   IMAGE             COMMAND       STATUS        PORTS
# abc123def456   flask-docker-app  "python ..."  Up X minutes  0.0.0.0:5000->5000/tcp
```

[_Add a screenshot of `docker ps` output here._]

### GitHub Actions Workflow

[_Add a screenshot of a successful GitHub Actions run showing all four jobs passing (green checkmarks)._]

### EC2 Deployment

[_Add a screenshot of the Flask app accessible via the EC2 public IP in a browser._]

---

## Challenges Faced

- **GitHub Actions workflow file location** — GitHub requires workflow files to be placed inside `.github/workflows/`. Keeping `ci-cd.yml` in the repo root means it must be referenced or moved before the pipeline will trigger correctly.
- **SSH key formatting in secrets** — the entire contents of the `.pem` file (including headers and newlines) must be pasted into the `EC2_SSH_KEY` secret exactly as-is.
- **Docker Hub token vs password** — GitHub Actions requires a Docker Hub *access token* rather than an account password for authentication.
- **Port mapping** — the Flask app runs on port `5000` inside the container but is mapped to port `80` on EC2 so it is accessible over standard HTTP without specifying a port in the URL.
- **Container restart on redeploy** — the deploy script uses `|| true` to gracefully handle the case where no container is running yet on the first deployment.
- **S3 static website hosting** — the bucket must have public access enabled and static website hosting configured for the status page to be accessible over HTTP.

---

## Key DevOps Concepts Demonstrated

- **Continuous Integration (CI)** — automated testing on every push and pull request prevents broken code from reaching production
- **Continuous Deployment (CD)** — every successful merge to `main` automatically ships a new container to EC2
- **Infrastructure as Code** — the entire pipeline is defined in YAML; EC2 setup is scripted in `ec2-setup.sh`
- **Immutable Infrastructure** — each deployment pulls a fresh Docker image tagged with the commit SHA; old containers are replaced, not patched
- **Secret Management** — all credentials are stored as GitHub Actions secrets and never appear in source code
- **Multi-job pipeline with dependencies** — `needs:` ensures jobs run in the correct order and failed tests block deployment
- **Docker layer caching** — GitHub Actions cache (`type=gha`) speeds up repeated builds
- **Health checks** — the `/health` endpoint provides a standard integration point for load balancers and monitoring tools

---

## Future Improvements

- [ ] Move `ci-cd.yml` to `.github/workflows/ci-cd.yml` to follow GitHub Actions convention
- [ ] Add a `pytest` test file with meaningful test cases for each Flask route
- [ ] Integrate container health checks in `docker-compose.yml`
- [ ] Add Terraform or AWS CDK scripts to provision EC2 and S3 infrastructure automatically
- [ ] Set up an Application Load Balancer (ALB) with HTTPS via AWS Certificate Manager
- [ ] Add Slack or email notifications on pipeline failure
- [ ] Implement semantic versioning and Git tags for Docker image tagging
- [ ] Add a staging environment that deploys on pull requests before merging to `main`
- [ ] Integrate a vulnerability scanner (e.g. Trivy) into the build step
- [ ] Use Amazon ECR instead of Docker Hub as the private container registry

---

## Useful Commands

```bash
# ── Local Development ──────────────────────────────────────────────────────────

# Run with Docker Compose
docker compose up --build

# Run tests locally
pip install pytest && pytest -v

# ── Docker ────────────────────────────────────────────────────────────────────

# Build image manually
docker build -t flask-docker-app .

# Run container locally
docker run -d -p 5000:5000 --name flask-app flask-docker-app

# Follow container logs
docker logs -f flask-app

# Stop and remove container
docker stop flask-app && docker rm flask-app

# Remove unused images
docker image prune -f

# ── GitHub Actions ────────────────────────────────────────────────────────────

# Watch pipeline in the terminal (requires GitHub CLI)
gh run watch

# Force a deploy without a code change
git commit --allow-empty -m "chore: trigger deploy" && git push

# ── EC2 ───────────────────────────────────────────────────────────────────────

# SSH into EC2 instance
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>

# Check running containers on EC2
docker ps

# Follow app logs on EC2
docker logs -f flask-app

# ── AWS CLI ───────────────────────────────────────────────────────────────────

# Manually sync status page to S3
aws s3 cp status.html s3://<BUCKET_NAME>/index.html --content-type "text/html"

# Invalidate CloudFront cache manually
aws cloudfront create-invalidation \
  --distribution-id <DISTRIBUTION_ID> \
  --paths "/*"
```

---

## Learning Outcomes

By building and running this project you will gain hands-on experience with:

- Writing a **Dockerfile** and understanding multi-stage builds
- Using **Docker Compose** for local development orchestration
- Designing a **multi-job GitHub Actions workflow** with job dependencies, conditional execution, and secret injection
- Authenticating GitHub Actions with **Docker Hub** and **AWS** using repository secrets
- Provisioning and configuring an **AWS EC2** instance (security groups, key pairs, SSH access)
- Running a **zero-downtime container replacement** on a remote server via SSH
- Hosting a static page on **AWS S3** and optionally distributing it with **CloudFront**
- Applying **environment variables** to control application behaviour across dev and prod
- Understanding the full **developer → CI → registry → cloud** delivery lifecycle

---

## Author

**Jyoti** — [@jyoti0828](https://github.com/jyoti0828)

If you found this project useful, consider giving it a ⭐ on [GitHub](https://github.com/jyoti0828/ci-cd-deployment-dashboard)!
