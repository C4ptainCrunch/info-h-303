DEBUG = True
DB_URL = "dbname=horeca"


try:
    from local_config import *
except ImportError:
    print("No local config found!")
