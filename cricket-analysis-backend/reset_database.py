import os
from flask import Flask

from config import Config
from models import db


def create_app():
    """Create a lightweight Flask app just for DB management."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app


def drop_all_tables():
    """Drop every table in the configured cricket analysis database."""
    app = create_app()

    with app.app_context():
        db.reflect()
        tables = list(db.metadata.tables.keys())

        if not tables:
            print("No tables found. Database is already empty.")
            return

        db.drop_all()
        print("Dropped tables:")
        for table_name in tables:
            print(f" - {table_name}")


if __name__ == "__main__":
    confirm = input(
        "WARNING: This will remove every table from the configured cricket analysis "
        "database. Type 'DELETE' to continue: "
    ).strip()

    if confirm != "DELETE":
        print("Aborted. No changes were made.")
        raise SystemExit(1)

    drop_all_tables()
    print("Database cleanup completed successfully.")

