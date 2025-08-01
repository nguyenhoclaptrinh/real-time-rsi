# app/routes/rsi.py
from flask import Blueprint, request, jsonify
from rsi.fetcher import price_cache
from rsi.calculator import compute_rsi
from rsi.ws_client import subscribe_pair, unsubscribe_pair
from rsi.storage import load_rsi_cache_from_file
import os
import json

bp = Blueprint("rsi", __name__)

@bp.route("/rsi_history")
def get_rsi_history():
    token = request.args.get("token")
    interval = request.args.get("interval") # Đây là string, cần chuyển sang int nếu dùng trong key
    
    if not token or not interval:
        return jsonify([]) # Trả về rỗng nếu thiếu tham số

    key = f"{token.upper()}_{interval}" # Tạo key khớp với rsi_cache
    
    all_data = load_rsi_cache_from_file() # Tải toàn bộ cache từ file

    # Lấy dữ liệu lịch sử cho token và interval cụ thể
    # rsi_cache lưu trữ dưới dạng [(timestamp, rsi_value), ...]
    history_list = all_data.get(key, [])
    
    # Chỉ trả về 100 điểm cuối cùng
    # (Nếu bạn muốn trả full data cho history, bỏ [-100:] đi)
    print(history_list)
    return jsonify(history_list[-100:]) 

@bp.route("/unsubscribe")
def unsubscribe():
    token = request.args.get("token")
    unsubscribe_pair(token)
    return jsonify({"status": "success"})

@bp.route("/rsi")
def get_rsi():
    tokens = request.args.get("tokens", "BTC/USDC")
    interval = int(request.args.get("interval", 60))

    for token in tokens.split(","):
        subscribe_pair(token.strip().upper())  # 🔁 Đăng ký từng cặp
    
    results = {}
    for pair in tokens.split(","):
        pair = pair.strip().upper()
        key = f"{pair}_{interval}"
        
        if key not in price_cache or len(price_cache[key]) < 15:  # Cần ít nhất 14 khung + 1 giá mới
            continue
            
        # Lấy dữ liệu 14 khung gần nhất + giá hiện tại
        price_data = price_cache[key][-15:]
        rsi_val = compute_rsi(price_data)
        
        if rsi_val is not None:
            results[pair] = {f"rsi_{interval}s": rsi_val}

    return jsonify(results)
