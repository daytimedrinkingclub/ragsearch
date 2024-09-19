from flask import Flask
from config import Config
from extensions import db, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Import and register blueprints
    from app.routes.chat_routes import chat_bp
    from app.routes.article_routes import article_bp
    from app.routes.embedding_routes import embedding_bp

    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(article_bp, url_prefix='/article')
    app.register_blueprint(embedding_bp, url_prefix='/embedding')

    return app