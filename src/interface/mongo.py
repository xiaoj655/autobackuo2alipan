from pymongo import MongoClient
import pymongo
import pymongo.errors
from yaml import load, Loader
from urllib.parse import quote
import logging.config, atexit

with open("config.yml", "r") as f:
    c = load(f, Loader)
    c = c["mongo"]

logger = logging.getLogger("app")

if c['uri']:
    uri = c['uri']
else:
    uri = f"mongodb://{quote(c['username'])}:{quote(c['password'])}@{quote(c['host'])}{(':'+str(c['port'])) if c['port'] else ''}"
try:
    client = MongoClient(uri)
    client.admin.command('ping')
    logger.info("hello", extra={"hello": "jkl"})
    print("successfully connect to mongodb")
except pymongo.errors.OperationFailure:
    print("authentication failed of mongodb")
except Exception as e:
    print(e)