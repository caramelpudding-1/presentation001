from dataclasses import dataclass

@dataclass
class SettlementResult:
    minutes_billable: int
    amount: float
    store_share: float
    protocol_fee: float

def calc_settlement(metered_minutes: int, free_minutes: int, price_per_min: float, store_share_rate: float) -> SettlementResult:
    minutes_billable = max(0, metered_minutes - free_minutes)
    amount = round(minutes_billable * float(price_per_min), 2)
    store_share = round(amount * store_share_rate, 2)
    protocol_fee = round(amount - store_share, 2)
    return SettlementResult(minutes_billable, amount, store_share, protocol_fee)
