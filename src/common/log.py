import logging.config
import logging.handlers
from yaml import load, Loader
import atexit

with open("config/log.yml", "r") as f:
    c = load(f, Loader)

logging.config.dictConfig(c)
logging.basicConfig(level="INFO")

queue_handler: logging.handlers.QueueHandler = logging.getHandlerByName("queue_handler")
if queue_handler is not None:
    queue_handler.listener.start()
    atexit.register(queue_handler.listener.stop)
