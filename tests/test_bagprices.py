import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import bagprices

class DummyResp:
    def __init__(self, text, status=200):
        self.content = text.encode()
        self.text = text
        self.status_code = status
    def read(self):
        return self.content
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass
    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError('bad status')


def test_fetch_currency_rate(monkeypatch):
    html = '<div class="unit-rates___StyledDiv-sc-1dk593y-0 dEqdnx"><p>1 EUR = 1.1 USD</p></div>'
    monkeypatch.setattr(bagprices, "urlopen", lambda req: DummyResp(html))
    rate = bagprices._fetch_currency_rate("EUR", "USD")
    assert abs(rate - (1/1.1)) < 1e-6


def test_fetch_currency_rate_missing(monkeypatch):
    monkeypatch.setattr(bagprices, "urlopen", lambda req: DummyResp("<html></html>"))
    try:
        bagprices._fetch_currency_rate("EUR", "USD")
    except ValueError:
        pass
    else:
        assert False, "ValueError not raised"


def test_get_prada_global_prices(monkeypatch):
    def dummy_get(req):
        return DummyResp('<div class="info-card-component__basic-info-price">$1,234</div>')
    monkeypatch.setattr(bagprices, "urlopen", dummy_get)
    monkeypatch.setattr(bagprices, "convert_one_currency_to_usd", lambda cur: 1)
    result = bagprices.get_prada_global_prices('pc', 'pc', 'pc', 'name')
    assert len(result) == 8
    assert all(price == 1234 for _, price in result)
