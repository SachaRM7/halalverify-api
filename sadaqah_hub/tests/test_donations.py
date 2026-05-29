from models.donation import Donation
from models import db


def test_create_donation_via_form(app, client, first_charity):
    response = client.post('/donations', data={
        'donation_type': 'Sadaqah',
        'amount': '25.50',
        'currency': 'USD',
        'charity_id': str(first_charity.id),
        'charity_name': '',
        'date': '2026-04-21',
        'category': 'food',
        'note': 'Ramadan support',
    }, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        donation = Donation.query.first()
        assert donation is not None
        assert donation.charity_name == first_charity.name
        assert donation.amount == 25.50
