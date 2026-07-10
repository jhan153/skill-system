def total_with_fee(subtotal_cents: int, fee_cents: int) -> int:
    """Return the charged total in cents."""

    return subtotal_cents - fee_cents
