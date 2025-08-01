# rsi/storage.py
import json
import os

RSI_FILE = os.path.join("rsi_data", "rsi_data.json")

def save_rsi_cache_to_file(rsi_cache):
    # Đảm bảo thư mục chứa file tồn tại nếu RSI_FILE có path
    if os.path.dirname(RSI_FILE):
        os.makedirs(os.path.dirname(RSI_FILE), exist_ok=True)
    with open(RSI_FILE, "w") as f:
        json.dump(rsi_cache, f)

def load_rsi_cache_from_file():
    if not os.path.exists(RSI_FILE):
        print(f"ℹ️ File '{RSI_FILE}' không tồn tại. Tạo cache rỗng.")
        return {}
    
    try:
        with open(RSI_FILE, "r") as f:
            # Thử đọc nội dung file. Nếu file rỗng, json.load sẽ lỗi.
            return json.load(f)
    except json.JSONDecodeError:
        # Bắt lỗi khi nội dung file không phải là JSON hợp lệ (ví dụ: file rỗng)
        print(f"⚠️ Cảnh báo: File '{RSI_FILE}' trống hoặc chứa JSON không hợp lệ. Khởi tạo cache rỗng.")
        # (Tùy chọn) Bạn có thể ghi lại một đối tượng JSON rỗng vào file để sửa chữa nó
        # with open(RSI_FILE, "w") as f:
        #     json.dump({}, f)
        return {}
    except Exception as e:
        # Bắt các lỗi khác có thể xảy ra khi đọc file
        print(f"❌ Lỗi không mong muốn khi đọc file '{RSI_FILE}': {e}")
        return {}
