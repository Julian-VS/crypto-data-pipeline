import requests
import json
import os

BASE_URL = "https://api.binance.com/api/v3/klines"
BRONZE_DIR = "bronze"


def fetch_klines(symbol: str, interval: str, startTime: int | None = None, limit: int = 1000):
    """
    Trae velas OHLCV desde Binance.
    """
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    if startTime is not None:
        params["startTime"] = startTime

    response = requests.get(BASE_URL, params=params)
    data = response.json()
    return data


def save_to_bronze(symbol: str, interval: str, klines: list) -> str:
    """
    Guarda un batch crudo de velas en bronze.
    Nombre: {symbol}_{interval}_{start_ts}_{end_ts}.json
    """
    if not klines:
        raise ValueError("No hay velas para guardar (lista vacía)")

    start_ts = klines[0][0]   # open_time de la primera vela del batch
    end_ts = klines[-1][6]    # close_time de la última vela del batch

    ticker_dir = os.path.join(BRONZE_DIR, symbol)
    os.makedirs(ticker_dir, exist_ok=True)

    filename = f"{symbol}_{interval}_{start_ts}_{end_ts}.json"
    filepath = os.path.join(ticker_dir, filename)

    with open(filepath, "w") as f:
        json.dump(klines, f)

    return filepath


def backfill_symbol(symbol: str, interval: str = "1d"):
    start_ts = 0

    while True:
        print(f"Pidiendo desde start_ts={start_ts}...")  # ← agregá esto
        klines = fetch_klines(symbol, interval, startTime=start_ts, limit=1000)
        print(f"Recibidas {len(klines)} velas")  # ← y esto

        if len(klines) == 0:
            print("No hay más datos. Backfill completo.")
            break

        save_to_bronze(symbol, interval, klines)
        print(f"Guardado batch: {len(klines)} velas, hasta {klines[-1][6]}")

        start_ts = klines[-1][6]


if __name__ == "__main__":
    backfill_symbol("BTCUSDT", "1d")
    