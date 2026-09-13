import json
import urllib.request
import re

def clean_word(w):
    w = re.sub(r'\s+', ' ', w.strip())
    # Chuyển dấu gạch dưới thành khoảng trắng nếu nguồn dùng dạng compound_word
    w = w.replace('_', ' ')
    return w

# 1. Đọc dữ liệu ban đầu
cleaned_set = set()
try:
    with open("vua_tieng_viet.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        for item in raw_data:
            w = clean_word(item)
            if w:
                cleaned_set.add(w)
    print(f"Đã nạp {len(cleaned_set)} mục từ file gốc.")
except FileNotFoundError:
    print("Không tìm thấy vua_tieng_viet.json, sẽ tạo mới từ kho mở.")

# 2. Danh sách các URL dữ liệu dự phòng từ các kho từ điển tiếng Việt chuẩn
DATA_SOURCES = [
    # Kho từ vựng chuẩn từ repo Vietnamese Lexicon / NLP
    "https://raw.githubusercontent.com/stopwords/vietnamese-stopwords/master/vietnamese-stopwords.txt",
    "https://raw.githubusercontent.com/vunb/vietnamese-wordlist/master/Viet74K.txt",
    "https://raw.githubusercontent.com/thunghiem-nlp/vietnamese-dictionary/master/words.txt"
]

req_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for url in DATA_SOURCES:
    try:
        print(f"Đang tải dữ liệu từ: {url.split('/')[-1]}...")
        req = urllib.request.Request(url, headers=req_headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8", errors="ignore").splitlines()
            count = 0
            for line in content:
                w = clean_word(line)
                # Bỏ từ quá ngắn hoặc chứa số, ký tự đặc biệt
                if len(w) >= 2 and not re.search(r'[0-9@#$%^&*()+=<>?/\\]', w):
                    cleaned_set.add(w)
                    count += 1
            print(f" -> Nạp thành công {count} mục.")
    except Exception as e:
        print(f" -> Bỏ qua nguồn này (Lỗi: {e})")

# 3. Phân nhóm dữ liệu cho format game show
total_list = sorted(list(cleaned_set), key=lambda s: s.lower())

game_data = {
    "tat_ca": total_list,
    "tu_don_va_ghep_ngan": [w for w in total_list if len(w.split()) <= 2],
    "thanh_ngu_quan_ngu": [w for w in total_list if len(w.split()) >= 4]
}

# 4. Xuất file kết quả
output_filename = "vua_tieng_viet_full.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(game_data, f, ensure_ascii=False, indent=2)

print(f"\nHoàn tất! Tổng cộng {len(total_list)} mục duy nhất đã lưu vào '{output_filename}'.")