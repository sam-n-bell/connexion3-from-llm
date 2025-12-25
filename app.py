"""Main Flask application using Connexion 3.x

Connexion 3.x is ASGI-first and works best with uvicorn/gunicorn+uvicorn.
"""
import os
import pathlib
from connexion import App

# Get the directory containing this file
basedir = pathlib.Path(__file__).parent.resolve()

# Create Connexion App (ASGI with Flask backend)
app = App(
    __name__,
    specification_dir=str(basedir / 'specs')
)

# Add API from OpenAPI spec
app.add_api(
    'swagger.yaml',
    base_path='/api/v1',
    strict_validation=True,
    pythonic_params=True
)

# Configure the underlying Flask app
app.app.config['JSON_SORT_KEYS'] = False


if __name__ == '__main__':
    # For development
    app.run(host='0.0.0.0', port=7878)
