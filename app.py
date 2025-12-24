"""Main Flask application using Connexion 3.x with WSGI"""
import os
from connexion import App


def create_app():
    """Create and configure the Connexion Flask app"""
    # Create Connexion App (WSGI-based)
    connexion_app = App(
        __name__,
        specification_dir='specs/'
    )
    
    # Add API from swagger spec (register with middleware for reloader/book-keeping)
    connexion_app.add_api(
        'swagger.yaml',
        base_path='/api/v1',
        strict_validation=True,
        pythonic_params=True
    )

    
    # Get the underlying Flask app
    flask_app = connexion_app.app
    flask_app.config['JSON_SORT_KEYS'] = False
    
    return connexion_app


if __name__ == '__main__':
    connexion_app = create_app()
    # Run via uvicorn through Connexion's middleware (ASGI), which is the supported path in Connexion 3.x
    connexion_app.run(host='0.0.0.0', port=7878, reload=False)
