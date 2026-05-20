from __future__ import annotations


def calculate_zakat_due(assets: float, liabilities: float, nisab_threshold: float) -> float:
    net_assets = max((assets or 0.0) - (liabilities or 0.0), 0.0)
    if net_assets < (nisab_threshold or 0.0):
        return 0.0
    return round(net_assets * 0.025, 2)
