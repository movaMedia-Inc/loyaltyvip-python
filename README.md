# loyaltyvip (Python)

Official Python client for the [LoyaltyVIP](https://loyaltyvip.com) API — the privacy-first casino player intelligence platform. Standard library only (no dependencies). Python 3.8+.

```bash
pip install loyaltyvip
```

```python
from loyaltyvip import LoyaltyVIP

lv = LoyaltyVIP()  # public directory needs no key
res = lv.search_casinos(state="NV", has_rewards=True, limit=5)
for c in res["data"]:
    print(c["name"], "-", c.get("city"), c.get("state"))

# Your own data needs a key (https://loyaltyvip.com/dashboard/developer):
import os
me = LoyaltyVIP(api_key=os.environ["LOYALTYVIP_API_KEY"])
print(me.player("tier_status"))
print(me.tax_report("generate_summary", tax_year=2025))  # scope: tax
```

Methods: `search_casinos`, `get_casino`, `list_rewards_programs`, `get_rewards_program` (public); `me`, `tiers`, `trips`, `offers`, `player`, `comp`, `predict`, `tier_match`, `tax_report` (API key). Errors raise `LoyaltyVIPError` (`status`, `code`, `message`, `docs`).

- Docs: https://loyaltyvip.com/developers
- OpenAPI 3.1: https://loyaltyvip.com/openapi.json
- Auth guide: https://loyaltyvip.com/auth.md

LoyaltyVIP is independent and not affiliated with any casino brand — a record-keeping and analytics tool, not a gambling product. MIT © movaMedia.
