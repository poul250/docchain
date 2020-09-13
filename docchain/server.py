import os
import uuid
import json
import hashlib

from docchain.config import config
from docchain.database import sqlite_db, User, Document

from flask import Flask, redirect, url_for, send_file, request, render_template
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


def get_user():
    google_data = google.get("/oauth2/v1/userinfo?alt=json").json()
    user, created = User.get_or_create(email=google_data['email'])
    if created:
        user.name = google_data['name']
        user.save()
    
    return user


def get_documents():
    user = get_user()
    documents = Document.select(user == user)


def verification_page(user_data):
    user = get_user()

    if user.verified:
        return render_template('profile.html', status='good')
    
    if not user.passport_id or not user.selfie_id:
        return render_template('profile.html', status='need_photos')

    # hack for now
    user.verified = True
    user.save
    return render_template('profile.html', status='good')


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/google_auth")
def auth_google():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v1/userinfo?alt=json")
    assert resp.ok, resp.text
    # return verification_page(resp.json())
    return redirect('/profile')


@app.route("/profile")
def profile():
    user = get_user()

    if user.verified:
        return render_template('profile.html', status='good')
    
    if not user.passport_id or not user.selfie_id:
        return render_template('profile.html', status='need_photos')

    # hack for now
    user.verified = True
    user.save
    return render_template('profile.html', status='good')


@app.route("/save_images", methods=["POST"])
def profile_save_images():
    user = get_user()
    images_path = config['DEFAULT']['images_path']

    photos = {}
    if user.passport_id:
        photos['passport'] = user.passport_id
    if user.selfie_id:
        photos['selfy'] = user.selfie_id

    if 'passport' in request.files:
        image = request.files['passport']
        new_id = str(uuid.uuid4())
        image.save(os.path.join(images_path, PASSPORTS_DIR, new_id))

        user.passport_id = new_id
        user.save()

        photos['passport'] = new_id
    
    if 'selfy' in request.files:
        image = request.files['selfy']
        new_id = str(uuid.uuid4())
        image.save(os.path.join(images_path, SELFIES_DIR, new_id))

        user.selfie_id = new_id
        user.save()

        photos['selfie'] = new_id

    if 'selfie' in photos and 'passport' in photos:
        return render_template('profile.html', status='wait_verify')

    return render_template('profile.html', status='need_photos')


@app.route("/my_documents")
def documents():
    user = get_user()

    # TODO: get from database
    documents = [
        {
            "name": "Продажа квартиры",
            "user": {
                "signed": False,
            }
        },
        {
            "name": "Продажа собаки",
            "user": {
                "signed": False,
            },
            "other_user": {
                "signed": False
            }
        },
        {
            "name": "аренда вдски на месяц",
            "user": {
                "signed": True,
            },
            "other_user": {
                "signed": False
            }
        },
        {
            "name": "Оплата пятерки по матану",
            "user": {
                "signed": True,
            },
            "other_user": {
                "signed": True
            }
        }
    ]

    return render_template('my_documents.html', documents=documents)


@app.route("/sign_documents")
def sign_requests():
    return render_template('sign_documents.html')


@app.route("/sign", methods=["POST"])
def sign():
    document_id = request.args.get("document_id")
    return f'{{status": "OK", "document_id": {document_id}}}'


@app.route("/request_sign", methods=["POST"])
def request_sign():
    document_id = request.args.get("document_id")
    another_user_email = request.args.get("user_email")


    return f'{{"document_id": {document_id}, "user_mail": {another_user_email}}}'


@app.route("/create_doc")
def load_image():
    new_id = str(uuid.uuid4())
    document_img = request.files['document']
    document_img.save(os.path.join(config["DEFAULT"]["images_path"], DOCUMENTS_DIR, new_id))

    return json.dumps({"document_id": new_id})


if __name__ == "__main__":
    sqlite_db.create_tables([User, Document], safe=True)
    app.run(debug=config["DEFAULT"].getboolean("debug"))
