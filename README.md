# FastAPI + Celery + Redis + PostgresSQL Microservices

full tech stack of this project:

- FastAPI
- Celery
- Redis
- PostgresSQL

## Get Started

```sh
docker run -it --rm fastapi-celery-web bash
```

```sh
docker exec -it fastapi-celery-db-1 bash
```

```sh
docker-compose build
# CTRL+C: just stop containers while keeping data
docker-compose up
docker-compose up -d

# Remove containers with wiping data
docker-compose down 
```