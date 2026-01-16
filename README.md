# FGN Savings Bond Subscription Application

A web application for submitting Federal Government of Nigeria (FGN) Savings Bond applications. Digitizes the official DMO FGNSB subscription form process.

## Quick Start (Docker)

### Prerequisites
- Docker Engine 20.10+ (`docker --version`)
- Docker Compose 2.0+ (`docker-compose --version`)
- Ports 80, 8080 available (or 8501, 8502 for direct access)

### Deploy in 3 Steps

```bash
# 1. Clone and configure
git clone <repository-url>
cd fgnbond_sub
cp .env.example .env

# 2. Start all services
docker-compose up -d

# 3. Verify deployment
docker-compose ps
```

### Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **User App** | http://localhost | Bond subscription form |
| **Admin Dashboard** | http://localhost:8080 | Analytics & management |

> **Default Admin Credentials:** `admin` / `admin123`
> **WARNING:** Change these before production! See [Configuration](#configuration).

---

## Quick Start (Local Development)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start MongoDB (required)
# Option 1: Docker
docker run -d -p 27017:27017 --name mongodb mongo:7.0

# Option 2: Local MongoDB installation

# Run applications (separate terminals)
streamlit run src/streamlit_app.py      # User app on :8501
streamlit run src/admin_app.py          # Admin on :8502
```

---

## Architecture

```
                           ┌─────────────────┐
                           │     Nginx       │
                           │  (Port 80/8080) │
                           └────────┬────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     │
    ┌─────────────────┐   ┌─────────────────┐            │
    │   User App      │   │  Admin Dashboard │            │
    │   (Port 8501)   │   │   (Port 8502)   │            │
    │                 │   │                 │            │
    │  - Bond Form    │   │  - Analytics    │            │
    │  - PDF Generate │   │  - Reports      │            │
    │  - Validation   │   │  - Export       │            │
    └────────┬────────┘   └────────┬────────┘            │
             │                     │                     │
             └──────────┬──────────┘                     │
                        │                                │
                        ▼                                │
              ┌─────────────────┐                        │
              │    MongoDB      │◄───────────────────────┘
              │  (Port 27017)   │
              │                 │
              │  - Applications │
              │  - User Data    │
              └─────────────────┘
```

**Services:**
- **Nginx** - Reverse proxy with WebSocket support for Streamlit
- **User App** - Bond subscription form (Individual, Joint, Corporate)
- **Admin Dashboard** - Password-protected analytics and reporting
- **MongoDB** - Application data storage with JSON fallback

---

## Features

- **Multiple Applicant Types** - Individual, Joint, and Corporate applications
- **Form Validation** - BVN, email, phone, and currency validation
- **PDF Generation** - Professional output matching official DMO form
- **Admin Dashboard** - Analytics, trends, and export functionality
- **Docker Ready** - Full containerization with health checks

---

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGO_URI` | MongoDB connection string | `mongodb://admin:password@mongodb:27017/...` |
| `DB_NAME` | Database name | `fgn_bonds` |
| `ADMIN_USERNAME` | Admin login username | `admin` |
| `ADMIN_PASSWORD_HASH` | SHA-256 hash of admin password | Hash of `admin123` |
| `ENVIRONMENT` | `development` or `production` | `development` |

### Generating Admin Password Hash

```bash
# macOS/Linux
echo -n "YourSecurePassword" | shasum -a 256 | cut -d' ' -f1

# Windows (PowerShell)
python -c "import hashlib; print(hashlib.sha256('YourSecurePassword'.encode()).hexdigest())"

# Python (cross-platform)
import hashlib
print(hashlib.sha256("YourSecurePassword".encode()).hexdigest())
```

Update `ADMIN_PASSWORD_HASH` in `.env` with the generated hash.

---

## Project Structure

```
fgnbond_sub/
├── src/
│   ├── streamlit_app.py      # Main user application
│   ├── admin_app.py          # Admin dashboard
│   ├── form_handler.py       # Form processing & PDF generation
│   ├── utils.py              # Utility functions
│   ├── components/           # Reusable UI components
│   ├── design_system/        # Theme and styling
│   └── pdf/                  # PDF generation templates
├── nginx/
│   └── nginx.conf            # Reverse proxy configuration
├── docs/
│   ├── SECURITY.md           # Production security checklist
│   └── ADMIN_GUIDE.md        # Admin dashboard guide
├── docker-compose.yml        # Development configuration
├── docker-compose.prod.yml   # Production configuration
├── Dockerfile                # Container build instructions
├── .env.example              # Environment template
└── requirements.txt          # Python dependencies
```

---

## Troubleshooting

### Services Not Starting

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs web        # User app
docker-compose logs admin      # Admin dashboard
docker-compose logs mongodb    # Database
docker-compose logs nginx      # Reverse proxy
```

### MongoDB Connection Failed

1. Ensure MongoDB is running: `docker-compose ps mongodb`
2. Check credentials in `.env` match docker-compose configuration
3. For local dev, verify `MONGO_URI` uses `localhost` not `mongodb`

### Port Already in Use

```bash
# Find process using port
lsof -i :80      # macOS/Linux
netstat -ano | findstr :80  # Windows

# Use alternative ports in docker-compose.yml
```

### Admin Login Not Working

1. Verify `ADMIN_PASSWORD_HASH` matches your password
2. Ensure `ADMIN_USERNAME` in `.env` is correct
3. Clear browser cache/cookies
4. Check logs: `docker-compose logs admin`

### Health Check Failing

```bash
# Test health endpoints directly
curl http://localhost:8501/_stcore/health
curl http://localhost:8502/_stcore/health

# Check container health status
docker inspect --format='{{.State.Health.Status}}' fgnbond_sub-web-1
```

---

## Production Deployment

For production deployments:

```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up -d
```

**Before deploying to production:**
1. Review [docs/SECURITY.md](docs/SECURITY.md) checklist
2. Change all default passwords in `.env`
3. Configure SSL certificates
4. Set `ENVIRONMENT=production`

See [docs/deployment_guide.md](docs/deployment_guide.md) for cloud deployment instructions (AWS, Azure, GCP).

---

## CI/CD

This project includes a GitHub Actions pipeline (`.github/workflows/ci.yml`):

- **Lint** - Python syntax validation with flake8
- **Build** - Docker image build and health check test
- **Push** - Automatic push to Docker Hub on main branch
- **Security** - Trivy vulnerability scanning

To enable Docker Hub push, add these secrets to your repository:
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Author

**Hedgar Ajakaiye**

---

## Acknowledgments

- Debt Management Office (DMO) of Nigeria
- Federal Government of Nigeria
