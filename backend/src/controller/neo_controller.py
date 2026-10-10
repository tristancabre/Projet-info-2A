from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from schema.neo_model import NeoModel, NeoReadModel
from service.neo_service import NeoService
from utils.auth import require_admin
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_neo_service() -> NeoService:
    """Dependency Injection provider for NeoService."""
    return NeoService()


# Les routes sont déclarées avec `def` (et non `async def`) car le service et le
# driver de base de données sont synchrones : FastAPI les exécute alors dans un
# pool de threads au lieu de bloquer la boucle d'événements.

# Droits d'accès : la lecture (GET) est publique ; la création, la modification, la
# suppression et l'import depuis la NASA sont réservés aux administrateurs (require_admin).

# --- Routes "statiques" déclarées AVANT /{id_neo} pour éviter tout conflit ---


@router.get("/approaching", response_model=list[NeoReadModel], tags=["Neos"])
def neos_approaching(
    days: int = Query(7, ge=1, description="Fenêtre en jours à partir d'aujourd'hui"),
    neo_service: NeoService = Depends(get_neo_service),
):
    """List neos whose closest approach falls within the next `days` days."""
    logger.info("List approaching neos (days=%s)", days)
    return neo_service.get_approaching(days)


@router.get("/search/name", response_model=list[NeoReadModel], tags=["Neos"])
def neos_by_name(
    name: str = Query(..., min_length=1),
    neo_service: NeoService = Depends(get_neo_service),
):
    """Find neos whose name partially matches (case insensitive)."""
    logger.info("Search neos by name")
    return neo_service.search_by_name(name)


@router.get("/search/diameter", response_model=list[NeoReadModel], tags=["Neos"])
def neos_by_diameter(
    min_diameter: float | None = Query(None, ge=0),
    max_diameter: float | None = Query(None, ge=0),
    neo_service: NeoService = Depends(get_neo_service),
):
    """Find neos whose diameter is within the given bounds."""
    logger.info("Search neos by diameter")
    return neo_service.search_by_diameter(min_diameter, max_diameter)


@router.get("/search/speed", response_model=list[NeoReadModel], tags=["Neos"])
def neos_by_speed(
    min_speed: float | None = Query(None, ge=0),
    max_speed: float | None = Query(None, ge=0),
    neo_service: NeoService = Depends(get_neo_service),
):
    """Find neos whose speed is within the given bounds."""
    logger.info("Search neos by speed")
    return neo_service.search_by_speed(min_speed, max_speed)


@router.get("/search/closest-day", response_model=list[NeoReadModel], tags=["Neos"])
def neos_by_closest_day(
    day: date = Query(..., description="Format: YYYY-MM-DD"),
    neo_service: NeoService = Depends(get_neo_service),
):
    """Find neos whose closest approach falls exactly on this day."""
    logger.info("Search neos by closest day")
    return neo_service.search_by_closest_day(day)


@router.post("/update_database", tags=["Neos"], dependencies=[Depends(require_admin)])
def update_database(neo_service: NeoService = Depends(get_neo_service)):
    """Fetch the NEO data from the NASA API and store it in the database. Administrators only."""
    logger.info("Update the neo database from NASA")
    try:
        count = neo_service.refresh_from_nasa()
    except Exception:
        logger.exception("Error while updating the neo database")
        raise HTTPException(status_code=500, detail="Error while updating the neo database.")
    return {"message": "NEO data successfully updated", "count": count}


# --- Routes dynamiques en dernier ---


@router.get("/", response_model=list[NeoReadModel], tags=["Neos"])
def find_all_neos(neo_service: NeoService = Depends(get_neo_service)):
    """List all neos.

    Returns:
        list[NeoReadModel]: A list of all registered neos.
    """
    logger.info("List all neos")
    return neo_service.find_all()


@router.get("/{id_neo}", response_model=NeoReadModel, tags=["Neos"])
def neo_by_id(id_neo: int, neo_service: NeoService = Depends(get_neo_service)):
    """Find a neo by its unique ID.

    Raises:
        HTTPException: 404 error if the neo is not found
    """
    logger.info("Find a neo by id")
    neo = neo_service.search_by_id(id_neo)
    if not neo:
        raise HTTPException(status_code=404, detail=f"neo (id={id_neo}) not found.")
    return neo


@router.post(
    "/",
    response_model=NeoReadModel,
    status_code=201,
    tags=["Neos"],
    dependencies=[Depends(require_admin)],
)
def create_neo(p: NeoModel, neo_service: NeoService = Depends(get_neo_service)):
    """Create a new neo. Administrators only. The rarity is computed from the distance
    and the diameter.

    Returns:
        NeoReadModel: The newly created neo data.
    Raises:
        HTTPException: 500 error if the creation process fails.
    """
    logger.info("Create a neo")
    neo = neo_service.create(p.name, p.diameter, p.distance, p.speed, p.closest_day)
    if not neo:
        raise HTTPException(status_code=500, detail="Error while creating neo.")
    return neo


@router.put(
    "/{id_neo}",
    response_model=NeoReadModel,
    tags=["Neos"],
    dependencies=[Depends(require_admin)],
)
def update_neo(id_neo: int, p: NeoModel, neo_service: NeoService = Depends(get_neo_service)):
    """Update an existing neo's information. Administrators only. The rarity is recomputed.

    Returns:
        NeoReadModel: The updated neo.
    Raises:
        HTTPException: 404 error if the neo is not found.
        HTTPException: 500 error if the update process fails.
    """
    logger.info("Update a neo")
    neo = neo_service.search_by_id(id_neo)
    if not neo:
        raise HTTPException(status_code=404, detail=f"neo (id={id_neo}) not found.")

    neo.name = p.name
    neo.diameter = p.diameter
    neo.distance = p.distance
    neo.speed = p.speed
    neo.closest_day = p.closest_day

    neo = neo_service.update(neo)
    if not neo:
        raise HTTPException(status_code=500, detail="Error while updating neo.")
    return neo


@router.delete("/{id_neo}", tags=["Neos"], dependencies=[Depends(require_admin)])
def delete_neo(id_neo: int, neo_service: NeoService = Depends(get_neo_service)):
    """Delete a neo from the system. Administrators only.

    Raises:
        HTTPException: 404 error if the neo is not found.
        HTTPException: 500 error if the deletion fails.
    """
    logger.info("Delete a neo")
    neo = neo_service.search_by_id(id_neo)
    if not neo:
        raise HTTPException(status_code=404, detail=f"neo (id={id_neo}) not found.")

    if not neo_service.delete(neo):
        raise HTTPException(status_code=500, detail="Error while deleting neo.")
    return {"message": f"neo {neo.name} deleted"}
