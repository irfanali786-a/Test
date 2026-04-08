# Gist API Server

A simple HTTP web server built with **FastAPI (Python 3.12+)** that interacts with the GitHub API and responds to requests on `/` with a list of a user’s publicly available gists.  
By default, the API uses the example user **octocat**.

## Features
- Endpoint `/` returns public gists for a given GitHub username (`?user=username`).
- Default user is `octocat`.
- Health check endpoint `/health`.
- Lightweight in-memory TTL cache (30s).
- Packaged in a Docker container running as a **non-root user** on port **8080**.
- Automated tests with **pytest**.

---

## Requirements
- Python 3.12+
- Docker (for containerized run)

---

## Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-org/gist-api.git
cd gist-api

### 2. Create a virtual environment and install dependencies

python3.12 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt


### 3. Run the server localy

uvicorn app.main:app --host 0.0.0.0 --port 8080

Now open 

http://localhost:8080/octocat in your browser to see the gists for the user `octocat`.

# Run the test 
pytest -q

# Docker Setup
docker build -t gist-api:latest .

Run  the container:
docker run -d -p 8080:8080 --name gist-api gist-api:latest
Now you can access the API at http://localhost:8080/octocat to see the gists for the user `octocat`.
