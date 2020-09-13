import os
import uuid
import json
import hashlib

from docchain.config import config
from docchain.database import sqlite_db, User, Document, DocumentSigns

from flask import Flask, redirect, url_for, send_file, request, render_template, send_from_directory
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
        passports_path = os.path.join(images_path, PASSPORTS_DIR)

        if not os.path.exists(passports_path):
            os.mkdir(passports_path)

        image.save(os.path.join(passports_path, new_id))

        user.passport_id = new_id
        user.save()

        photos['passport'] = new_id
    
    if 'selfy' in request.files:
        image = request.files['selfy']
        new_id = str(uuid.uuid4())
        selfies_path = os.path.join(images_path, SELFIES_DIR)

        if not os.path.exists(selfies_path):
            os.mkdir(selfies_path)

        image.save(os.path.join(selfies_path, new_id))

        user.selfie_id = new_id
        user.save()

        photos['selfie'] = new_id

    if 'selfie' in photos and 'passport' in photos:
        return render_template('profile.html', status='wait_verify')

    return render_template('profile.html', status='need_photos')


@app.route("/my_documents")
def documents():
    user = get_user()

    documents = []

    for doc in Document.select().where(Document.user_id==user.id):
        document = {"id": doc.id, "name": f"Документ №{doc.id}"}
        signs = DocumentSigns.select().where(DocumentSigns.document_id==doc.id)

        for sign in signs:
            who = "user" if sign.signer_id == user.id else "other_user"

            document[who] = {
                "signed": sign.signed
            }

        documents.append(document)

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
    another_user_email = request.args.get("signer_mail")
    raise Exception(request.args)
    another_user = User.get_or_none(User.email == another_user_email)

    if another_user is None:
        raise Exception()
        return "Нет такого пользователя"
    DocumentSigns.create(document_id=document_id, signer_id=another_user.id)
    return "Отправлено"


@app.route("/docs/<doc_id>")
def get_doc(doc_id):
    path = os.path.join(config['DEFAULT']['images_path'], DOCUMENTS_DIR, str(doc_id))

    return send_file(path + '.pdf')


@app.route("/document_save", methods=["POST"])
def save_document():
    user = get_user()

    document_img = request.files['document']

    document_hash = hashlib.md5(document_img.stream.read()).hexdigest()
    document = Document.create(user=user, document_hash=document_hash)

    DocumentSigns.create(document_id=document.id, signer_id=user.id)

    documents_path = os.path.join(config["DEFAULT"]["images_path"], DOCUMENTS_DIR)
    if not os.path.exists(documents_path):
        os.mkdir(documents_path)

    document_img.save(os.path.join(documents_path, f"{document.id}.pdf"))

    return redirect("/my_documents")


if __name__ == "__main__":
    sqlite_db.create_tables([User, Document, DocumentSigns], safe=True)
    app.run(debug=config["DEFAULT"].getboolean("debug"))
