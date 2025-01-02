from app import create_app, db
from app.seed import seed_data
from app.models import Room
from datetime import datetime

app = create_app()

def initialize_db(app):
    with app.app_context():
        db.create_all() # Create tables for our models
        print("Database initialized!")

        # Seed initial data
        if not Room.query.first():
            seed_data()
            print("Initial data has been seeded.")


if __name__ == "__main__":   
    initialize_db(app)

    app.run(host='0.0.0.0', port=5000)
