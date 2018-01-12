import json

from flask import Flask, redirect, request, render_template
from oauth2client.client import flow_from_clientsecrets

from config import GOOGLE_CLIENT_SECRETS_JSON, REGISTERED_CREDENTIALS_JSON


server_uri = 'http://localhost:5000'
app = Flask(__name__)
flow = flow_from_clientsecrets(
    GOOGLE_CLIENT_SECRETS_JSON,
    scope='https://mail.google.com',
    redirect_uri=server_uri + '/post_registration'
)

@app.route('/')
def index():
    """
    renders home page
    """

    return render_template('index.html')


@app.route('/register')
def register():
    """
    redirects to authorization url
    """

    authorization_url = flow.step1_get_authorize_url()
    return redirect(authorization_url)


def store_credentials(credentials):
    try:
        with open(REGISTERED_CREDENTIALS_JSON) as f:
            registered_credentials = json.load(f)
    except IOError:
        registered_credentials = []

    registered_credential = credentials.to_json()
    registered_credentials.append(registered_credential)

    with open(REGISTERED_CREDENTIALS_JSON, 'w') as f:
        json.dump(registered_credentials, f)


@app.route('/post_registration')
def post_registration():
    """
    renders post registration page
    """

    error = request.args.get('error', None)
    auth_code = request.args.get('code', None)

    if error is not None:
        return render_template('error.html', detail='I am sure you have your reasons...')

    if auth_code is None:
        return render_template('error.html', detail='Sorry! There were some problems. Please try again...')

    credentials = flow.step2_exchange(auth_code)
    store_credentials(credentials)
    return render_template('registered.html')

