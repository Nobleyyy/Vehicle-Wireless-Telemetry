### Server Web ###

# Package Imports
import logging
import os
import yaml

# File Imports
from website import create_app

# Only show WARNING, ERROR and CRITICAL messages
logging.getLogger("werkzeug").setLevel(logging.WARNING)

# Crerate flask object
app = create_app()

# Constants
DEFAULT_IP = "127.0.0.1"
DEFAULT_WEB_PORT = 5000

## Functions ##
def load_config():
    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "config.txt"
    )

    with open(config_path, "r") as file:
        return yaml.safe_load(file) or {}

def run():
    config = load_config()

    # Use default IP if empty
    ip = config.get("server_ip") or DEFAULT_IP

    # Treat "localhost" as 127.0.0.1
    if ip.lower() == "localhost":
        ip = "127.0.0.1"

    # Use default port if empty
    web_port = config.get("server_web_port") or DEFAULT_WEB_PORT
    web_port = int(web_port)

    app.run(
        host=ip,
        port=web_port,
        debug=False,
        use_reloader=True,      # When file changes are made automatically reload the server
        threaded=True           # Multiple requests are handled in different threads
    )

## Main Program ##
if __name__ == '__main__':      # Starts the server if this file is run directly
    run()
