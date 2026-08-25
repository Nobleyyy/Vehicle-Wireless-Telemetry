### Server Web ###

# File Imports
from website import create_app

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
