"""Run: python examples/quickstart.py  (no key needed for the directory)."""

import os

from loyaltyvip import LoyaltyVIP

lv = LoyaltyVIP(api_key=os.environ.get("LOYALTYVIP_API_KEY"))

res = lv.search_casinos(state="NV", has_rewards=True, limit=5)
print(f"Found {res.get('count', len(res['data']))} casinos; first 5:")
for c in res["data"]:
    print(f" - {c['name']} ({c.get('city')}, {c.get('state')})")

if os.environ.get("LOYALTYVIP_API_KEY"):
    print("\nYour tier status:")
    print(lv.player("tier_status"))
