# Docker Setup for Recipier

This guide explains how to run Recipier using Docker, both for development and production.

## Quick Start

### Production (Single Container)

Build and run the complete application (frontend + backend) in a single container:

```bash
# Build the image
docker build -t recipier:latest .

# Run the container
docker run -d \
  -p 8000:8000 \
  -e TODOIST_API_TOKEN='your_token_here' \
  -v $(pwd)/data:/app/data \
  --name recipier \
  recipier:latest

# Access the application
open http://localhost:8000
```

### Production (Docker Compose)

```bash
# Set your Todoist API token
export TODOIST_API_TOKEN='your_token_here'

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Development (Docker Compose)

Run with hot-reload for both frontend and backend:

```bash
# Set your Todoist API token
export TODOIST_API_TOKEN='your_token_here'

# Start development environment
docker-compose -f docker-compose.dev.yml up

# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
```

## Architecture

### Production Build

The production Dockerfile uses a **multi-stage build**:

1. **Stage 1 (frontend-builder)**: Builds React frontend with Vite
   - Uses Node.js 20 Alpine image
   - Runs `npm ci` and `npm run build`
   - Creates optimized static files in `dist/`

2. **Stage 2 (backend)**: Python backend serving API + static files
   - Uses Python 3.12 slim image
   - Installs dependencies with `uv`
   - Copies built frontend from Stage 1
   - Serves frontend via FastAPI's StaticFiles

**Result**: Single container running on port 8000 with both frontend and backend.

### Development Setup

The development compose file runs **two separate services**:

1. **Backend**: Python backend with hot-reload
   - Mounts source code as volumes
   - Runs `uvicorn` with `--reload` flag
   - Changes to Python files reload automatically

2. **Frontend**: Vite development server
   - Mounts source code as volumes
   - Runs `npm run dev` with hot-reload
   - Changes to React files reload automatically
   - Access at http://localhost:5173

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TODOIST_API_TOKEN` | Yes | - | Your Todoist API token |
| `HOST` | No | `0.0.0.0` | Host to bind to |
| `PORT` | No | `8000` | Port for backend |

### Volumes

**Production**:
- `./data:/app/data` - Meal plan JSON files
- `./meals_database.json:/app/meals_database.json` - Meals database
- `./my_config.json:/app/my_config.json` - Configuration

**Development** (additional):
- `./recipier:/app/recipier` - Backend source code
- `./backend:/app/backend` - API routes and models
- `./frontend:/app` - Frontend source code

## Docker Commands Reference

### Building

```bash
# Build production image
docker build -t recipier:latest .

# Build development image
docker build -f Dockerfile.dev -t recipier:dev .

# Build with no cache
docker build --no-cache -t recipier:latest .
```

### Running

```bash
# Run production container
docker run -d -p 8000:8000 \
  -e TODOIST_API_TOKEN='your_token' \
  --name recipier \
  recipier:latest

# Run with custom port
docker run -d -p 3000:8000 \
  -e TODOIST_API_TOKEN='your_token' \
  --name recipier \
  recipier:latest

# Run development (docker-compose)
docker-compose -f docker-compose.dev.yml up
```

### Managing

```bash
# View logs
docker logs -f recipier

# Stop container
docker stop recipier

# Restart container
docker restart recipier

# Remove container
docker rm -f recipier

# Execute command in container
docker exec -it recipier bash

# View container stats
docker stats recipier
```

### Docker Compose

```bash
# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild and start
docker-compose up --build

# Development mode
docker-compose -f docker-compose.dev.yml up
```

## Health Checks

The backend includes health checks on `/api/health`:

```bash
# Check health via curl
curl http://localhost:8000/api/health

# Expected response
{"status": "healthy", "version": "1.0.0"}
```

Docker automatically monitors container health:
- Interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3
- Start period: 5 seconds

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs recipier

# Check if port is already in use
lsof -i :8000

# Run with interactive mode to see errors
docker run -it --rm recipier:latest
```

### API token issues

```bash
# Verify token is set
docker exec recipier env | grep TODOIST

# Update token on running container
docker exec recipier env TODOIST_API_TOKEN='new_token'
# Note: You'll need to restart the container for changes to take effect
```

### Frontend not loading

**Production**:
- Verify `frontend/dist` exists in container:
  ```bash
  docker exec recipier ls -la /app/frontend/dist
  ```
- Check backend logs for static file serving errors

**Development**:
- Ensure frontend service is running: `docker-compose ps`
- Check frontend logs: `docker-compose logs frontend`
- Verify frontend is accessible: http://localhost:5173

### Hot-reload not working (development)

Ensure volumes are mounted correctly:
```bash
docker-compose -f docker-compose.dev.yml config
```

If using Docker Desktop on Mac/Windows, enable file sharing for the project directory.

### Database changes not reflected

The meals database is mounted as a volume. Changes on host will reflect in container immediately:

```bash
# Restart to ensure backend reloads
docker-compose restart backend
```

## Production Deployment

### Best Practices

1. **Use environment variables** for secrets:
   ```bash
   # Don't commit API tokens to .env files
   docker run -e TODOIST_API_TOKEN="$TODOIST_API_TOKEN" recipier:latest
   ```

2. **Enable health checks** in orchestration (Kubernetes, ECS, etc.)

3. **Use volumes** for persistent data:
   ```bash
   docker run -v recipier-data:/app/data recipier:latest
   ```

4. **Run as non-root user** (add to Dockerfile if needed):
   ```dockerfile
   RUN useradd -m -u 1000 recipier
   USER recipier
   ```

5. **Set resource limits**:
   ```bash
   docker run --memory="512m" --cpus="1.0" recipier:latest
   ```

### Kubernetes Deployment

Example deployment manifest:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recipier
spec:
  replicas: 2
  selector:
    matchLabels:
      app: recipier
  template:
    metadata:
      labels:
        app: recipier
    spec:
      containers:
      - name: recipier
        image: recipier:latest
        ports:
        - containerPort: 8000
        env:
        - name: TODOIST_API_TOKEN
          valueFrom:
            secretKeyRef:
              name: recipier-secrets
              key: todoist-token
        volumeMounts:
        - name: data
          mountPath: /app/data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: recipier-data
---
apiVersion: v1
kind: Service
metadata:
  name: recipier
spec:
  selector:
    app: recipier
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Size Optimization

Current image sizes:
- Production: ~500MB (Alpine + Python slim + built frontend)
- Development: ~600MB (includes dev dependencies)

To reduce size further:
1. Use multi-stage builds (already implemented)
2. Minimize Python dependencies
3. Use `.dockerignore` (already implemented)
4. Consider distroless images for production

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI in Containers](https://fastapi.tiangolo.com/deployment/docker/)
- [Vite Docker Guide](https://vitejs.dev/guide/static-deploy.html)
