from app import create_app
from app.models.system_model import System
from app.seed_data import seed_system_data
from extensions import db

def seed_database():
    app = create_app()
    with app.app_context():
        # Seed system data
        system_data = seed_system_data()
        for data in system_data:
            existing = System.query.filter_by(key=data['key']).first()
            if not existing:
                new_system = System(**data)
                db.session.add(new_system)
                print(f"Added new system data: {data['key']}")
            else:
                print(f"System data already exists: {data['key']}")
        
        db.session.commit()
        print("Database seeding completed.")