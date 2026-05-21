import traceback
import sys
from dotenv import load_dotenv
import os

load_dotenv()

# This forces the real error to show in logs
import api as _api_module

app = _api_module.app  # Vercel can see `app` at module level

if hasattr(app, 'config'):
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 280
    app.config['SQLALCHEMY_POOL_PRE_PING'] = True

port = 5001

if __name__ == "__main__":
    from api.scheduled_tasks.email_scheduler import start_email_scheduler
    start_email_scheduler()
    app.run(debug=True, port=port)