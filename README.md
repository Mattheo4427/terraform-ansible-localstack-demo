# Todo App with Terraform & LocalStack

A simple Todo application demonstrating **Infrastructure as Code (IaC)** using Terraform with LocalStack to simulate AWS services locally.

## Purpose

This project showcases how to:
- Use **Terraform** to provision AWS resources locally
- Simulate **AWS DynamoDB** using **LocalStack** (free tier)
- Build a full-stack application with **Flask** (Python)
- Use **Nginx** as a reverse proxy / load balancer
- Orchestrate everything with **Docker Compose**

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Compose                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Client (Browser)                                              │
│        │                                                        │
│        ▼ :80                                                    │
│   ┌─────────┐                                                   │
│   │  Nginx  │  (Load Balancer / Reverse Proxy)                  │
│   └────┬────┘                                                   │
│        │                                                        │
│        ├── /api/* ──────▶ ┌──────────┐                          │
│        │                  │ Backend  │ Flask :5000              │
│        │                  └────┬─────┘                          │
│        │                       │                                │
│        │                       ▼                                │
│        │                  ┌────────────┐                        │
│        │                  │ LocalStack │ :4566                  │
│        │                  │ (DynamoDB) │                        │
│        │                  └────────────┘                        │
│        │                       ▲                                │
│        │                       │                                │
│        │                  ┌────┴─────┐                          │
│        │                  │Terraform │ (provisions table)       │
│        │                  └──────────┘                          │
│        │                                                        │
│        └── /* ──────────▶ ┌──────────┐                          │
│                           │ Frontend │ Flask :3000              │
│                           └──────────┘                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Component | Technology | Role |
|-----------|------------|------|
| **Infrastructure** | Terraform | Provisions DynamoDB on LocalStack |
| **Cloud Simulation** | LocalStack | Emulates AWS locally (DynamoDB) |
| **Load Balancer** | Nginx | Reverse proxy, routes `/api` vs `/` |
| **Backend** | Flask (Python) | REST API for todos |
| **Frontend** | Flask + HTML/JS/CSS | User interface |
| **Containerization** | Docker Compose | Service orchestration |

## Project Structure

```
terraform-local-aws-demo/
├── docker-compose.yml          # Service orchestration
├── nginx/
│   └── nginx.conf              # Reverse proxy configuration
├── terraform/
│   ├── provider.tf             # AWS/LocalStack configuration
│   ├── database.tf             # DynamoDB table definition
│   └── outputs.tf              # Terraform outputs
├── backend/
│   ├── Dockerfile
│   ├── main.py                 # Flask REST API
│   ├── requirements.txt
│   ├── .env
│   ├── .env.template
│   └── app/                    # Additional backend modules
└── frontend/
    ├── Dockerfile
    ├── app.py                  # Flask UI server
    ├── requirements.txt
    ├── .env
    ├── .env.template
    ├── templates/
    │   └── index.html
    └── static/
        ├── app.js
        └── style.css
```

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Git

### Run the application

```bash
# Clone the repository
git clone <repository-url>
cd terraform-local-aws-demo

# Start all services
docker-compose up --build
```

### Access the application

- **Frontend**: http://localhost:80
- **API**: http://localhost:80/api/todos
- **LocalStack**: http://localhost:4566

## Startup Order

1. **LocalStack** → Starts and waits for healthcheck
2. **Terraform** → Creates DynamoDB table `todo`
3. **Backend** → Starts after Terraform completes
4. **Frontend** → Starts after Backend
5. **Nginx** → Starts after Backend + Frontend

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/todos` | List all todos |
| `POST` | `/api/todos` | Create a new todo |
| `PUT` | `/api/todos/<id>` | Update a todo |
| `DELETE` | `/api/todos/<id>` | Delete a todo |

## Terraform Resources

| Resource | Description |
|----------|-------------|
| `aws_dynamodb_table.todo_table` | DynamoDB table with `id` as partition key |

## LocalStack Limitations

This project uses **LocalStack Community (free)** which supports:
- DynamoDB
- S3
- SQS, SNS
- Lambda

Not supported (requires Pro):
- ELBv2 (Application Load Balancer)
- RDS
- ECS/EKS

That's why we use **Nginx** instead of AWS ALB for load balancing.

## Cleanup

```bash
# Stop and remove all containers
docker-compose down -v

# Remove Terraform state (if needed)
rm -f terraform/terraform.tfstate terraform/terraform.tfstate.backup
```

## License

MIT
