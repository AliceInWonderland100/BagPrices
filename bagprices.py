import re
from urllib.request import Request, urlopen


USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
)


def _fetch_currency_rate(currency: str, target: str) -> float:
    """Return conversion rate from ``currency`` to ``target``.

    Raises ValueError if the rate cannot be parsed.
    """
    url = (
        f"https://www.xe.com/currencyconverter/convert/?Amount=1&From="
        f"{currency}&To={target}"
    )
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req) as resp:
        html = resp.read().decode()

    match = re.search(
        r'class="unit-rates___StyledDiv-sc-1dk593y-0 dEqdnx"[^>]*>\s*<p>([^<]+)</p>',
        html,
        re.S,
    )
    if not match:
        raise ValueError("could not locate rate container")
    numbers = re.findall(r"[0-9.]+", match.group(1))
    if len(numbers) < 2:
        raise ValueError("unexpected rate format")
    second_number = float(numbers[1])
    return 1 / second_number


def convert_one_currency_to_usd(currency: str) -> float:
    return _fetch_currency_rate(currency, "USD")


def convert_one_currency_to_cny(currency: str) -> float:
    return _fetch_currency_rate(currency, "CNY")


def get_prada_global_prices(product_code: str, product_code_eu: str,
                             product_code_jp: str, product_name: str):
    """Return price list for multiple regions.

    Each entry of the returned list is (location, price_in_usd).
    """
    loc_list = ["US", "CA", "JP", "FR", "UK", "IT", "HK", "CN"]
    url_list = [
        f"https://www.prada.com/us/en/products.{product_name}.{product_code}..html",
        f"https://www.prada.com/ca/en/products.{product_name}.{product_code}..html",
        f"https://www.prada.com/jp/ja/products.{product_name}.{product_code_jp}..html",
        f"https://www.prada.com/fr/fr/products.{product_name}.{product_code_eu}..html",
        f"https://www.prada.com/gb/en/products.{product_name}.{product_code_eu}..html",
        f"https://www.prada.com/it/it/products.{product_name}.{product_code_eu}..html",
        f"https://www.prada.com/hk/hk/products.{product_name}.{product_code_jp}..html",
        f"https://www.prada.com/cn/zh/products.{product_name}.{product_code}..html",
    ]
    cur_list = ["USD", "CAD", "JPY", "EUR", "GBP", "EUR", "HKD", "CNY"]

    results = []
    for loc, url, currency in zip(loc_list, url_list, cur_list):
        req = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(req) as resp:
            html = resp.read().decode()
        match = re.search(
            r'class="info-card-component__basic-info-price"[^>]*>([^<]+)<',
            html,
            re.S,
        )
        if not match:
            raise ValueError(f"price container not found for {loc}")
        price_string = match.group(1).strip()
        number_match = re.search(r"([0-9.,]+)", price_string)
        if not number_match:
            raise ValueError(f"unable to parse price for {loc}")
        number = round(float(number_match.group(1).replace(",", "").replace(".", "")))
        usd_price = round(number * convert_one_currency_to_usd(currency))
        results.append((loc, usd_price))
    return results
