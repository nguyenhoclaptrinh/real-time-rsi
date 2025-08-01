# rsi/fetcher.py

import time
from rsi.calculator import compute_rsi
from rsi.storage import save_rsi_cache_to_file

price_cache = {}     # { "BTC/USDC_60": [(timestamp, price), ...] }
rsi_cache = {}       # { "BTC/USDC_60": [(timestamp, rsi), ...] }

def handle_price_update(data):
    token = data.get("pair").upper()
    price = float(data.get("priceUsd"))
    current_time = time.time()

    for interval in [1, 5, 30, 60]:
        key = f"{token}_{interval}"
        interval_start = int(current_time) // interval * interval

        # --- Price cache
        if key not in price_cache:
            price_cache[key] = []
        if not price_cache[key] or interval_start > price_cache[key][-1][0]:
            price_cache[key].append((interval_start, price))
        else:
            price_cache[key][-1] = (interval_start, price)

        # --- RSI cache
        if len(price_cache[key]) >= 15:
            rsi_val = compute_rsi(price_cache[key][-15:])
            if rsi_val is not None:
                if key not in rsi_cache:
                    rsi_cache[key] = []
                rsi_cache[key].append((interval_start, rsi_val))
                # Giới hạn
                if len(rsi_cache[key]) > 100:
                    rsi_cache[key] = rsi_cache[key][-100:]

    # Ghi ra file định kỳ (hoặc debounce sau này)
    save_rsi_cache_to_file(rsi_cache)
