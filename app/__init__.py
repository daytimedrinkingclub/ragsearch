from flask import Flask, redirect, url_for
from config import Config
from flask_cors import CORS
from extensions import db, migrate
from app.routes.system_routes import system_bp
from app.routes.webhook_routes import webhook_bp
from app.models.system_model import System

def create_app(config_class=Config):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Import and register blueprints
    from app.routes.article_routes import article_bp
    from app.routes.chat_routes import chat_bp
    app.register_blueprint(system_bp)

    app.register_blueprint(article_bp, url_prefix='/article')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(webhook_bp, url_prefix='/webhook')

    @app.route('/')
    def home():
        return redirect(url_for('article.index'))

    @app.cli.command("seed-db")
    def seed_db():
        """Seed the database."""
        from app.seed import seed_database
        seed_database()

    @app.context_processor
    def inject_chatwoot_config():
        return dict(
            CHATWOOT_BASE_URL=app.config['CHATWOOT_BASE_URL'],
            CHATWOOT_WEBSITE_TOKEN=app.config['CHATWOOT_WEBSITE_TOKEN']
        )

    return app
