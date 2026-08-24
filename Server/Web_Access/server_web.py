### Server Web ###
from website import create_app

app = create_app()

def run():
    app.run(debug=False)

if __name__ == '__main__':
    run()
