# Deployment Guide for FGN Savings Bond Application

This guide provides detailed instructions for deploying the FGN Savings Bond application in various environments.

## Table of Contents

1. [Docker Deployment](#docker-deployment)
2. [Cloud Deployment](#cloud-deployment)
   - [AWS](#aws)
   - [Azure](#azure)
   - [Google Cloud](#google-cloud)
3. [Local Server Deployment](#local-server-deployment)
4. [Environment Variables](#environment-variables)
5. [Database Setup](#database-setup)
6. [Backup and Restore](#backup-and-restore)
7. [Monitoring](#monitoring)

## Docker Deployment

The application is containerized using Docker, making it easy to deploy in any environment that supports Docker.

### Prerequisites

- Docker Engine (version 20.10.0 or higher)
- Docker Compose (version 2.0.0 or higher)

### Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd fgnbond_sub
   ```

2. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file with your configuration.

4. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

5. Verify the application is running:
   ```bash
   docker-compose ps
   ```

6. Access the application at http://localhost:8501

## Cloud Deployment

### AWS

#### Using Elastic Container Service (ECS)

1. Create an ECR repository:
   ```bash
   aws ecr create-repository --repository-name fgn-bond-app
   ```

2. Authenticate Docker to your ECR registry:
   ```bash
   aws ecr get-login-password | docker login --username AWS --password-stdin <aws-account-id>.dkr.ecr.<region>.amazonaws.com
   ```

3. Build, tag, and push the Docker image:
   ```bash
   docker build -t <aws-account-id>.dkr.ecr.<region>.amazonaws.com/fgn-bond-app:latest .
   docker push <aws-account-id>.dkr.ecr.<region>.amazonaws.com/fgn-bond-app:latest
   ```

4. Create an ECS cluster, task definition, and service using the AWS Console or CLI.

5. Configure environment variables in the task definition.

#### Using Elastic Beanstalk

1. Install the EB CLI:
   ```bash
   pip install awsebcli
   ```

2. Initialize EB application:
   ```bash
   eb init -p docker fgn-bond-app
   ```

3. Create an environment:
   ```bash
   eb create fgn-bond-production
   ```

4. Deploy the application:
   ```bash
   eb deploy
   ```

### Azure

#### Using Azure Container Instances

1. Create an Azure Container Registry:
   ```bash
   az acr create --resource-group myResourceGroup --name fgnbondregistry --sku Basic
   ```

2. Build and push the image:
   ```bash
   az acr build --registry fgnbondregistry --image fgn-bond-app:latest .
   ```

3. Create a container instance:
   ```bash
   az container create --resource-group myResourceGroup --name fgn-bond-app --image fgnbondregistry.azurecr.io/fgn-bond-app:latest --dns-name-label fgn-bond-app --ports 8501
   ```

### Google Cloud

#### Using Cloud Run

1. Build and push the image to Google Container Registry:
   ```bash
   gcloud builds submit --tag gcr.io/[PROJECT_ID]/fgn-bond-app
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy fgn-bond-app --image gcr.io/[PROJECT_ID]/fgn-bond-app --platform managed
   ```

## Local Server Deployment

### Using Docker

Follow the [Docker Deployment](#docker-deployment) instructions above.

### Using Nginx as a Reverse Proxy

1. Install Nginx:
   ```bash
   sudo apt update
   sudo apt install nginx
   ```

2. Create an Nginx configuration file:
   ```bash
   sudo nano /etc/nginx/sites-available/fgn-bond-app
   ```

3. Add the following configuration:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

4. Enable the site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/fgn-bond-app /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## Environment Variables

The application uses the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| MONGO_URI | MongoDB connection string | mongodb://username:password@mongodb:27017/fgn_bonds?authSource=admin |
| DB_NAME | MongoDB database name | fgn_bonds |
| COLLECTION_NAME | MongoDB collection name | applications |
| ENVIRONMENT | Application environment | development |
| SECRET_KEY | Secret key for secure operations | None |

## Database Setup

### MongoDB

1. Create a MongoDB database:
   ```javascript
   use fgn_bonds
   ```

2. Create a collection:
   ```javascript
   db.createCollection("applications")
   ```

3. Create an index for faster queries:
   ```javascript
   db.applications.createIndex({ "submission_date": 1 })
   db.applications.createIndex({ "full_name": 1 })
   db.applications.createIndex({ "company_name": 1 })
   ```

## Backup and Restore

### MongoDB Backup

1. Create a backup:
   ```bash
   mongodump --uri="mongodb://username:password@hostname:port/fgn_bonds" --out=/backup/directory
   ```

2. Restore from backup:
   ```bash
   mongorestore --uri="mongodb://username:password@hostname:port/fgn_bonds" /backup/directory
   ```

## Monitoring

### Application Logs

Docker logs can be viewed with:
```bash
docker-compose logs -f web
```

### MongoDB Logs

```bash
docker-compose logs -f mongodb
```

### Health Check

Create a simple health check endpoint in your application to monitor its status.
