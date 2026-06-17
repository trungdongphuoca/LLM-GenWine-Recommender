"""
Phân tích toàn diện dữ liệu Sapo để lên kế hoạch ablation study
"""
import pandas as pd
import numpy as np
import warnings, sys
warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

# ─── Load ────────────────────────────────────────────────────────────────
df_orders  = pd.read_excel('Sapo/Danh sach don hang.xlsx')
df_cust    = pd.read_excel('Sapo/Danh sach khach hang.xlsx')
df_prod    = pd.read_excel('Sapo/Danh sach san pham.xlsx')

# ─── Sản phẩm ────────────────────────────────────────────────────────────
print("=" * 60)
print("PHÂN TÍCH SẢN PHẨM (Danh sach san pham.xlsx)")
print("=" * 60)
print(f"Tổng sản phẩm: {df_prod.shape[0]}")
print(f"\nLoại sản phẩm:")
print(df_prod['Loại sản phẩm'].value_counts().head(20).to_string())
print(f"\nGiá (sample):")
prices = df_prod['Giá'].dropna().astype(str).str.replace(',','').apply(pd.to_numeric, errors='coerce').dropna()
print(f"  Min: {prices.min():,.0f} VND")
print(f"  Max: {prices.max():,.0f} VND")
print(f"  Mean: {prices.mean():,.0f} VND")
print(f"  Median: {prices.median():,.0f} VND")
print(f"\nNhãn hiệu (top 10):")
print(df_prod['Nhãn hiệu'].value_counts().head(10).to_string())
print(f"\nMô tả sản phẩm có hay không:")
has_desc = df_prod['Mô tả sản phẩm'].notna().sum()
print(f"  Có mô tả: {has_desc}/{df_prod.shape[0]} sản phẩm ({has_desc/df_prod.shape[0]*100:.1f}%)")

# ─── Đơn hàng ────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("PHÂN TÍCH ĐƠN HÀNG (Danh sach don hang.xlsx)")
print("=" * 60)
print(f"Tổng dòng đơn hàng: {df_orders.shape[0]}")
unique_orders = df_orders['Mã đơn hàng'].nunique()
print(f"Đơn hàng duy nhất: {unique_orders}")
print(f"\nNguồn đơn hàng:")
print(df_orders['Nguồn'].value_counts().to_string())
print(f"\nTop 10 sản phẩm bán chạy:")
top_prods = df_orders.groupby('Tên sản phẩm')['Số lượng sản phẩm'].sum().sort_values(ascending=False).head(10)
print(top_prods.to_string())
print(f"\nKhoảng giá đơn hàng:")
print(f"  Min: {df_orders['Tổng tiền'].min():,.0f} VND")
print(f"  Max: {df_orders['Tổng tiền'].max():,.0f} VND")
print(f"  Mean: {df_orders['Tổng tiền'].mean():,.0f} VND")

# ─── Khách hàng ──────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("PHÂN TÍCH KHÁCH HÀNG (Danh sach khach hang.xlsx)")
print("=" * 60)
print(f"Tổng khách hàng: {df_cust.shape[0]}")
print(f"Columns: {list(df_cust.columns)}")

# Tìm cột tổng đơn hàng và tổng chi tiêu
order_col = [c for c in df_cust.columns if 'đơn' in c.lower() or 'order' in c.lower()]
spent_col = [c for c in df_cust.columns if 'chi tiêu' in c.lower() or 'spent' in c.lower()]
print(f"Order col: {order_col}")
print(f"Spent col: {spent_col}")

if order_col:
    col = order_col[0]
    print(f"\nPhân phối số đơn hàng/khách ({col}):")
    print(df_cust[col].describe().to_string())
    repeat = (df_cust[col] > 1).sum()
    print(f"Khách mua lại (>1 đơn): {repeat}/{df_cust.shape[0]} ({repeat/df_cust.shape[0]*100:.1f}%)")

# ─── Khả năng xây dựng CF ────────────────────────────────────────────────
print("\n" + "=" * 60)
print("ĐÁNH GIÁ KHẢ NĂNG XÂY DỰNG RECOMMENDER")
print("=" * 60)

# Join orders với products
df_orders['Mã SKU'] = df_orders['Mã SKU'].astype(str).str.strip()
df_prod['Mã SKU'] = df_prod['Mã SKU'].astype(str).str.strip()

merged = df_orders.merge(df_prod[['Mã SKU', 'Tên sản phẩm*', 'Loại sản phẩm', 'Giá', 'Mô tả sản phẩm']], 
                          on='Mã SKU', how='left')

n_products_in_orders = df_orders['Mã SKU'].nunique()
n_customers_with_orders = df_orders['Tên khách hàng'].nunique()
n_products_matched = merged['Loại sản phẩm'].notna().sum()

print(f"Sản phẩm duy nhất trong đơn hàng: {n_products_in_orders}")
print(f"Khách hàng duy nhất trong đơn hàng: {n_customers_with_orders}")
print(f"Tỷ lệ match SKU orders→products: {n_products_matched}/{df_orders.shape[0]} ({n_products_matched/df_orders.shape[0]*100:.1f}%)")

# Khách mua nhiều sản phẩm
orders_per_cust = df_orders.groupby('Tên khách hàng')['Mã SKU'].nunique()
multi_buy = (orders_per_cust > 1).sum()
print(f"\nKhách mua ≥2 sản phẩm khác nhau: {multi_buy}/{n_customers_with_orders} ({multi_buy/n_customers_with_orders*100:.1f}%)")
print(f"\nTop 10 khách hàng (số loại sản phẩm):")
print(orders_per_cust.sort_values(ascending=False).head(10).to_string())

print("\n\nTÓM TẮT KHẢ NĂNG:")
print(f"  - Catalog: {df_prod.shape[0]} sản phẩm (vs 130,000 Winemag)")
print(f"  - Interactions: {df_orders.shape[0]} dòng đơn ({unique_orders} đơn)")
print(f"  - Khách hàng: {n_customers_with_orders} unique (vs millions)")
print(f"  - Mô tả sản phẩm: {has_desc} sản phẩm có mô tả chi tiết")
