from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from dao.nasa_dao import NasaDao
from schema.neo_model import NeoReadModel
from service.neo_service import NeoService
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_neo_service():
    """Dependency Injection provider for NeoService."""
    return NeoService()


# --- Routes "statiques" déclarées AVANT /{id_neo} pour éviter tout conflit ---


@router.get("/approaching", response_model=list[NeoReadModel], tags=["Neos"])
async def neos_approaching(
    days: int = Query(7, ge=1, description="Fenêtre en jours à partir d'aujourd'hui"),
    neo_service=Depends(get_neo_service),
):
    """List neos whose closest approach falls within the next `days` days."""
    logger.info("List approaching neos (days=%s)", days)
    return neo_service.get_approaching(days)


@router.get("/search/name", response_model=list[NeoReadModel], tags=["Neos"])
async def neos_by_name(
    name: str = Query(..., min_length=1),
    neo_service=Depends(get_neo_service),
):
    """Find neos whose name partially matches (case insensitive)."""
    logger.info("Search neos by name")
    neos = neo_service.search_by_name(name)
    if not neos:
        raise HTTPException(status_code=404, detail=f"No neo matching name='{name}'.")
    return neos


@router.get("/search/diameter", response_model=list[NeoReadModel], tags=["Neos"])
async def neos_by_diameter(
    min_diameter: float | None = Query(None),
    max_diameter: float | None = Query(None),
    neo_service=Depends(get_neo_service),
):
    """Find neos whose diameter is within the given bounds."""
    logger.info("Search neos by diameter")
    return neo_service.search_by_diameter(min_diameter, max_diameter)


@router.get("/search/speed", response_model=list[NeoReadModel], tags=["Neos"])
async def neos_by_speed(
    min_speed: float | None = Query(None),
    max_speed: float | None = Query(None),
    neo_service=Depends(get_neo_service),
):
    """Find neos whose speed is within the given bounds."""
    logger.info("Search neos by speed")
    return neo_service.search_by_speed(min_speed, max_speed)


@router.get("/search/closest-day", response_model=list[NeoReadModel], tags=["Neos"])
async def neos_by_closest_day(
    day: date = Query(..., description="Format: YYYY-MM-DD"),
    neo_service=Depends(get_neo_service),
):
    """Find neos whose closest approach falls exactly on this day."""
    logger.info("Search neos by closest day")
    neos = neo_service.search_by_closest_day(day)
    if not neos:
        raise HTTPException(status_code=404, detail=f"No neo with closest_day={day}.")
    return neos


# --- Route dynamique en dernier ---


@router.get("/{id_neo}", response_model=NeoReadModel, tags=["Neos"])
async def neo_by_id(id_neo: int, neo_service=Depends(get_neo_service)):
    """Find a neo by their unique ID.

    Args:
        id_neo (int)
        neo_service (NeoService): The service used to interact with neo data
    Returns:
        NeoReadModel: The neo data if found
    Raises:
        HTTPException: 404 error if the neo is not found
    """
    logger.info("Find a neo by id")
    neo = neo_service.search_by_id(id_neo)
    if not neo:
        raise HTTPException(status_code=404, detail=f"neo (id={id_neo}) not found.")
    return neo


@router.get("/", response_model=list[NeoReadModel], tags=["Neos"])
async def find_all_neos(neo_service=Depends(get_neo_service)):
    """List all neos.

    Args:
        neo_service (NeoService): The service used to interact with neo data
    Returns:
        list[NeoReadModel]: A list of all registered neos.
    """
    logger.info("List all neos")
    return neo_service.find_all()


@router.post("/update")
def update_neos():
    nasa_database = NasaDao()

    neos = nasa_database.recuperer_donnees_nasa()
    nasa_database.inserer_donnees_sql(neos)

    return {"message": "NEO data successfully updated", "count": len(neos)}
