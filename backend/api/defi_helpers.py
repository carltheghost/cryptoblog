SWAP_RATES = {"ETH": 3456.72, "USDC": 1.0, "TRD": 0.2457, "MGANGA": 1.0, "MWANJESA": 0.98, "BTC": 68432.18}

DEFAULT_TOKENS = {
    "ETH": 5.42,
    "USDC": 4200.0,
    "TRD": 12500.0,
    "MWANJESA": 0.0,
}


def get_token_balances(wallet) -> dict:
    balances = dict(DEFAULT_TOKENS)
    if wallet.token_balances:
        balances.update(wallet.token_balances)
    balances["MWANJESA"] = wallet.mwanjesa_balance
    return balances


def set_token_balance(wallet, symbol: str, amount: float) -> None:
    balances = get_token_balances(wallet)
    balances[symbol.upper()] = max(0, amount)
    if symbol.upper() == "MWANJESA":
        wallet.mwanjesa_balance = max(0, amount)
    wallet.token_balances = {k: v for k, v in balances.items() if k != "MWANJESA"}


def swap_tokens(wallet, from_token: str, to_token: str, amount: float) -> tuple[float, float]:
    from_token = from_token.upper()
    to_token = to_token.upper()
    balances = get_token_balances(wallet)
    if balances.get(from_token, 0) < amount:
        raise ValueError(f"Insufficient {from_token}")
    from_rate = SWAP_RATES.get(from_token, 1.0)
    to_rate = SWAP_RATES.get(to_token, 1.0)
    output = (amount * from_rate / to_rate) * 0.997
    balances[from_token] -= amount
    balances[to_token] = balances.get(to_token, 0) + output
    wallet.token_balances = {k: v for k, v in balances.items() if k != "MWANJESA"}
    wallet.mwanjesa_balance = balances.get("MWANJESA", wallet.mwanjesa_balance)
    return output, from_rate / to_rate
