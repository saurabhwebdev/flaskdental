from urllib.parse import urlencode
from flask import url_for

def update_url_query(request, **new_params):
    """Update URL query parameters while preserving existing ones."""
    args = request.args.copy()
    
    for key, value in new_params.items():
        if value is not None:
            args[key] = value
        elif key in args:
            del args[key]
            
    return f"{request.path}?{urlencode(args)}" if args else request.path
