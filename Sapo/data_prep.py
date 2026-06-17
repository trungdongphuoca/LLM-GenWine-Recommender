"""
sapo/data_prep.py
=================
Chuẩn bị dữ liệu Sapo cho ablation study:
- Làm sạch catalog sản phẩm (mô tả HTML → text)
- Chuẩn hóa giá VND
- Xây dựng user-item interaction matrix
- Split train/test theo leave-one-out
- Xuất: sapo_catalog.csv, sapo_interactions.csv, sapo_test.jsonl
"""
import sys, os, re, json
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parents[1]))
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import numpy as np
from pathlib import Path
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')

ROOT   = Path(__file__).parents[1]
SAPO   = ROOT / 'Sapo'
OUT    = ROOT / 'data' / 'sapo'
OUT.mkdir(parents=True, exist_ok=True)

# ── 1. Load raw data ─────────────────────────────────────────────────────
print("Loading Sapo data...")
df_prod   = pd.read_excel(SAPO / 'Danh sach san pham.xlsx')
df_orders = pd.read_excel(SAPO / 'Danh sach don hang.xlsx')

# ── 2. Catalog: làm sạch ────────────────────────────────────────────────
def clean_html(text):
    if pd.isna(text) or not isinstance(text, str):
        return ''
    soup = BeautifulSoup(text, 'html.parser')
    clean = soup.get_text(separator=' ')
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def parse_price_vnd(val):
    if pd.isna(val):
        return np.nan
    s = str(val).replace(',', '').replace('.', '').strip()
    try:
        return float(s)
    except:
        return np.nan

print("Cleaning product catalog...")
df_prod['description_clean'] = df_prod['Mô tả sản phẩm'].apply(clean_html)
df_prod['price_vnd']         = df_prod['Giá'].apply(parse_price_vnd)
df_prod['price_compare_vnd'] = df_prod['Giá so sánh'].apply(parse_price_vnd)
df_prod['Mã SKU']            = df_prod['Mã SKU'].astype(str).str.strip()

# Lọc chỉ lấy unique SKU (có thể có nhiều dòng cùng SKU do variants)
cat = df_prod.drop_duplicates(subset='Mã SKU', keep='first').copy()
cat = cat[cat['Mã SKU'].notna() & (cat['Mã SKU'] != 'nan')].reset_index(drop=True)

# Tạo text đầy đủ cho embedding
cat['full_text'] = (
    cat['Tên sản phẩm*'].fillna('') + ' ' +
    cat['Loại sản phẩm'].fillna('') + ' ' +
    cat['Nhãn hiệu'].fillna('') + ' ' +
    cat['Tags'].fillna('') + ' ' +
    cat['description_clean'].str[:500]  # giới hạn 500 ký tự
).str.strip()

# Chọn cột cần thiết
cat_out = cat[['Mã SKU', 'Tên sản phẩm*', 'Loại sản phẩm',
               'Nhãn hiệu', 'Tags', 'price_vnd', 'price_compare_vnd',
               'description_clean', 'full_text']].copy()
cat_out.columns = ['sku', 'name', 'type', 'brand', 'tags',
                   'price', 'price_compare', 'description', 'full_text']
cat_out['item_idx'] = range(len(cat_out))

cat_out.to_csv(OUT / 'sapo_catalog.csv', index=False, encoding='utf-8-sig')
print(f"  Catalog: {len(cat_out)} sản phẩm unique → sapo_catalog.csv")

# ── 3. Interactions: chuẩn hóa ──────────────────────────────────────────
print("Building interaction matrix...")
df_orders['sku']  = df_orders['Mã SKU'].astype(str).str.strip()
df_orders['user'] = df_orders['Tên khách hàng'].fillna('UNKNOWN').str.strip()
df_orders['date'] = pd.to_datetime(df_orders['Ngày tạo đơn'], dayfirst=True, errors='coerce')

# Chỉ giữ orders có SKU hợp lệ trong catalog
valid_skus = set(cat_out['sku'].tolist())
df_valid   = df_orders[df_orders['sku'].isin(valid_skus)].copy()
df_valid   = df_valid[df_valid['user'] != 'UNKNOWN'].copy()

# Aggregate: user × sku → tổng qty
interactions = df_valid.groupby(['user', 'sku']).agg(
    qty=('Số lượng sản phẩm', 'sum'),
    n_orders=('Mã đơn hàng', 'nunique'),
    last_date=('date', 'max'),
    total_spent=('Giá sản phẩm', 'sum')
).reset_index()

interactions.to_csv(OUT / 'sapo_interactions.csv', index=False, encoding='utf-8-sig')
print(f"  Interactions: {len(interactions)} records → sapo_interactions.csv")
print(f"  Users: {interactions['user'].nunique()}")
print(f"  Items: {interactions['sku'].nunique()}")

# ── 4. Leave-One-Out Split ───────────────────────────────────────────────
print("Building leave-one-out test set...")

# Lấy các user có ≥2 items (theo thứ tự thời gian)
user_history = df_valid.sort_values('date').groupby('user')['sku'].apply(list).reset_index()
user_history.columns = ['user', 'sku_history']

# Chỉ giữ user có ≥2 SP unique
user_history['unique_items'] = user_history['sku_history'].apply(lambda x: list(dict.fromkeys(x)))
eligible = user_history[user_history['unique_items'].apply(len) >= 2].copy()
eligible = eligible.reset_index(drop=True)

# Tạo test JSONL
test_records = []
for _, row in eligible.iterrows():
    items    = row['unique_items']
    target   = items[-1]      # SP cuối = ground truth
    history  = items[:-1]     # SP trước = context

    # Lấy tên sản phẩm cho context
    hist_names = []
    for s in history[-5:]:  # tối đa 5 SP gần nhất
        name_row = cat_out[cat_out['sku'] == s]
        if not name_row.empty:
            hist_names.append(name_row.iloc[0]['name'])

    target_row = cat_out[cat_out['sku'] == target]
    if target_row.empty:
        continue

    target_info = target_row.iloc[0]
    instruction = (
        f"Khách hàng đã mua: {', '.join(hist_names)}. "
        f"Gợi ý sản phẩm rượu vang tiếp theo phù hợp."
    )

    test_records.append({
        'user': row['user'],
        'instruction': instruction,
        'history_skus': history,
        'target_sku': target,
        'target_name': target_info['name'],
        'target_type': str(target_info['type']),
        'target_price': float(target_info['price']) if not pd.isna(target_info['price']) else None,
    })

test_path = OUT / 'sapo_test.jsonl'
with open(test_path, 'w', encoding='utf-8') as f:
    for rec in test_records:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')

print(f"  Test set: {len(test_records)} users → sapo_test.jsonl")

# ── 5. Summary ───────────────────────────────────────────────────────────
print("\n=== SAPO DATA PREP SUMMARY ===")
print(f"  Catalog:      {len(cat_out)} products")
print(f"  Interactions: {len(interactions)} (user×item pairs)")
print(f"  Test users:   {len(test_records)}")
print(f"  Output dir:   {OUT}")
print("=" * 40)
