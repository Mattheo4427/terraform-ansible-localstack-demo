# Todo App with Terraform, Ansible & LocalStack

A simple Todo application demonstrating **Infrastructure as Code (IaC)** using Terraform and **Configuration Management** with Ansible, all running on LocalStack to simulate AWS services locally.

## Purpose

This project showcases how to:
- Use **Terraform** to provision AWS resources locally
- Use **Ansible** to seed initial data into the database
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
│        │                   ▲          ▲                         │
│        │                   │          │                         │
│        │           ┌───────┴─┐      ┌─┴───────────┐             │
│        │           │ Ansible │      │  Terraform  │             │
│        │           └─────────┘      └─────────────┘             │
│        │          (seeds data)     (provisions table)           │
│        │                                                        │
│        │                                                        │
│        │                                                        │
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
| **Configuration** | Ansible | Seeds initial data into DynamoDB |
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
├── ansible/
│   ├── inventory.ini           # Ansible inventory
│   └── playbook.yml            # Data seeding playbook
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
3. **Ansible** → Seeds the table with 3 initial todo items
4. **Backend** → Starts after Terraform and Ansible complete
5. **Frontend** → Starts after Backend
6. **Nginx** → Starts after Backend + Frontend

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/todos` | List all todos |
| `POST` | `/api/todos` | Create a new todo |
| `PUT` | `/api/todos/<id>` | Update a todo |
| `DELETE` | `/api/todos/<id>` | Delete a todo |

## Infrastructure Components

### Terraform Resources

| Resource | Description |
|----------|-------------|
| `aws_dynamodb_table.todo_table` | DynamoDB table with `id` as partition key |

### Ansible Tasks

| Task | Description |
|------|-------------|
| Seed DynamoDB | Inserts 3 sample todo items into the `todo` table |

The Ansible playbook runs after Terraform provisions the infrastructure and populates the database with initial data so the application has content immediately upon startup.

## Testing

### Run Backend Tests

```bash
# Run tests in Docker
docker-compose --profile test up backend-test --build
```

### Test Coverage

The test suite includes:
- Health check endpoint (1 test)
- CRUD operations - Create, Read, Update, Delete (8 tests)
- Error handling and edge cases (3 tests)
- CORS headers validation (2 tests)

**Total: 14 test cases** covering all API endpoints with DynamoDB mocking (no real AWS connection needed).

Coverage results are displayed directly in the terminal output.

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
