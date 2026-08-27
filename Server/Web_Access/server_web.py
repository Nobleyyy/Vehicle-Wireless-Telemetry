### Server Web ###

# Package Imports
import logging

# File Imports
from website import create_app

# Only show WARNING, ERROR and CRITICAL messages
logging.getLogger("werkzeug").setLevel(logging.WARNING)

# Crerate flask object
app = create_app()

## Functions ##
def run():
    app.run(
        debug=True,
        use_reloader=True,      # When file changes are made automatically reload the server
        threaded=True           # Multiple requests are handled in different threads
    )

## Main Program ##
if __name__ == '__main__':      # Starts the server if this file is run directly
    run()
