import pytest

from app import create_app
from models import db
from models.charity import Charity


@pytest.fixture()
def app():
    app = create_app({
        'TESTING': True,
        'SECRET_KEY': 'test',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'COMMUNITY_SYNC_ON_STARTUP': False,
        'COMMUNITY_SHARED_PASSPHRASE': 'test-pass',
    })
    with app.app_context():
        db.drop_all()
        db.create_all()
        from app import seed_charities
        seed_charities()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def first_charity(app):
    with app.app_context():
        return Charity.query.order_by(Charity.id.asc()).first()
