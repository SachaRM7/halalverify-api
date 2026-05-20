import pytest


@pytest.mark.asyncio
async def test_search_returns_paginated_results(client):
    response = await client.get('/v1/search', params={'q': 'halal', 'page': 1, 'page_size': 10})
    assert response.status_code == 200
    payload = response.json()
    assert payload['page'] == 1
    assert payload['page_size'] == 10
    assert payload['total'] >= 1
    assert any(item['name'] == 'Sakura Tokyo Halal Ramen' for item in payload['items'])


@pytest.mark.asyncio
async def test_stats_returns_counts(client):
    response = await client.get('/v1/stats')
    assert response.status_code == 200
    payload = response.json()
    assert payload['total_items'] >= 3
    assert payload['by_type']['food'] >= 1
    assert 'halal' in payload['by_status']
