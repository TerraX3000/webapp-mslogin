from main_app import create_app
from main_app.config import Config
from main_app.config_msa import Config as config_msa

app = create_app(config_class=config_msa)

if __name__ == "__main__":
    app.run("localhost", 5000, debug=True)
