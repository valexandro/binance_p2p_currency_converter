class OffersNotFoundError(Exception):
    """Offers not found in JSON."""

    pass


class BinanceApiError(Exception):
    """Api available but failed to process request."""

    pass


class ApiUnavailableError(Exception):
    """Api unavailable."""

    pass
