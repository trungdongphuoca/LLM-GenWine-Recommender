"""
Plot final model comparison charts with ACCURATE data.
Model name: "Proposed Model (Đề xuất)" instead of TIGER.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os
from math import pi

# ─── CONFIG ────────────────────────────────────────────────────────────────────
OUTPUT_DIR = 'results/scientific_metrics'
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 12

# ─── DATA ──────────────────────────────────────────────────────────────────────
# Chỉ lấy các model tiêu biểu nhất (tránh rối)
models = ['Random\nBaseline', 'TF-IDF CF', 'BM25', 'BM25+\nEnhanced',
          'Struct-Filter\nBM25', 'Proposed Model\n(Mô hình đề xuất)']

# Số liệu THỰC TẾ từ evaluation (nhân 100 để ra %)
recall_1  = [0.0083, 2.93,  3.62,  6.85,  5.19,  0.15]
recall_10 = [0.083,  14.74, 18.42, 31.04, 26.03, 0.15]   # Proposed chỉ sinh 1 ID
ndcg_10   = [0.034,  8.02,  9.85,  17.06, 13.80, 0.05]   # ~ Recall@1 * log(2)
mrr       = [0.020,  5.98,  7.25,  12.83, 10.12, 0.15]
intent_1  = [0.81,   50.27, 39.86, 89.80, 84.33, 9.67]   # TIGER = ClusterMatch (4096 cụm)
latency   = [0.004,  1.40,  253.6, 353.0, 85.1,  2277.5]

# Màu sắc
palette = ['#d4e6f1', '#aed6f1', '#5dade2', '#2e86c1', '#1a5276', '#c0392b']

# ─── HÀM VẼ BAR CHART ────────────────────────────────────────────────────────
def bar_chart(values, title, ylabel, filename, note=None, invert_better=False):
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(models))
    bars = ax.bar(x, values, color=palette, edgecolor='black', linewidth=0.8, zorder=3)
    
    # Highlight Proposed Model
    bars[-1].set_edgecolor('#7d0000')
    bars[-1].set_linewidth(2.5)
    
    # Số liệu trên đỉnh cột
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(values) * 0.01,
                f'{val:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=13)
    ax.set_title(title, fontsize=15, fontweight='bold', pad=15)
    ax.set_ylim(0, max(values) * 1.25)
    ax.yaxis.grid(True, linestyle='--', alpha=0.6)
    ax.set_axisbelow(True)

    if note:
        ax.text(0.5, -0.15, note, transform=ax.transAxes,
                ha='center', fontsize=10, color='gray', fontstyle='italic')

    # Gạch dưới Proposed Model
    ax.axvline(x=len(models) - 1, color='#c0392b', linestyle='--', alpha=0.3, linewidth=1.5)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  ✅ Saved: {path}")


# ─── BAR CHARTS ──────────────────────────────────────────────────────────────
print("\n[1/5] Recall@1")
bar_chart(recall_1, 'Recall@1 (%)', 'Recall@1 (%)',
          'bar_Recall_1.png',
          note='* Proposed Model: Greedy Decoding (1 output). Baselines: Top-1 from ranked list.')

print("[2/5] Recall@10")
bar_chart(recall_10, 'Recall@10 (%)', 'Recall@10 (%)',
          'bar_Recall_10.png',
          note='* Proposed Model retrieves exactly 1 candidate → Recall@10 ≈ Recall@1.')

print("[3/5] NDCG@10")
bar_chart(ndcg_10, 'NDCG@10 (%)', 'NDCG@10 (%)', 'bar_NDCG_10.png')

print("[4/5] MRR")
bar_chart(mrr, 'Mean Reciprocal Rank - MRR (%)', 'MRR (%)', 'bar_MRR.png')

print("[5/6] Intent/Cluster Match@1")
bar_chart(intent_1,
          'Intent Match@1 / Cluster Match@1 (%)',
          'Score (%)',
          'bar_Intent_Cluster_Match.png',
          note='* Baselines: Intent Match (Quốc gia + Giống nho, ~330 classes).\n  Proposed Model: Cluster Match (Đúng cụm K-Means C1-C2-C3 trong 4,096 cụm — khó hơn ~12 lần).')

print("[6/6] Latency")
bar_chart(latency, 'Inference Latency (ms/query) — thấp hơn là tốt hơn',
          'Latency (ms)', 'bar_Latency.png')

# ─── RADAR CHART ─────────────────────────────────────────────────────────────
print("\n[Radar] Trade-off Chart")

# Chỉ lấy 4 model đại diện để radar không rối
radar_models  = ['BM25', 'BM25+\nEnhanced', 'Struct-Filter\nBM25', 'Proposed Model\n(Mô hình đề xuất)']
radar_palette = ['#5dade2', '#2e86c1', '#1a5276', '#c0392b']

# 5 trục — Tất cả đều chuẩn hóa về 0-100, cao hơn = tốt hơn
categories = ['Recall@1', 'Recall@10', 'MRR', 'Semantic\nGeneralization', 'Response\nSpeed']
N = len(categories)
angles = [n / float(N) * 2 * pi for n in range(N)]
angles += angles[:1]

# Giá trị thực sau khi chuẩn hóa theo max toàn nhóm (0-100)
raw_data = {
    'BM25':                   [3.62,  18.42, 7.25,  39.86, 253.6],
    'BM25+\nEnhanced':        [6.85,  31.04, 12.83, 89.80, 353.0],
    'Struct-Filter\nBM25':    [5.19,  26.03, 10.12, 84.33, 85.1],
    'Proposed Model\n(Mô hình đề xuất)': [0.15, 0.15, 0.15, 9.67, 2277.5]
}

# Max values cho chuẩn hóa
col_max = [6.85, 31.04, 12.83, 89.80, 353.0]  # Recall@1, Recall@10, MRR, Intent, Latency

# Với Latency: nghịch đảo (thấp = tốt = điểm cao)
latency_max = max(v[4] for v in raw_data.values())

def normalize_row(vals):
    n = []
    for i, v in enumerate(vals):
        if i == 4:  # Latency: invert
            n.append((1 - (v / latency_max)) * 100)
        else:
            n.append((v / col_max[i]) * 100 if col_max[i] > 0 else 0)
    return n

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
fig.patch.set_facecolor('white')
ax.set_facecolor('#f9f9f9')

plt.xticks(angles[:-1], categories, size=12, fontweight='bold')
ax.set_rlabel_position(45)
plt.yticks([25, 50, 75, 100], ['25', '50', '75', '100'], color='grey', size=9)
plt.ylim(0, 100)

legend_handles = []
for model, color in zip(radar_models, radar_palette):
    norm_vals = normalize_row(raw_data[model])
    norm_vals += norm_vals[:1]
    lw = 3 if 'Proposed' in model else 1.5
    ax.plot(angles, norm_vals, linewidth=lw, linestyle='solid', color=color)
    ax.fill(angles, norm_vals, color=color, alpha=0.15 if 'Proposed' not in model else 0.25)
    legend_handles.append(mpatches.Patch(color=color, label=model.replace('\n', ' ')))

plt.legend(handles=legend_handles, loc='upper right', bbox_to_anchor=(1.45, 1.15), fontsize=11)
plt.title('Biểu đồ Đánh đổi Đa chiều\n(Multi-dimensional Trade-off)',
          size=15, fontweight='bold', pad=30)

path = os.path.join(OUTPUT_DIR, 'radar_tradeoff.png')
plt.tight_layout()
plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print(f"  ✅ Saved: {path}")

print("\n✅ Hoàn thành! Tất cả biểu đồ đã lưu tại:", OUTPUT_DIR)
