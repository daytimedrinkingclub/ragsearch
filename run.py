from app import create_app
from flask import Flask
from flask_migrate import Migrate
from extensions import db

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)