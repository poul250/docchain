import os
import uuid
import json

from docchain.config import config

from flask import Flask, redirect, url_for, send_file, request
from flask_dance.contrib.google import make_google_blueprint, google


PASSPORTS_DIR = 'passports'
SELFIES_DIR = 'selfies'
DOCUMENTS_DIR = 'documents'


app = Flask(__name__)
app.secret_key = "supersekrit"
blueprint = make_google_blueprint(
    client_id=config["GOOGLE"]["client_id"],
    client_secret=config["GOOGLE"]["secret"],
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


@app.route("/profile/save_images", methods=["POST"])
def profile_save_images():
    passport_image = request.files['passport']
    selfie_image = request.files['selfie']

    passport_uuid = uuid.uuid4()
    selfie_uuid = uuid.uuid4()

    file.save(os.path.join(config["DEFAULT"]["images_path"], PASSPORTS_DIR))
    return "wait profile verification page"


@app.route("/my_documents")
def documents():
    return "my documents page"


@app.route("/sign_documents")
def sign_requests():
    return "sign requests page"


@app.route("/sign", methods=["POST"])
def sign():
    document_id = request.args.get("document_id")
    return f'{{status": "OK", "document_id": {document_id}}}'


@app.route("/request_sign", methods=["POST"])
def request_sign():
    document_id = request.args.get("document_id")
    user_mail = request.args.get("user_mail")
    return f'{{"document_id": {document_id}, "user_mail": {user_mail}}}'


@app.route("/doc")
def load_image():
    _id = str(uuid.uuid4())
    file = request.files['pasport']
    file.save(os.path.join(config["DEFAULT"]["images_path"], _id))
    return json.dumps({"doc_id": _id})


@app.route("/get_pasport/<id>", methods=['GET', 'POST', 'PUT'])
def get_image(id):
    return send_file(id)


if __name__ == "__main__":
    app.run(debug=config["DEFAULT"].getboolean("debug"))
