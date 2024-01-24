import connexion # type: ignore

from .encoder import JSONEncoder


def get_app() -> connexion.FlaskApp:
    app = connexion.App(__name__, specification_dir='./openapi/')
    app.app.json_encoder = JSONEncoder
    app.add_api('openapi.yaml', pythonic_params=True)
    return app
