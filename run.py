import api as _api_module
app = _api_module.app

if hasattr(app, 'config'):
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 280
    app.config['SQLALCHEMY_POOL_PRE_PING'] = True

port = 5001

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    from api.scheduled_tasks.email_scheduler import start_email_scheduler
    start_email_scheduler()
    app.run(debug=True, port=port)
