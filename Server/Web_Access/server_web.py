### Server Web ###
from website import create_app

app = create_app()

def run():
    app.run(
        debug=True,
        use_reloader=True,
        threaded=True
    )

if __name__ == '__main__':
    run()
