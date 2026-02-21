# Rempy backend

This is the backend of the image processing benchmark application.

## Installation

See the **README.md** at the root directory of the project and the warning below.

**Warning**

The backend is not supposed to be USED ALONE.

But if you really want to test only the backend of the application, you need to comment all the services in the **docker-compose.yaml** file except the db and backend services. Uncomment this part in the backend service (so you can access the API from localhost) : 

```yaml
ports:
      - "8000:8000"
```
## Usage

Connect to **http://127.0.0.1:8000/docs** to see the Swagger and try the API.