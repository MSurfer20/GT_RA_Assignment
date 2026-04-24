# Data Processing System

This system allows asynchronous processing of JSON files, allowing users to upload JSON datasets, track the progress of processing and see the processed outputs.

## Requirements

- Docker
- Docker Compose

## Usage Instructions

1.  Clone the repo
    ```bash
    git clone https://github.com/MSurfer20/GT_RA_Assignment
    cd GT_RA_Assignment
    ```

2.  Run the application
    ```bash
    docker-compose up --build
    ```

3.  The system will be running at  `http://localhost:8080/`.


## Stopping the Application

To shut down the system and remove the containers:
```bash
docker-compose down
```

## Design Choices
Detailed design choices can be found in `DESIGN.md`.