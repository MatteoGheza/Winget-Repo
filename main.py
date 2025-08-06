import os
import sys

from flask import Flask, send_from_directory, url_for, redirect

from Modules.DevMode.Functions import generate_dev_certificate
from Modules.Functions import start_up_check
from Modules.Clients.Clients import client_bp
from Modules.Groups.Functions import groups_bp
from Modules.Login.Login import login_bp
from Modules.Settings.Settings import settings_bp
from Modules.Store.store import store_bp
from Modules.UI.UI import ui_bp
from Modules.User.User import user_bp
from Modules.Winget.Functions import get_winget_Settings
from Modules.Winget.winget_Routes import winget_routes
from Modules.API.API import api_bp

settings = get_winget_Settings(True)

app = Flask(__name__)
app.config['SERVERNAME'] = settings['SERVERNAME']
app.secret_key = settings['SECRET_KEY'].encode()
app.config['SESSION_COOKIE_NAME'] = app.config['SERVERNAME']
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['active_downloads'] = {}

# Set APPLICATION_ROOT if environment variable is provided
application_root = os.getenv('APPLICATION_ROOT')
if application_root:
    app.config['APPLICATION_ROOT'] = application_root

app.jinja_env.add_extension('jinja2.ext.do')

app.register_blueprint(login_bp, url_prefix='/')
app.register_blueprint(ui_bp, url_prefix='/ui')
app.register_blueprint(user_bp, url_prefix='/ui/user')
app.register_blueprint(groups_bp, url_prefix='/ui/groups')
app.register_blueprint(client_bp, url_prefix='/ui/clients')
app.register_blueprint(settings_bp, url_prefix='/ui/settings')
app.register_blueprint(store_bp, url_prefix='/ui/store')
app.register_blueprint(api_bp, url_prefix='/client/api')
app.register_blueprint(winget_routes, url_prefix='/api')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/images'),'favicon.png', mimetype='image/png')


@app.route('/')
def root():
    """Redirect root access to login page"""
    return redirect(url_for('login_bp.index'))


@app.context_processor
def global_settings():
    return {
        'app_name': app.config['SERVERNAME'],
        'app_logo': url_for('static', filename='images/logo.png')
    }


if __name__ == '__main__':
    start_up_check()

    # Docker-compatible configuration
    host = os.getenv('WINGET_HOST', '127.0.0.1')
    port = int(os.getenv('WINGET_PORT', '5000'))
    ssl_port = int(os.getenv('WINGET_SSL_PORT', '5443'))
    ssl_enabled = os.getenv('WINGET_SSL_ENABLED', 'false').lower() == 'true'
    dev_mode = os.getenv('WINGET_DEV_MODE', 'false').lower() == 'true'

    if len(sys.argv) > 1 and sys.argv[1] == "/dev" or dev_mode:
        status = generate_dev_certificate()
        if status:
            app.config['dev_mode'] = True
            print(f"Starting Winget-Repo in development mode on https://{host}:{ssl_port}")
            app.run(host=host, port=ssl_port, ssl_context=('SSL/cert.pem', 'SSL/key.pem'), threaded=True)
        else:
            print("Error while starting the development server! Please check the certificates!")
    elif ssl_enabled:
        print(f"Starting Winget-Repo with SSL on https://{host}:{ssl_port}")
        app.run(host=host, port=ssl_port, ssl_context=('SSL/cert.pem', 'SSL/key.pem'), threaded=True)
    else:
        print(f"Starting Winget-Repo on http://{host}:{port}")
        app.run(host=host, port=port, threaded=True)
