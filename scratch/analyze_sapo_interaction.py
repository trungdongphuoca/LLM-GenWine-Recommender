"""
Phân tích khả năng xây dựng recommender từ Sapo
với dữ liệu khách hàng + đơn hàng
"""
import pandas as pd
import numpy as np
import warnings, sys
warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

df_orders = pd.read_excel('Sapo/Danh sach don hang.xlsx')
df_cust   = pd.read_excel('Sapo/Danh sach khach hang.xlsx')
df_prod   = pd.read_excel('Sapo/Danh sach san pham.xlsx')

# ── Chuẩn hóa ───────────────────────────────────────────────────────────
df_orders['Tên khách hàng'] = df_orders['Tên khách hàng'].fillna('UNKNOWN')
df_orders['Mã SKU'] = df_orders['Mã SKU'].astype(str).str.strip()
df_prod['Mã SKU']   = df_prod['Mã SKU'].astype(str).str.strip()

# ── 1. Interaction Matrix ────────────────────────────────────────────────
print("=" * 60)
print("1. INTERACTION MATRIX (User × Item)")
print("=" * 60)

# Tổng hợp: mỗi khách × sản phẩm → tổng số lượng mua
user_item = df_orders.groupby(['Tên khách hàng', 'Mã SKU'])['Số lượng sản phẩm'].sum().reset_index()
n_users = user_item['Tên khách hàng'].nunique()
n_items = user_item['Mã SKU'].nunique()
n_interactions = len(user_item)
density = n_interactions / (n_users * n_items) * 100

print(f"  Users (khách hàng): {n_users}")
print(f"  Items (sản phẩm):   {n_items}")
print(f"  Interactions:       {n_interactions}")
print(f"  Matrix density:     {density:.2f}%")

# Phân phối số sản phẩm/khách
items_per_user = user_item.groupby('Tên khách hàng')['Mã SKU'].count()
print(f"\n  Phân phối số sản phẩm mua/khách:")
print(f"    ≥1 SP:  {(items_per_user >= 1).sum()} khách")
print(f"    ≥2 SP:  {(items_per_user >= 2).sum()} khách  ← có thể dùng leave-one-out")
print(f"    ≥3 SP:  {(items_per_user >= 3).sum()} khách")
print(f"    ≥5 SP:  {(items_per_user >= 5).sum()} khách")
print(f"    Max:    {items_per_user.max()} SP")
print(f"    Median: {items_per_user.median():.0f} SP")

# ── 2. Khả năng Leave-One-Out Evaluation ────────────────────────────────
print("\n" + "=" * 60)
print("2. LEAVE-ONE-OUT EVALUATION POTENTIAL")
print("=" * 60)

eligible = items_per_user[items_per_user >= 2]
print(f"  Khách đủ điều kiện test (≥2 SP): {len(eligible)}")
print(f"  → Dùng SP cuối làm ground truth, SP trước làm context")

# Xem ai mua nhiều nhất
print(f"\n  Top khách hàng (số loại SP):")
print(items_per_user.sort_values(ascending=False).head(10).to_string())

# ── 3. Khách hàng features ───────────────────────────────────────────────
print("\n" + "=" * 60)
print("3. CUSTOMER FEATURES")
print("=" * 60)

# Total Orders từ file khách hàng
total_orders_col = 'Total Orders(Tổng đơn hàng)'
total_spent_col  = 'Total Spent(Tổng chi tiêu)'
gender_col       = 'Giới tính'

print(f"  Giới tính:")
print(df_cust[gender_col].value_counts().to_string())

print(f"\n  Total Orders distribution:")
to_numeric = pd.to_numeric(df_cust[total_orders_col], errors='coerce').dropna()
print(f"    Mean: {to_numeric.mean():.2f} đơn")
print(f"    Median: {to_numeric.median():.0f} đơn")
print(f"    Max: {to_numeric.max():.0f} đơn")
print(f"    Khách mua lại (≥2 đơn): {(to_numeric >= 2).sum()}")

print(f"\n  Tỉnh/Thành phố:")
print(df_cust['Province(Tỉnh)'].value_counts().head(10).to_string())

# ── 4. Loại rượu preference ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("4. PRODUCT TYPE PREFERENCE (từ đơn hàng)")
print("=" * 60)

merged = df_orders.merge(df_prod[['Mã SKU', 'Loại sản phẩm']], on='Mã SKU', how='left')
type_by_cust = merged.groupby(['Tên khách hàng', 'Loại sản phẩm'])['Số lượng sản phẩm'].sum()
print("  Phân bố loại rượu mua theo khách:")
print(merged.groupby('Loại sản phẩm')['Số lượng sản phẩm'].sum().sort_values(ascending=False).to_string())

# ── 5. Potential Methods ─────────────────────────────────────────────────
print("\n" + "=" * 60)
print("5. CÁC PHƯƠNG PHÁP CÓ THỂ ÁP DỤNG")
print("=" * 60)
print("""
  [A] Content-Based (BM25/TF-IDF trên mô tả SP)
      → Giống Winemag, KHÔNG dùng lịch sử
      
  [B] Collaborative Filtering (User-Item Matrix)
      → Dùng lịch sử mua để tìm khách tương đồng
      → Phương pháp: cosine similarity, SVD, ALS
      
  [C] Session-Based (Đơn hàng = Session)
      → Mỗi đơn hàng là 1 session nhiều SP
      → "Đã mua A+B, gợi ý C"
      
  [D] LLM + Purchase History (Our method mở rộng)
      → Dùng lịch sử mua làm context cho LLM
      → Query: "Khách đã mua [SP1, SP2], recommend tiếp?"
      → SO SÁNH vs Winemag không có user history
      
  [E] Hybrid: CF + Content + LLM Rerank
      → CF cho warm users, LLM cho cold-start users
""")
