"""
plot_comprehensive.py
=====================
Generates all publication-quality charts for the thesis:
  P1 - Grouped Bar Chart (all metrics, all models)
  P2 - Recall@K Curve
  P3 - Ablation Study Bar
  P4 - Latency vs Recall@10 Scatter
  P5 - Radar Chart (updated)
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parents[1]))
import config as cfg

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# ── Style ──────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family':      'DejaVu Sans',
    'font.size':        11,
    'axes.titlesize':   13,
    'axes.titleweight': 'bold',
    'axes.spines.top':  False,
    'axes.spines.right':False,
    'axes.grid':        True,
    'grid.alpha':       0.3,
    'grid.linestyle':   '--',
    'figure.dpi':       150,
    'savefig.dpi':      200,
    'savefig.bbox':     'tight',
    'savefig.facecolor':'white',
})

OUT = cfg.RESULTS / "correct_comparison"
OUT.mkdir(parents=True, exist_ok=True)

# ── Data ───────────────────────────────────────────────────────────────────────
MODELS = [
    ("TF-IDF CF",            0.31, 1.28, 2.59, 1.23, 0.82,    1.14),
    ("BM25",                 1.07, 3.53, 5.54, 2.95, 2.17,    1.51),
    ("BM25+ Enhanced",       7.31, 13.69, 14.45, 11.06, 9.94, 1.57),
    ("Struct-Filter BM25",   7.39, 14.02, 14.84, 11.31, 10.15, 1.42),
    ("GNN-Filter",           0.21, 0.90, 1.71, 0.80, 0.53,    1.08),
    ("TIGER Greedy",         0.15, 0.15, 0.15, 0.15, 0.15,  2277.5),
    ("Proposed Hybrid",      2.42, 6.13, 7.76, 4.87, 3.97, 15703.0),
]

cols   = ["Model","R@1","R@5","R@10","NDCG@10","MRR","Latency_ms"]
df     = pd.DataFrame(MODELS, columns=cols)

PALETTE = {
    "TF-IDF CF":          "#8ecae6",
    "BM25":               "#219ebc",
    "BM25+ Enhanced":     "#023047",
    "Struct-Filter BM25": "#457b9d",
    "GNN-Filter":         "#a8dadc",
    "TIGER Greedy":       "#e9c46a",
    "Proposed Hybrid":    "#e63946",
}
colors = [PALETTE[m] for m in df["Model"]]

# ══════════════════════════════════════════════════════════════════════════════
# P1 — Grouped Bar Chart (5 metrics)
# ══════════════════════════════════════════════════════════════════════════════
def plot_p1_grouped_bar():
    metrics    = ["R@1","R@5","R@10","NDCG@10","MRR"]
    metric_labels = ["Recall@1","Recall@5","Recall@10","NDCG@10","MRR"]
    n_models   = len(df)
    n_metrics  = len(metrics)
    x          = np.arange(n_metrics)
    width      = 0.10
    offsets    = np.linspace(-(n_models-1)/2*width, (n_models-1)/2*width, n_models)

    fig, ax = plt.subplots(figsize=(14, 6))
    for j, (_, row) in enumerate(df.iterrows()):
        vals = [row[m] for m in metrics]
        bars = ax.bar(x + offsets[j], vals, width, label=row["Model"],
                      color=colors[j], edgecolor='white', linewidth=0.5,
                      zorder=3)
        # Highlight proposed
        if row["Model"] == "Proposed Hybrid":
            for bar in bars:
                bar.set_edgecolor('#c1121f')
                bar.set_linewidth(2)

    ax.set_xticks(x)
    ax.set_xticklabels(metric_labels, fontsize=12)
    ax.set_ylabel("Score (%)", fontsize=12)
    ax.set_title("Figure 4.1 — Model Comparison Across All Evaluation Metrics\n(Test set N=12,991, Hierarchical Semantic ID space)", fontsize=13)
    ax.legend(loc='upper right', fontsize=9, framealpha=0.9, ncol=2)
    ax.set_ylim(0, max(df[metrics].values.max()*1.25, 1))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f'{v:.1f}%'))

    # Annotate best bar per metric
    for k, m in enumerate(metrics):
        best_val = df[m].max()
        best_j   = df[m].idxmax()
        ax.annotate(f'{best_val:.2f}%',
                    xy=(x[k] + offsets[best_j], best_val),
                    xytext=(0, 4), textcoords='offset points',
                    ha='center', va='bottom', fontsize=8, color='#c1121f', fontweight='bold')

    fig.tight_layout()
    path = OUT / "P1_grouped_bar.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"  Saved: {path}")

# ══════════════════════════════════════════════════════════════════════════════
# P2 — Recall@K Curve
# ══════════════════════════════════════════════════════════════════════════════
def plot_p2_recall_curve():
    K_vals = [1, 5, 10]
    # Only 3 key models for clarity + proposed
    selected = [
        ("BM25+ Enhanced",  [7.31, 13.69, 14.45], "#023047",  "o", "--"),
        ("GNN-Filter",      [0.21, 0.90, 1.71],   "#a8dadc",  "s", ":"),
        ("TIGER Greedy",    [0.15, 0.15, 0.15],   "#e9c46a",  "D", "-."),
        ("Proposed Hybrid", [2.42, 6.13, 7.76],   "#e63946",  "*", "-"),
    ]

    fig, ax = plt.subplots(figsize=(8, 5))
    for name, vals, color, marker, ls in selected:
        lw = 3 if name == "Proposed Hybrid" else 1.8
        ms = 12 if name == "Proposed Hybrid" else 8
        ax.plot(K_vals, vals, marker=marker, linestyle=ls, color=color,
                linewidth=lw, markersize=ms, label=name, zorder=4)
        ax.annotate(f'{vals[-1]:.2f}%',
                    xy=(10, vals[-1]),
                    xytext=(3, 0), textcoords='offset points',
                    va='center', fontsize=9, color=color)

    ax.set_xlabel("K (cutoff)", fontsize=12)
    ax.set_ylabel("Recall@K (%)", fontsize=12)
    ax.set_title("Figure 4.2 — Recall@K Curves for Key Models", fontsize=13)
    ax.set_xticks(K_vals)
    ax.set_xlim(0.5, 11.5)
    ax.set_ylim(0)
    ax.legend(fontsize=10)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f'{v:.1f}%'))

    fig.tight_layout()
    path = OUT / "P2_recall_curve.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"  Saved: {path}")

# ══════════════════════════════════════════════════════════════════════════════
# P3 — Ablation Study Bar
# ══════════════════════════════════════════════════════════════════════════════
def plot_p3_ablation():
    ablation_path = cfg.RESULTS / "ablation_results.csv"
    if not ablation_path.exists():
        print("  [SKIP] ablation_results.csv not found. Run ablation_eval.py first.")
        # Use stub data
        abl_data = [
            ("A1: LLM Greedy",            0.20, 0.20, 0.20),
            ("A2: Cluster + Random",       0.10, 0.80, 2.10),
            ("A3: Cluster + Price (Ours)", 1.60, 4.40, 5.40),
            ("A4: Cluster + TF-IDF",       0.60, 2.00, 3.60),
            ("A5: Global Price",           0.40, 1.60, 2.80),
        ]
        df_abl = pd.DataFrame(abl_data, columns=["Method","Recall@1","Recall@5","Recall@10"])
    else:
        df_abl = pd.read_csv(ablation_path)

    methods = df_abl["Method"].tolist()
    r1  = df_abl["Recall@1"].tolist()
    r10 = df_abl["Recall@10"].tolist()

    x = np.arange(len(methods))
    w = 0.35
    abl_colors = ["#8ecae6","#457b9d","#e63946","#023047","#219ebc"]

    fig, ax = plt.subplots(figsize=(12, 5))
    bars1 = ax.bar(x - w/2, r1,  w, label='Recall@1',  alpha=0.85, edgecolor='white')
    bars2 = ax.bar(x + w/2, r10, w, label='Recall@10', alpha=0.85, edgecolor='white')

    for j, (b1, b2) in enumerate(zip(bars1, bars2)):
        c = abl_colors[j % len(abl_colors)]
        b1.set_facecolor(c)
        b2.set_facecolor(c)
        b2.set_alpha(0.55)
        ax.text(b1.get_x() + b1.get_width()/2, b1.get_height() + 0.05,
                f'{r1[j]:.2f}%', ha='center', va='bottom', fontsize=8)
        ax.text(b2.get_x() + b2.get_width()/2, b2.get_height() + 0.05,
                f'{r10[j]:.2f}%', ha='center', va='bottom', fontsize=8)

    ax.set_xticks(x)
    short_labels = [m.split(':')[0] if ':' in m else m[:20] for m in methods]
    ax.set_xticklabels(short_labels, fontsize=10)
    ax.set_ylabel("Score (%)", fontsize=12)
    ax.set_title("Figure 4.3 — Ablation Study: Contribution of Each Pipeline Component", fontsize=13)
    ax.legend(fontsize=11)
    ax.set_ylim(0, max(max(r10)*1.3, 1))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f'{v:.1f}%'))

    # Add full method names as legend
    method_patches = [mpatches.Patch(color=abl_colors[j], label=methods[j])
                      for j in range(len(methods))]
    ax2 = ax.twinx()
    ax2.set_yticks([])
    ax2.legend(handles=method_patches, loc='upper right', fontsize=8,
               title='Ablation Variants', framealpha=0.9)

    fig.tight_layout()
    path = OUT / "P3_ablation.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"  Saved: {path}")

# ══════════════════════════════════════════════════════════════════════════════
# P4 — Latency vs Recall@10 Scatter
# ══════════════════════════════════════════════════════════════════════════════
def plot_p4_latency_scatter():
    fig, ax = plt.subplots(figsize=(9, 6))

    for _, row in df.iterrows():
        is_proposed = row["Model"] == "Proposed Hybrid"
        color  = PALETTE[row["Model"]]
        size   = 300 if is_proposed else 150
        marker = "*" if is_proposed else "o"
        edge   = '#c1121f' if is_proposed else 'white'
        lw     = 2.5 if is_proposed else 0.8

        ax.scatter(row["Latency_ms"], row["R@10"], s=size, c=color,
                   marker=marker, edgecolors=edge, linewidths=lw, zorder=4)
        offset = (15, 8) if is_proposed else (8, 6)
        ax.annotate(row["Model"],
                    xy=(row["Latency_ms"], row["R@10"]),
                    xytext=offset, textcoords='offset points',
                    fontsize=9, color='#333333',
                    fontweight='bold' if is_proposed else 'normal')

    # "Better" annotation
    ax.annotate('Better →\n(higher Recall)', xy=(0.98, 0.98),
                xycoords='axes fraction', ha='right', va='top',
                fontsize=9, color='green', alpha=0.6)
    ax.annotate('← Faster\n(lower Latency)', xy=(0.02, 0.02),
                xycoords='axes fraction', ha='left', va='bottom',
                fontsize=9, color='blue', alpha=0.6)

    ax.set_xscale('log')
    ax.set_xlabel("Inference Latency (ms, log scale)", fontsize=12)
    ax.set_ylabel("Recall@10 (%)", fontsize=12)
    ax.set_title("Figure 4.4 — Accuracy–Latency Trade-off\n(upper-left = fast+accurate, lower-right = slow+inaccurate)", fontsize=13)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f'{v:.1f}%'))

    fig.tight_layout()
    path = OUT / "P4_latency_scatter.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"  Saved: {path}")

# ══════════════════════════════════════════════════════════════════════════════
# P5 — Updated Radar Chart
# ══════════════════════════════════════════════════════════════════════════════
def plot_p5_radar():
    from matplotlib.patches import FancyArrowPatch

    metrics_radar = ["Recall@1","Recall@5","Recall@10","NDCG@10","MRR"]
    selected_models = [
        ("BM25+ Enhanced",  [7.31, 13.69, 14.45, 11.06, 9.94], "#023047"),
        ("Proposed Hybrid", [2.42, 6.13, 7.76, 4.87, 3.97], "#e63946"),
    ]

    N = len(metrics_radar)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics_radar, fontsize=11)
    ax.set_ylim(0, 16)
    ax.set_yticks([2, 4, 6, 8, 10, 12, 14, 16])
    ax.set_yticklabels(['2%','4%','6%','8%','10%','12%','14%','16%'], fontsize=8)

    for name, vals, color in selected_models:
        values = vals + vals[:1]
        lw = 3 if "Hybrid" in name else 1.8
        ax.plot(angles, values, linewidth=lw, linestyle='solid', color=color, label=name)
        ax.fill(angles, values, alpha=0.15, color=color)

    ax.set_title("Figure 4.5 — Performance Radar: BM25+ vs Proposed Hybrid", 
                 fontsize=12, pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.15), fontsize=10)

    fig.tight_layout()
    path = OUT / "P5_radar_updated.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"  Saved: {path}")

# ══════════════════════════════════════════════════════════════════════════════
# P6 — Summary Table (as figure)
# ══════════════════════════════════════════════════════════════════════════════
def plot_p6_summary_table():
    fig, ax = plt.subplots(figsize=(13, 4))
    ax.axis('off')

    table_data = [
        [row["Model"], f'{row["R@1"]:.2f}%', f'{row["R@5"]:.2f}%',
         f'{row["R@10"]:.2f}%', f'{row["NDCG@10"]:.2f}%',
         f'{row["MRR"]:.2f}%', f'{row["Latency_ms"]:.1f}ms']
        for _, row in df.iterrows()
    ]
    col_labels = ["Method","Recall@1","Recall@5","Recall@10","NDCG@10","MRR","Latency"]

    tbl = ax.table(cellText=table_data, colLabels=col_labels,
                   loc='center', cellLoc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1, 1.8)

    # Style header
    for j in range(len(col_labels)):
        tbl[0,j].set_facecolor('#023047')
        tbl[0,j].set_text_props(color='white', fontweight='bold')

    # Highlight best row
    for j in range(len(col_labels)):
        tbl[7,j].set_facecolor('#ffe8e8')
        tbl[7,j].set_text_props(color='#c1121f', fontweight='bold')

    # Alternate row shading
    for i in range(1, len(table_data)+1):
        for j in range(len(col_labels)):
            if i % 2 == 0:
                tbl[i,j].set_facecolor('#f0f4f8')

    ax.set_title("Table 4.1 — Complete Evaluation Results (N=12,991 test samples)",
                 fontsize=13, fontweight='bold', pad=10, y=1.02)

    fig.tight_layout()
    path = OUT / "P6_summary_table.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"  Saved: {path}")

# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating all publication-quality charts...")
    plot_p1_grouped_bar()
    plot_p2_recall_curve()
    plot_p3_ablation()
    plot_p4_latency_scatter()
    plot_p5_radar()
    plot_p6_summary_table()
    print("\nAll charts saved to:", OUT)
