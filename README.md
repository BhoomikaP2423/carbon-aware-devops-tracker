# Carbon-Aware DevOps Tracker

A FastAPI service that logs CI builds and Kubernetes deployments and estimates their carbon cost.

## Run locally
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    uvicorn main:app --reload

Open http://localhost:8000/docs

## Run tests
    pytest -v

## Run with Docker
    docker build -t carbon-tracker .
    docker run -p 8000:8000 carbon-tracker