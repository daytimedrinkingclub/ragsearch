from app import db

class Article(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    article_name = db.Column(db.String(1000), nullable=False)
    article_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __init__(self, id, article_name, article_content):
        self.id = id
        self.article_name = article_name
        self.article_content = article_content