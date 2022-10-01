from datetime import datetime, timedelta, time
from time import sleep
import os
import threading
import secret
from discord import Gateway
from image import generate
from json import load, JSONDecodeError
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S"
    )
)

logger.addHandler(handler)

if not os.path.exists("pfps"):
    os.makedirs("pfps")

try:
    with open("config.json", "r") as file:
        config = load(file)
except FileNotFoundError:
    raise Exception("Could not find config.json")
except JSONDecodeError:
    raise Exception("Could not parse config.json")

bot = Gateway(
    token=config["token"],
    properties=config.get("properties", {}),
    user=config.get("user", False),
    intents=config.get("intents", 0)
)

def day_loop():
    while True:
        now = datetime.now()
        midnight = datetime.combine(now.date(), time()) + timedelta(days=1)
        until_midnight = midnight - now

        logger.info(f"Sleeping until {midnight}.")
        sleep(until_midnight.seconds)

        if bot.ws is None:
            return

        file_name = f"pfps/{midnight.strftime('%d-%m-%y')}.png"
        image = generate(file_name)
        bot.set_pfp(image, file_name)
        sleep(10)


threading.Thread(target=day_loop, daemon=True).start()

bot.run()
