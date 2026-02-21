## Rempy

## Description

This is an image processing benchmark application.

This application is divided in 3 parts:

- The frontend: This is the user interface of the application.
- The backend: This is the server of the application (handles requests, logic, DB...).
- The database: All the benchmark data are stored in a PostgreSQL DB.

## Installation

The whole project is usable from a Docker Compose file. Each Python server
instance (front-end and back-end) is handled by uv. The database used is PostgreSQL.

## Usage

1. Go in the rempy directory
    ```bash
    cd rempy 
    ```
2. Launch all the services (frontend, backend, db)
    ```bash
    docker compose up 
    ```
3. Go to **http://127.0.0.1:8050** to connect to the application

4. Enjoy ! 