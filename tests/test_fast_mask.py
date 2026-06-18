import time
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parents[1]
CATALOG_PATH = ROOT / 'data/processed/wine_catalog_semantic.csv'

print("Loading catalog...")
cat = pd.read_csv(CATALOG_PATH, usecols=['variety', 'country'], dtype=str).fillna('')

cat_variety = cat['variety'].str.lower().tolist()
cat_country = cat['country'].str.lower().tolist()
cat_var_arr = np.array(cat_variety)
cat_ctr_arr = np.array(cat_country)

# Warm up / original method
v, c = "cabernet sauvignon", "us"
print("\n--- Original method (string find) ---")
t0 = time.time()
for _ in range(50):
    v_mask = np.ones(len(cat), dtype=bool) if not v else np.char.find(cat_var_arr, v[:10]) >= 0
    c_mask = np.ones(len(cat), dtype=bool) if not c else np.char.find(cat_ctr_arr, c[:8])  >= 0
    mask = v_mask & c_mask
    sub_idx_orig = np.where(mask)[0]
print(f"Original: {time.time()-t0:.4f}s for 50 iterations (avg {(time.time()-t0)/50*1000:.2f}ms/it)")

# New optimized method
print("\n--- Optimized method (precomputed dict) ---")
t0 = time.time()
unique_varieties = cat['variety'].str.lower().unique()
unique_countries = cat['country'].str.lower().unique()

variety_to_indices = {var: np.where(cat_var_arr == var)[0] for var in unique_varieties if var}
country_to_indices = {ctr: np.where(cat_ctr_arr == ctr)[0] for ctr in unique_countries if ctr}
print(f"Precomputation took {time.time()-t0:.4f}s")

t0 = time.time()
for _ in range(50):
    if not v:
        v_idx = None
    else:
        matching_vars = [var for var in unique_varieties if var and v[:10] in var]
        v_idx = np.concatenate([variety_to_indices[var] for var in matching_vars]) if matching_vars else np.array([], dtype=int)
    
    if not c:
        c_idx = None
    else:
        matching_ctrs = [ctr for ctr in unique_countries if ctr and c[:8] in ctr]
        c_idx = np.concatenate([country_to_indices[ctr] for ctr in matching_ctrs]) if matching_ctrs else np.array([], dtype=int)
        
    if v_idx is None and c_idx is None:
        sub_idx_opt = np.arange(len(cat))
    elif v_idx is None:
        sub_idx_opt = c_idx
    elif c_idx is None:
        sub_idx_opt = v_idx
    else:
        sub_idx_opt = np.intersect1d(v_idx, c_idx, assume_unique=True)
print(f"Optimized: {time.time()-t0:.4f}s for 50 iterations (avg {(time.time()-t0)/50*1000:.2f}ms/it)")

# Compare correctness
print(f"\nOriginal length: {len(sub_idx_orig)}")
print(f"Optimized length: {len(sub_idx_opt)}")
# Sort and check equality
sub_idx_orig.sort()
sub_idx_opt.sort()
print(f"Match: {np.array_equal(sub_idx_orig, sub_idx_opt)}")
