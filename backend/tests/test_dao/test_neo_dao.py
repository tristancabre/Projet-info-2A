import os
from unittest.mock import patch

import psycopg2
import pytest

from business_object.user import User
from dao.user_dao import UserDao
from utils.reset_database import ResetDatabase
from utils.security import hash_password



