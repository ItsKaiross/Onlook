# from pyngrok import ngrok
from api import app
from api.scheduled_tasks.email_scheduler import start_email_scheduler
from api.public_users import post_response
from dotenv import load_dotenv
import os

load_dotenv()

# Configure database connection pool to prevent lock timeouts
if hasattr(app, 'config'):
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 280
    app.config['SQLALCHEMY_POOL_PRE_PING'] = True

port = 5001

# public_url = ngrok.connect(port)
# print(f" * ngrok tunnel: {public_url}")

# app.config["BASE_URL"] = public_url
#  use_reloader=False,~~
if __name__ == "__main__":
    start_email_scheduler()
    app.run(debug=True ,port=port)