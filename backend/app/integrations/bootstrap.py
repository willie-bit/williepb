"""Import-side-effect module: instantiate and register all adapters.

Kept separate so `get_registry()` can cheaply import it once. Add new adapters
by appending a `registry.register_*` line here.
"""

from __future__ import annotations

from app.integrations.banks.kb_kookmin import KBKookminBankAdapter
from app.integrations.banks.woori import WooriBankAdapter
from app.integrations.crypto.upbit import UpbitAdapter
from app.integrations.fx.ecos import ECOSFxAdapter
from app.integrations.market.gold import KRXGoldAdapter
from app.integrations.market.krx import KRXAdapter
from app.integrations.real_estate.molit import MOLITAdapter
from app.integrations.real_estate.reb import REBIndexAdapter
from app.integrations.registry import AdapterRegistry
from app.integrations.securities.kiwoom import KiwoomAdapter
from app.integrations.securities.nh_invest import NHInvestAdapter

registry = AdapterRegistry()

# Account adapters (본인계좌 동기화)
registry.register_account(KBKookminBankAdapter())
registry.register_account(WooriBankAdapter())
registry.register_account(KiwoomAdapter())
registry.register_account(NHInvestAdapter())
_upbit = UpbitAdapter()
registry.register_account(_upbit)

# Market quote adapters (시세)
registry.register_market(KRXAdapter())
registry.register_market(KRXGoldAdapter())
registry.register_market(_upbit)
registry.register_market(ECOSFxAdapter())

# Real estate
registry.register_realestate(REBIndexAdapter())
registry.register_realestate(MOLITAdapter())
