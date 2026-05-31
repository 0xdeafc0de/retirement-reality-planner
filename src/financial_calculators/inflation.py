"""Inflation-adjusted value calculations."""


def adjusted_value_after_inflation(
    present_value: float,
    annual_inflation_rate: float,
    years: float,
) -> float:
    """Return today's purchasing power after inflation erodes it over time.

    Rates are decimals, so 6% should be passed as 0.06.
    """
    if present_value < 0:
        raise ValueError("present_value must be non-negative")
    if annual_inflation_rate <= -1:
        raise ValueError("annual_inflation_rate must be greater than -100%")
    if years < 0:
        raise ValueError("years must be non-negative")

    return present_value / ((1 + annual_inflation_rate) ** years)


def future_cost_after_inflation(
    present_cost: float,
    annual_inflation_rate: float,
    years: float,
) -> float:
    """Return the future nominal cost of something that costs present_cost today."""
    if present_cost < 0:
        raise ValueError("present_cost must be non-negative")
    if annual_inflation_rate <= -1:
        raise ValueError("annual_inflation_rate must be greater than -100%")
    if years < 0:
        raise ValueError("years must be non-negative")

    return present_cost * ((1 + annual_inflation_rate) ** years)

