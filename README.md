# FastAPI + PostgresSQL + Celery Example

An example microservices demonstrates how to perform heavy background computation task such as running machine learning model.

Tech stack:

- FastAPI
  - create task
  - query task
- PostgresSQL
  - persist task
- Celery
  - Redis: as broker and backend of celery

Workflow:

![workflow](./out/workflow.png)

_NOTE_:

- `Task` are defined by custom FastAPI `App` frontend user.
- `Celery Task` are defined by `Celery` for internal
  - [task model](https://docs.celeryq.dev/en/latest/internals/reference/celery.backends.database.models.html#celery.backends.database.models.Task)
  - [result backend](https://docs.celeryq.dev/en/stable/userguide/tasks.html#result-backends)
- Update `Celery Task` progress with custom states
  - [celery task getting progress · GitHub](https://gist.github.com/siddhism/6399964b89ce734990763c922c3556da)
  - [python - How to retrieve meta from celery backend storage - Stack Overflow](https://stackoverflow.com/questions/34208399/how-to-retrieve-meta-from-celery-backend-storage)


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

_NOTE_:

- `Dockerfile.dev` is used for developing easily in container environment. All `docker compose files` here are for development.
