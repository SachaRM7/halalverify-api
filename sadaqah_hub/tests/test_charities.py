from models import db
from models.review import Review


def test_seeded_charities_exist(app):
    from models.charity import Charity
    with app.app_context():
        assert Charity.query.count() >= 20


def test_charity_detail_and_review_submission(app, client, first_charity):
    response = client.post(f'/charities/{first_charity.id}', data={
        'reviewer_name': 'Test User',
        'rating': '5',
        'review_text': 'Very transparent.',
    }, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        review = Review.query.filter_by(charity_id=first_charity.id).first()
        assert review is not None
        assert review.rating == 5
