from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="Carbon-Aware DevOps Tracker")
@app.get("/")
def root():
    return {
        "app": "Carbon-Aware DevOps Tracker",
        "endpoints": ["/health", "/builds", "/deployments", "/carbon-report", "/optimize"]
    }
# In-memory storage (resets when the app restarts — that's fine for this assignment)
builds = []
deployments = []

# Rough constants for estimating energy/carbon cost.
# These are simplified assumptions, not scientifically precise — good enough for demonstrating the concept.
POWER_DRAW_WATTS = 65          # estimated average power draw per "unit" of compute during a build/pod
GRID_CARBON_INTENSITY = 0.7    # kg CO2 per kWh (rough grid average, India-ish)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/builds")
def log_build(duration_seconds: float, cpu_cores: float = 1.0):
    """Log a CI build event: how long it ran and how much CPU it used."""
    entry = {
        "duration_seconds": duration_seconds,
        "cpu_cores": cpu_cores,
        "timestamp": datetime.utcnow().isoformat()
    }
    builds.append(entry)
    return {"message": "build logged", "entry": entry}


@app.post("/deployments")
def log_deployment(replica_count: int, duration_seconds: float):
    """Log a Kubernetes scaling event: how many replicas ran, and for how long."""
    entry = {
        "replica_count": replica_count,
        "duration_seconds": duration_seconds,
        "timestamp": datetime.utcnow().isoformat()
    }
    deployments.append(entry)
    return {"message": "deployment logged", "entry": entry}


def estimate_carbon_kg(duration_seconds: float, active_units: float) -> float:
    """Core calculation: convert time + resource usage into estimated kg of CO2."""
    hours = duration_seconds / 3600
    energy_kwh = (POWER_DRAW_WATTS * active_units * hours) / 1000
    return round(energy_kwh * GRID_CARBON_INTENSITY, 6)


@app.get("/carbon-report")
def carbon_report():
    """Total estimated CO2 emitted across all logged builds and deployments."""
    build_carbon = sum(estimate_carbon_kg(b["duration_seconds"], b["cpu_cores"]) for b in builds)
    deploy_carbon = sum(estimate_carbon_kg(d["duration_seconds"], d["replica_count"]) for d in deployments)

    return {
        "total_builds_logged": len(builds),
        "total_deployments_logged": len(deployments),
        "estimated_build_carbon_kg": round(build_carbon, 6),
        "estimated_deployment_carbon_kg": round(deploy_carbon, 6),
        "estimated_total_carbon_kg": round(build_carbon + deploy_carbon, 6)
    }


@app.get("/optimize")
def optimize():
    """Flag potential waste: were more replicas run than the average workload needed?"""
    if not deployments:
        return {"message": "No deployment data logged yet."}

    avg_replicas = sum(d["replica_count"] for d in deployments) / len(deployments)
    max_replicas = max(d["replica_count"] for d in deployments)

    flags = []
    if max_replicas > avg_replicas * 1.5:
        flags.append(
            f"Peak replica count ({max_replicas}) was well above your average "
            f"({avg_replicas:.1f}) — consider whether that peak scaling was necessary."
        )

    return {
        "average_replicas": round(avg_replicas, 2),
        "max_replicas": max_replicas,
        "flags": flags if flags else ["No significant waste detected."]
    }