_model = None


def load(params: dict):
    global _model
    _model = params


def model_version() -> str:
    return _model["version"]


def score(amount_usd: int, term_months: int) -> float:
    """Placeholder credit model: larger amounts and longer terms are riskier."""
    risk = (
        _model["intercept"]
        + (amount_usd / 5000) * _model["amount_weight"]
        + (term_months / 24) * _model["term_weight"]
    )
    return round(min(max(risk, 0.0), 1.0), 4)
