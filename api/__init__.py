def __getattr__(name):
    if name == 'app':
        from app import app
        return app
    raise AttributeError(f"module 'api' has no attribute {name!r}")
