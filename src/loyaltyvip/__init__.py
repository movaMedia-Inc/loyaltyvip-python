"""LoyaltyVIP Python SDK — casino player intelligence API client.

See https://loyaltyvip.com/developers for docs.
"""

from .client import DEFAULT_BASE_URL, LoyaltyVIP, LoyaltyVIPError

__version__ = "1.0.0"
__all__ = ["LoyaltyVIP", "LoyaltyVIPError", "DEFAULT_BASE_URL", "__version__"]
