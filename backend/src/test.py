from dao.nasa_dao import NasaDao
from dao.neo_dao import NeoDao

neo = NasaDao().recuperer_donnees_nasa()
NeoDao().inserer_donnees_sql(neo)
