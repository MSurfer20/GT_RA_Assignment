# Design Choices made for the system

## Overview
The system is built using a simple setup for handling tasks in the background:

- **FastAPI**: Acts as the web server. It handles requests, file uploads, and serves the frontend.
- **Celery**: Runs tasks in the background so that multiple files can be handled concurrently.
- **Redis**: Helps FastAPI and Celery talk to each other.
- **SQLite**: Serves as the DB to store information about tasks and their results.
- **HTML & Vanilla JavaScript**: A basic frontend to interact with the backend APIs.

## Rationales behind each design choice

### FastAPI
**Why?** Since the assignment constraints required Python backend, FastAPI was used as it is the standard choice for API development. FastAPI is modern, fast, and provides built-in validation through Pydantic, making it the obvious choice. Additionally, its auto-generated OpenAPI docs make it easy to test API endpoints as well!


**Alternatives considered:** I also considered using Flask or Django for the backend. However, Flask lacks native`async` support and automatic request validation. On the other hand, Django being a heavier framework seemed like an overkill in this case.

### Celery + Redis
**Why?** The assessment requires simulating a 15-second computation without blocking the user. Celery is the industry standard for offloading these long-running tasks. By using Redis as a broker, the system ensures that every submitted dataset is properly queued and processed with minimal data loss or inconsistency. Since the processing of datasets is not kept on the web server, it also ensures that if the server restarts then also processing of the tasks happens correctly. Further, if a worker dies in the middle of processing, then `task_acks_late` flag ensures that it is restarted from the Redis queue. This increases the fault tolerance of the system.

**Alternatives considered:** The task required long-running concurrent computations, which provided two other choices:
* Creating a polling worker: In this case, I would have inserted a new dataset with status PENDING into the DB, and would have spawned another process which polled the DB continuously to find any elements with PENDING status. If found, the worker would set its status to PROCESSING and process it. After it is done processing, it would write the results to the DB and set status to COMPLETED. However, this approach suffers from requiring continious polling over the DB, causing hitting disk unnecessarily and also possibly causing a lag in processing. Further, if the worker is not multi-threaded then it would lead to slow sequential processing. 

* Using FastAPI's BackgroundTasks: FastAPI's `BackgroundTasks` could be simpler for usage here. However, it runs in the same memory space as the web server. Thus, in case the server restarts, the processing tasks would be dropped and would be in an incorrect state. Avoiding this was a **hard requirement** of the assignment. Hence, this was not chosen. Celery guarantees that tasks are safely queued in a dedicated message broker (Redis) and executed by separate worker processes. This prevents data loss and handles concurrent bursts naturally. Further, FastAPI itself recommends [BackgroundTasks](https://fastapi.tiangolo.com/tutorial/background-tasks/#caveat) for only small tasks, and I wanted to design the system to be more robust.

### SQLite

**Why?** SQLite requires zero configuration overhead, making the project exceptionally easy to run (just `docker-compose up`). The database file is mounted as a Docker volume (`./data`), ensuring state survives container restarts. While SQLite's file-level locking isn't ideal for highly concurrent distributed workers, it is perfectly suited for simulating this assignment's requirements without requiring reviewers to provision a PostgreSQL database.

### HTML+Vanilla JS

**Why?** Since the assignment explicitly mentioned minimal frontend, I decided to not use any complex frameworks. Using a heavy framework would introduce a Node.js build step (Webpack/Vite), increasing complexity and Docker image size. Vanilla JS keeps the frontend lightweight and directly servable.*

## An important design choice

Rather than passing the entire JSON through Redis, increasing the memory consumption of the queue, I stored every uploaded file in `data/` directory and each worker independently parsed the file. This ensured that redis didn't run out of memory.

**Assumption:** This assumes that the files are big enough to be opened in the web server. If the file is too big, then we would require `ijson` to parse it. However, I assume that the file is not that big.