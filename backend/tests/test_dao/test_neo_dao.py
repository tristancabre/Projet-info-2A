import os
from unittest.mock import patch

import psycopg2
import pytest
from business_object.player import Player

from dao.player_dao import PlayerDao
from utils.reset_database import ResetDatabase
from utils.security import hash_password



