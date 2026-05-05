def test_list_charities(client):
    response = client.get('/api/charities')
    assert response.status_code == 200
    payload = response.get_json()
    assert isinstance(payload, list)
    assert len(payload) >= 20


def test_create_charity_requires_passphrase(client):
    response = client.post('/api/charities', json={'name': 'Blocked Charity'})
    assert response.status_code == 403


def test_create_charity_and_review(client, first_charity):
    response = client.post('/api/charities', headers={'X-Community-Passphrase': 'test-pass'}, json={
        'name': 'API Added Charity',
        'website': 'https://api.example.org',
        'registration_country': 'France',
        'cause_areas': 'water,food',
        'description': 'Added through API',
        'reports_json': ['https://api.example.org/report.pdf'],
    })
    assert response.status_code == 201
    review_response = client.post(f'/api/charities/{first_charity.id}/reviews', headers={'X-Community-Passphrase': 'test-pass'}, json={
        'reviewer_name': 'API User',
        'rating': 4,
        'review_text': 'Good reporting',
    })
    assert review_response.status_code == 201
    detail = client.get(f'/api/charities/{first_charity.id}')
    assert detail.status_code == 200
    assert 'reviews' in detail.get_json()
