from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
db.init_app(app)

def setup_create():
    """Create the table. Only used to initialize the database."""
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    setup_create()
