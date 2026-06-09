PAIR_PRICES = {
    "BTC/USDT": 68432.18,
    "ETH/USDT": 3456.72,
    "TRD/USDT": 0.2457,
    "SOL/USDT": 178.34,
    "BNB/USDT": 612.50,
}


def pair_price(pair: str) -> float:
    return PAIR_PRICES.get(pair.upper(), 1.0)


def order_notional(amount: float, price: float) -> float:
    return round(amount * price, 4)


def apply_buy(account, amount: float, price: float, market: bool) -> float:
    cost = order_notional(amount, price)
    if account.mganga_balance < cost:
        raise ValueError("Insufficient MGANGA balance")
    account.mganga_balance -= cost
    return cost


def apply_sell(account, amount: float, price: float) -> float:
    proceeds = order_notional(amount, price)
    account.mganga_balance += proceeds
    return proceeds
