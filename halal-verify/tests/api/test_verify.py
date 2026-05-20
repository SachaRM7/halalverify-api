import pytest


@pytest.mark.asyncio
async def test_verify_barcode_returns_seeded_item(client):
    response = await client.get('/v1/verify/barcode/040000001001')
    assert response.status_code == 200
    payload = response.json()
    assert payload['name'] == 'Snickers Bar'
    assert payload['status'] == 'halal'
    assert payload['sources'][0]['verified'] is True


@pytest.mark.asyncio
async def test_verify_barcode_404_for_unknown_code(client):
    response = await client.get('/v1/verify/barcode/999999999999')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Barcode not found'


@pytest.mark.asyncio
async def test_submission_and_report_flow(client):
    search_response = await client.get('/v1/search', params={'q': 'Snickers'})
    item_id = search_response.json()['items'][0]['item_id']

    submission_response = await client.post(
        '/v1/submissions',
        json={
            'submitted_by': 'tester',
            'submitted_data': {'name': 'New Chocolate', 'status': 'unknown'},
        },
    )
    assert submission_response.status_code == 201
    assert submission_response.json()['status'] == 'pending'

    report_response = await client.post(
        '/v1/reports',
        json={
            'item_id': item_id,
            'reporter_id': 'tester',
            'reason': 'Packaging changed recently',
        },
    )
    assert report_response.status_code == 201
    assert report_response.json()['status'] == 'open'
