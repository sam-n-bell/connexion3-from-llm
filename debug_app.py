"""Debug script to test app creation"""
import os
from connexion import App

print(f"Current working directory: {os.getcwd()}")
print(f"Specs directory exists: {os.path.exists('specs')}")
print(f"swagger.yaml exists: {os.path.exists('specs/swagger.yaml')}")

# Create Connexion App
print("\nCreating App...")
connexion_app = App(
    __name__,
    specification_dir='specs/'
)

print("Adding API (middleware)...")
try:
    result = connexion_app.add_api(
        'swagger.yaml',
        base_path='/api/v1',
        strict_validation=True,
        pythonic_params=True
    )
    print(f"middleware.add_api returned: {result}")
except Exception as e:
    print(f"ERROR adding API via middleware: {e}")
    import traceback
    traceback.print_exc()

print("Adding API (Flask blueprint via _middleware_app)...")
try:
    from connexion.middleware import main as _cm
    spec = _cm.Specification.load('specs/swagger.yaml')
    result2 = connexion_app._middleware_app.add_api(
        spec,
        base_path='/api/v1',
        strict_validation=True,
        pythonic_params=True
    )
    print(f"flask_app.add_api returned: {result2}")
except Exception as e:
    print(f"ERROR adding API via _middleware_app: {e}")
    import traceback
    traceback.print_exc()

# Get the underlying Flask app
flask_app = connexion_app.app

# Print all registered routes
print("\nRegistered routes:")
for rule in flask_app.url_map.iter_rules():
    print(f"  {rule.endpoint}: {rule.rule} [{', '.join(rule.methods)}]")

# Check connexion APIs
print(f"\nConnexion app APIs: {connexion_app.apis if hasattr(connexion_app, 'apis') else 'N/A'}")

# Try to test with test client
if len(list(flask_app.url_map.iter_rules())) > 1:
    client = flask_app.test_client()
    response = client.get('/api/v1/health')
    print(f"\nTest GET /api/v1/health:")
    print(f"  Status: {response.status_code}")
    print(f"  Data: {response.data}")
else:
    print("\nSkipping test - no API routes registered!")
