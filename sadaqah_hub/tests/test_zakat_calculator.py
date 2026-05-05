from services.zakat_calculator import calculate_zakat_due


def test_zakat_due_when_above_nisab():
    assert calculate_zakat_due(10000, 1000, 5000) == 225.0


def test_zakat_due_when_below_nisab():
    assert calculate_zakat_due(3000, 0, 5000) == 0.0
