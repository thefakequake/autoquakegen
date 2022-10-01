import requests
import websocket
import rel
import json
import time
import threading
import logging

logger = logging.getLogger("__main__")


class Bot:
    def __init__(self, **kwargs):
        self.token = kwargs["token"]
        self.properties = kwargs["properties"]
        self.user = kwargs["user"]
        self.intents = kwargs["intents"]
        self.ws = None
        self.connections = 0
        self.sequence = None

    def get_gateway(self):
        res = requests.get("https://discord.com/api/gateway")
        return res.json().get("url")

    def run(self):
        gateway = self.get_gateway()
        if gateway is None:
            raise Exception("Couldn't fetch API gateway.")
        self.connections += 1
        self.ws = websocket.WebSocketApp(
            gateway,
            on_open=self.on_open,
            on_close=self.on_close,
            on_message=self.on_message,
            on_error=self.on_error,
        )
        self.ws.run_forever(dispatcher=rel)
        rel.signal(2, rel.abort)
        rel.dispatch()

    def on_open(self, ws):
        logger.info(f"WebSocket connection {self.connections} established.")

    def on_close(self, close_status_code, close_msg):
        logger.info(
            f"WebSocket connection {self.connections} closed with code {close_status_code}x."
        )

    def on_error(self, ws, error):
        logger.error(error)
        self.close()

    def heartbeat(self, heartbeat_interval):
        logger.info("Started heartbeat loop.")
        while self.ws is not None:
            connections = self.connections
            time.sleep(heartbeat_interval / 1000)
            if self.connections != connections:
                return
            payload = {"op": 1, "d": self.sequence}
            self.ws.send(json.dumps(payload))
            logger.info(f"Heartbeat sent with seq {self.sequence}.")

    def close(self, ws):
        self.ws.close()
        self.ws = None

    def identify(self):
        payload = json.dumps(
            {
                "op": 2,
                "d": {
                    "token": self.token,
                    "properties": self.properties,
                    "capabilities" if self.user else "intents": self.intents,
                    "presence": {
                        "status": "offline",
                        "since": 0,
                        "afk": False,
                    },
                    "compress": False,
                },
            }
        )

        self.ws.send(payload)
        logger.info("Sent identify payload.")

    def on_message(self, ws, message):
        data = json.loads(message)

        match data["op"]:
            case 0:
                self.sequence = data.get("s")
                if data["t"] == "READY":
                    logger.info("READY event received.")
            case 7:
                self.close()
                self.run()
            case 9:
                self.identify()
            case 10:
                threading.Thread(
                    target=self.heartbeat,
                    args=(data["d"]["heartbeat_interval"],),
                    daemon=True,
                ).start()
                self.identify()
            case 11:
                logger.info("Heartbeat ACK received.")

    def set_pfp(self, data, filename):
        headers = {
            "user-agent": self.properties.get(
                "browser_user_agent",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
            ),
            "authorization": self.token,
            "content-type": "application/json",
        }

        res = requests.patch(
            "https://discord.com/api/v9/users/@me",
            headers=headers,
            json={"avatar": data},
        )
        if res.status_code == 200:
            logger.info(f"Changed profile picture to {filename}.")
