import sqlite3

from typing import Optional

from docchain.config import config
from peewee import Model, PrimaryKeyField, TextField, SqliteDatabase, BooleanField, ForeignKeyField

sqlite_db = SqliteDatabase(config['DEFAULT']['sqlite_path'])

class _BaseModel(Model):
    """A base model that will use our Sqlite database."""
    class Meta:
        database = sqlite_db

class User(_BaseModel):
    id = PrimaryKeyField(null=False)
    name = TextField(null=True)
    email = TextField()
    verified = BooleanField(default=False)
    passport_id = TextField(null=True)
    selfie_id = TextField(null=True)


class Document(_BaseModel):
    id = PrimaryKeyField(null=False)
    user = ForeignKeyField(User)
    other_user = ForeignKeyField(User)
