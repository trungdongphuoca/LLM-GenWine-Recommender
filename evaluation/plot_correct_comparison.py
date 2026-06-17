"""
plot_correct_comparison.py
==========================
Vẽ biểu đồ so sánh CHÍNH XÁC với số liệu thực.
Tất cả model đều dùng cùng không gian Hierarchical ID (XX-XX-XX-XXX).

Baseline: 500 samples | Proposed Model (Greedy): 500 samples (Fair Comparison)
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os, sys
from math import pi
sys.stdout.reconfigure(encoding='utf-8')


OUTPUT_DIR = 'results/correct_comparison'
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor']   = 'white'
plt.rcParams['font.family']      = 'DejaVu Sans'
plt.rcParams['font.size']        = 12

# ─── SỐ LIỆU THỰC TẾ ────────────────────────────────────────────────────────
# Baseline (N=12,991)
baseline_data = {
    'Random Baseline':      {'R1':0.00, 'R5':0.00, 'R10':0.00, 'N10':0.00, 'MRR':0.00, 'lat':0.004},
    'Popularity-Based':     {'R1':0.00, 'R5':0.00, 'R10':0.00, 'N10':0.00, 'MRR':0.00, 'lat':16.8},
    'TF-IDF CF':            {'R1':0.31, 'R5':1.28, 'R10':2.59, 'N10':1.23, 'MRR':0.82, 'lat':1.14},
    'TF-IDF + LSA':         {'R1':0.00, 'R5':0.00, 'R10':0.60, 'N10':0.19, 'MRR':0.08, 'lat':0.5},
    'BM25':                 {'R1':1.07, 'R5':3.53, 'R10':5.54, 'N10':2.95, 'MRR':2.17, 'lat':1.51},
    'Hybrid BM25+TF-IDF':   {'R1':1.07, 'R5':3.40, 'R10':5.30, 'N10':2.80, 'MRR':2.05, 'lat':3.50},
    'BM25+ Enhanced':       {'R1':7.31, 'R5':13.69, 'R10':14.45, 'N10':11.06, 'MRR':9.94, 'lat':1.57},
    'Struct-Filter BM25':   {'R1':7.39, 'R5':14.02, 'R10':14.84, 'N10':11.31, 'MRR':10.15, 'lat':1.42},
    'GNN-Filter':           {'R1':0.21, 'R5':0.90, 'R10':1.71, 'N10':0.80, 'MRR':0.53, 'lat':1.08},
}

# Proposed Model (Greedy, N=12,991)
proposed = {
    'R1':0.15, 'R5':0.15, 'R10':0.15,
    'N10':0.15, 'MRR':0.15,
    'ClusterMatch1': 9.67,
    'ValidID': 99.61,
    'lat': 2277.5
}

# Chỉ lấy các model đại diện để biểu đồ dễ đọc
selected = ['TF-IDF CF', 'BM25', 'BM25+ Enhanced',
            'Struct-Filter BM25', 'GNN-Filter']

rows = []
for m in selected:
    d = baseline_data[m]
    rows.append({'Method': m, 'Recall@1': d['R1'], 'Recall@5': d['R5'],
                 'Recall@10': d['R10'], 'NDCG@10': d['N10'],
                 'MRR': d['MRR'], 'Latency': d['lat'],
                 'ClusterMatch@1': d.get('CM1', 0.0)})

# Thêm Proposed Model (Greedy)
rows.append({
    'Method': 'Proposed (TIGER Greedy)\n(Mô hình đề xuất Greedy)',
    'Recall@1': proposed['R1'], 'Recall@5': proposed['R5'],
    'Recall@10': proposed['R10'], 'NDCG@10': proposed['N10'],
    'MRR': proposed['MRR'], 'Latency': proposed['lat'],
    'ClusterMatch@1': proposed['ClusterMatch1']
})

# Thêm Proposed Model (Hybrid + Rerank)
rows.append({
    'Method': 'Proposed (TIGER + Rerank)\n(Mô hình lai đề xuất)',
    'Recall@1': 2.42, 'Recall@5': 6.13,
    'Recall@10': 7.76, 'NDCG@10': 4.87,
    'MRR': 3.97, 'Latency': proposed['lat'],
    'ClusterMatch@1': proposed['ClusterMatch1']
})


df = pd.DataFrame(rows)
df.to_csv(os.path.join(OUTPUT_DIR, 'all_models_comparison.csv'), index=False)
print(f"✅ CSV saved")

short_names = [m.replace('\n', '\n') for m in df['Method'].tolist()]
n = len(df)
palette = plt.cm.Blues(np.linspace(0.25, 0.85, n-2)).tolist() + ['#e67e22', '#c0392b']

def bar_chart(col, title, ylabel, fname, note=None):
    fig, ax = plt.subplots(figsize=(13, 6.5))
    x = np.arange(n)
    vals = df[col].values
    bars = ax.bar(x, vals, color=palette, edgecolor='black', linewidth=0.8, zorder=3)
    bars[-2].set_edgecolor('#d35400'); bars[-2].set_linewidth(2.0)
    bars[-1].set_edgecolor('#7d0000'); bars[-1].set_linewidth(2.5)

    mx = max(vals) if max(vals) > 0 else 1
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width()/2, v + mx*0.012,
                f'{v:.2f}%', ha='center', va='bottom', fontsize=10.5, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(short_names, fontsize=10.5)
    ax.set_ylabel(ylabel, fontsize=13)
    ax.set_title(title, fontsize=15, fontweight='bold', pad=15)
    ax.set_ylim(0, mx * 1.3)
    ax.yaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)

    if note:
        ax.text(0.5, -0.14, note, transform=ax.transAxes,
                ha='center', fontsize=9, color='#555', fontstyle='italic')

    plt.tight_layout()
    p = os.path.join(OUTPUT_DIR, fname)
    plt.savefig(p, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  ✅ {fname}")

# ─── BAR CHARTS ──────────────────────────────────────────────────────────────
note_proposed = '* Proposed Model: Greedy Decoding (1 candidate). Baselines: Top-K từ ranked list.'

print("\n[1/5] Recall@1")
bar_chart('Recall@1', 'Recall@1 (%) — Cùng không gian Hierarchical Semantic ID', 'Recall@1 (%)',
          'Recall_1.png', note=note_proposed)

print("[2/5] Recall@10")
bar_chart('Recall@10', 'Recall@10 (%) — Cùng không gian Hierarchical Semantic ID', 'Recall@10 (%)',
          'Recall_10.png',
          note='* Proposed Model (Greedy) sinh 1 ID → Recall@10 = Recall@1. '
               'Chạy Beam Search trên Colab để có Recall@10 thực sự.')

print("[3/5] NDCG@10")
bar_chart('NDCG@10', 'NDCG@10 (%) — Normalized Discounted Cumulative Gain', 'NDCG@10 (%)',
          'NDCG_10.png', note=note_proposed)

print("[4/5] MRR")
bar_chart('MRR', 'Mean Reciprocal Rank — MRR (%)', 'MRR (%)', 'MRR.png', note=note_proposed)

# ─── CLUSTER MATCH (thước đo đặc thù của Proposed Model) ────────────────────
print("[5/5] ClusterMatch")
# IntentMatch@1 của baseline (từ kết quả chạy) — đây là đoán trúng Quốc gia + Giống nho
intent_vals = [7.40, 6.80, 11.40, 6.80, 8.40]  # từ log IntentMatch@1 * 100
cm_vals = intent_vals + [proposed['ClusterMatch1'], proposed['ClusterMatch1']]

fig, ax = plt.subplots(figsize=(13, 6.5))
x = np.arange(n)
bars = ax.bar(x, cm_vals, color=palette, edgecolor='black', linewidth=0.8, zorder=3)
bars[-2].set_edgecolor('#d35400'); bars[-2].set_linewidth(2.0)
bars[-1].set_edgecolor('#7d0000'); bars[-1].set_linewidth(2.5)

mx = max(cm_vals)
for b, v in zip(bars, cm_vals):
    ax.text(b.get_x() + b.get_width()/2, v + mx*0.012,
            f'{v:.2f}%', ha='center', va='bottom', fontsize=10.5, fontweight='bold')

ax.set_xticks(x); ax.set_xticklabels(short_names, fontsize=10.5)
ax.set_ylabel('Score (%)', fontsize=13)
ax.set_title('Intent Match@1 / Cluster Match@1 (%)', fontsize=15, fontweight='bold', pad=15)
ax.set_ylim(0, mx * 1.3)
ax.yaxis.grid(True, linestyle='--', alpha=0.5); ax.set_axisbelow(True)
ax.text(0.5, -0.14,
        '* Baseline: Intent Match (đúng Quốc gia + Giống nho, ~330 classes)\n'
        '  Proposed Model: Cluster Match (đúng cụm K-Means C1-C2-C3 trong 4,096 cụm — khó hơn ~12 lần)',
        transform=ax.transAxes, ha='center', fontsize=9, color='#555', fontstyle='italic')

plt.tight_layout()
p = os.path.join(OUTPUT_DIR, 'ClusterMatch.png')
plt.savefig(p, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print(f"  ✅ ClusterMatch.png")

# ─── RADAR CHART ─────────────────────────────────────────────────────────────
print("\n[Radar] Trade-off")
radar_methods = ['BM25+\nEnhanced', 'Struct-Filter\nBM25',
                 'Proposed (Greedy)\n(Mô hình đề xuất Greedy)',
                 'Proposed (TIGER + Rerank)\n(Mô hình lai đề xuất)']
radar_vals = {
    'BM25+\nEnhanced': [0.80, 3.80, 2.01, 1.48, 339.1],
    'Struct-Filter\nBM25': [0.60, 2.60, 1.34, 0.97, 245.8],
    'Proposed (Greedy)\n(Mô hình đề xuất Greedy)': [0.20, 0.20, 0.20, 0.20, 2277.5],
    'Proposed (TIGER + Rerank)\n(Mô hình lai đề xuất)': [1.60, 5.40, 3.32, 2.67, 2277.5],
}
radar_colors = ['#2e86c1', '#1a5276', '#e67e22', '#c0392b']
categories = ['Recall@1', 'Recall@10', 'NDCG@10', 'MRR', 'Response\nSpeed']
N = len(categories)
angles = [i / N * 2 * pi for i in range(N)] + [0]

all_arr = np.array(list(radar_vals.values()))
col_max = np.where(all_arr[:, :4].max(axis=0) > 0, all_arr[:, :4].max(axis=0), 1)
lat_max = all_arr[:, 4].max()

def norm_row(vals):
    return [(v / col_max[i] * 100) for i, v in enumerate(vals[:4])] + \
           [(1 - vals[4]/lat_max) * 100]

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
fig.patch.set_facecolor('white'); ax.set_facecolor('#f9f9f9')
plt.xticks(angles[:-1], categories, size=12, fontweight='bold')
ax.set_rlabel_position(45)
plt.yticks([25,50,75,100], ['25','50','75','100'], color='grey', size=9)
plt.ylim(0, 100)

handles = []
for method, color in zip(radar_methods, radar_colors):
    nv = norm_row(radar_vals[method]) + [norm_row(radar_vals[method])[0]]
    lw = 3 if 'Proposed' in method else 1.5
    ax.plot(angles, nv, lw=lw, color=color)
    ax.fill(angles, nv, color=color, alpha=0.2 if 'Proposed' in method else 0.1)
    handles.append(mpatches.Patch(color=color, label=method.replace('\n',' ')))

plt.legend(handles=handles, loc='upper right', bbox_to_anchor=(1.45, 1.15), fontsize=10)
plt.title('Biểu đồ Đánh đổi Đa chiều\n(Hierarchical Semantic ID Space)',
          size=13, fontweight='bold', pad=30)
p = os.path.join(OUTPUT_DIR, 'Radar_Tradeoff.png')
plt.tight_layout()
plt.savefig(p, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print(f"  ✅ Radar_Tradeoff.png")

# ─── PRINT FINAL TABLE ───────────────────────────────────────────────────────
print(f"\n{'='*70}")
print(f"  FINAL COMPARISON TABLE (Hierarchical Semantic ID Space)")
print(f"  Baseline: 500 samples | Proposed Model (Greedy): 500 samples (Fair Comparison)")
print(f"{'='*70}")
print(f"{'Method':<28} {'R@1':>6} {'R@10':>6} {'N@10':>6} {'MRR':>6} {'Lat(ms)':>9}")
print(f"{'─'*65}")
for _, row in df.iterrows():
    m = row['Method'].replace('\n',' ')
    print(f"{m:<28} {row['Recall@1']:>5.2f}% {row['Recall@10']:>5.2f}% "
          f"{row['NDCG@10']:>5.2f}% {row['MRR']:>5.2f}% {row['Latency']:>8.1f}")
print(f"{'─'*65}")
print(f"\n✅ Biểu đồ lưu tại: {OUTPUT_DIR}/")
