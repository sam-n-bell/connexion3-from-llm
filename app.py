"""Pure ASGI application using Connexion 3.x

Connexion 3.x ASGI app without Flask backend - uses Starlette directly.
"""
import pathlib
from connexion import AsyncApp

# Get the directory containing this file
basedir = pathlib.Path(__file__).parent.resolve()

# Create Connexion AsyncApp (pure ASGI)
app = AsyncApp(
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


if __name__ == '__main__':
    # For development
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=7878)
