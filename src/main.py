import os
import sys
import django
from django.core.wsgi import get_wsgi_application
from flask import Flask, request, Response
from werkzeug.serving import WSGIRequestHandler

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payroll_backend.settings')

# Setup Django
django.setup()

# Get Django WSGI application
django_app = get_wsgi_application()

# Create Flask app as a wrapper
app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy_to_django(path):
    """Proxy all requests to Django WSGI application"""
    
    # Create a WSGI environ from Flask request
    environ = request.environ.copy()
    environ['PATH_INFO'] = '/' + path if path else '/'
    environ['SCRIPT_NAME'] = ''
    
    # Handle CORS for all requests
    def start_response(status, headers, exc_info=None):
        # Add CORS headers
        cors_headers = [
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With'),
            ('Access-Control-Allow-Credentials', 'true'),
        ]
        headers.extend(cors_headers)
        start_response.status = status
        start_response.headers = headers
    
    # Call Django WSGI app
    response_iter = django_app(environ, start_response)
    response_data = b''.join(response_iter)
    
    # Handle OPTIONS requests for CORS preflight
    if request.method == 'OPTIONS':
        response = Response('', status=200)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    # Create Flask response
    response = Response(
        response_data,
        status=int(start_response.status.split()[0]),
        headers=start_response.headers
    )
    
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

