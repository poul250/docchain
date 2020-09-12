import os
import uuid
import json

import docchain.config as config

from flask import Flask, redirect, url_for, send_file, request
from flask_dance.contrib.google import make_google_blueprint, google


app = Flask(__name__)
app.secret_key = "supersekrit"
blueprint = make_google_blueprint(
    client_id=config.GOOGLE_CLIENT_ID,
    client_secret=config.GOOGLE_SECRET,
    scope=["profile", "email"]
)
app.register_blueprint(blueprint, url_prefix="/login")


def verification_page(user_data):
    return user_data


@app.route("/")
def index():
    return "index page"


@app.route("/auth")
def auth():
    return "You can auth with google account"


@app.route("/auth/google")
def auth_google():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v1/userinfo?alt=json")
    assert resp.ok, resp.text
    return verification_page(resp.json())


@app.route("/profile")
def profile():
    return "profile page"


@app.route("/my_documents")
def documents():
    return "my documents page"


@app.route("/sign_requests")
def sign_requests():
    return "sign requests page"


@app.route("/sign?document_id=<document_id>")
def sign():
    return '{"status": "OK"}'


@app.route("/request_sign?document_id=<document_id>&user_mail=<user_mail>")
def request_sign():
    return '{"status": "OK"}'


@app.route("/doc", methods=['GET', 'POST', 'PUT'])
def load_image():
    _id = str(uuid.uuid4())
    file = request.files['pasport']
    file.save(os.path.join(config.IMAGES_PATH, _id))
    return json.dumps({"doc_id": _id})


@app.route("/get_pasport/<id>", methods=['GET', 'POST', 'PUT'])
def get_image(id):
    return send_file(id)


if __name__ == "__main__":
    app.run(debug=True)
