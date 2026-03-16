# Redis Setup 

## SECTION 1: Files Created

- **`data/api/reddis_api_db.py`**  
  Abstract base class defining the DB contract (`get`, `set`, `delete`, `exists`, `keys`, `get_all`, `clear`). This lets the RL code depend on an interface instead of a specific database.

- **`data/api/redis_db.py`**  
  Redis implementation of `BaseDB` using `redis-py`. Values are JSON-serialized so you can store floats, dicts, lists, etc.

- **`data/services/rl_data_service.py`**  
  Service that stores and retrieves Q-values using any `BaseDB` implementation. Keys follow the pattern `q_val:{state}:{action}`.

- **`Dockerfile.redis`**  
  Recipe to build the Redis Docker image used by this project (based on `redis:7-alpine`) and copy in `redis.conf`.

- **`redis.conf`**  
  Redis configuration for dev: port/bind settings, memory limits + eviction policy, and persistence settings.

- **`docker-compose.yml`**  
  Starts the Redis container (plus storage volume and healthcheck) with a single command.

## SECTION 2: Setup Steps for New Members

### 1) Prerequisites
- Install **Docker Desktop**
- Make sure **Docker Engine is running** before proceeding

### 2) Start Redis container

```bash
docker-compose up -d
```

First time will take a minute to download/build what’s needed.

### 3) Verify container is running

```bash
docker ps
```

You should see a container like `marl_redis` with status `Up`.

### 4) Test the Python connection

```bash
python -c "from data.api.redis_db import RedisDB; db = RedisDB(); print(db.ping())"
```

It should print `True`.

### 5) Run the RL engine normally after this

Once Redis is up and responding, run the RL engine the usual way for this repo.

## SECTION 3: Useful Commands

- Start Redis in background:

```bash
docker-compose up -d
```

- Stop everything:

```bash
docker-compose down
```

- View Redis logs if something breaks:

```bash
docker-compose logs redis
```

- Check running containers:

```bash
docker ps
```

- Rebuild image if config changes:

```bash
docker-compose up -d --build
```

## SECTION 4: Notes

- Docker must be running before starting the RL engine.
- The Q-table is persisted to disk via `redis.conf`, so training progress is not lost on container restart.
- `REDIS_HOST` and `REDIS_PORT` can be overridden via environment variables (defaults: `localhost` and `6379`).

