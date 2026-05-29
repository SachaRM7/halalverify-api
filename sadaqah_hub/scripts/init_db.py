#!/usr/bin/env python3
from app import create_app, seed_charities
from models import db


def main() -> None:
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_charities()
        print('Database initialized successfully.')


if __name__ == '__main__':
    main()
