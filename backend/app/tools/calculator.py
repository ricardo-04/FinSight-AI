"""Financial calculation utilities."""

def growth_rate(current: float, previous: float) -> float:
    return (current - previous) / previous * 100

def gross_margin(revenue: float, cogs: float) -> float:
    return (revenue - cogs) / revenue * 100
