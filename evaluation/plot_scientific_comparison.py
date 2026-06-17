import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns
import numpy as np

def main():
    sns.set_theme(style="whitegrid")
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['font.family'] = 'sans-serif'
    
    output_dir = 'results/scientific_metrics'
    os.makedirs(output_dir, exist_ok=True)

    # 1. Load Baseline CSV
    baseline_csv = 'results/baseline_comparison.csv'
    if not os.path.exists(baseline_csv):
        print(f"Error: {baseline_csv} not found.")
        return
        
    df_base = pd.read_csv(baseline_csv)
    
    # Chọn ra các model đại diện tốt nhất để vẽ (tránh bị rối mắt)
    selected_models = ['BM25', 'TF-IDF CF', 'Struct-Filter BM25']
    df_plot = df_base[df_base['Method'].isin(selected_models)].copy()
    
    # 2. Thêm TIGER vào dataframe
    # Chú ý: TIGER dùng greedy decoding (chỉ sinh 1 kết quả) nên Recall@1 = Recall@10 = Exact Match (0.15%).
    # MRR của TIGER cũng chính là Exact Match.
    tiger_data = {
        'Method': 'TIGER (Generative LLM)',
        'Recall@1': 0.0015,
        'Recall@10': 0.0015,
        'MRR': 0.0015,
        'IntentMatch@1': 0.0967,  # Cluster Match của TIGER
        'Latency_ms': 2277.5
    }
    df_tiger = pd.DataFrame([tiger_data])
    df_plot = pd.concat([df_plot, df_tiger], ignore_index=True)
    
    # Chuyển đổi Recall, MRR sang phần trăm (%) cho dễ nhìn
    df_plot['Recall@1 (%)'] = df_plot['Recall@1'] * 100
    df_plot['Recall@10 (%)'] = df_plot['Recall@10'] * 100
    df_plot['MRR (%)'] = df_plot['MRR'] * 100
    df_plot['IntentMatch@1 (%)'] = df_plot['IntentMatch@1'] * 100
    
    metrics = [
        ('Recall@1 (%)', 'Recall@1 (Exact Match)', '%', 'Blues'),
        ('Recall@10 (%)', 'Recall@10', '%', 'Greens'),
        ('MRR (%)', 'Mean Reciprocal Rank (MRR)', '%', 'Oranges'),
        ('IntentMatch@1 (%)', 'Intent Match @ 1 (Cluster Match)', '%', 'Purples'),
        ('Latency_ms', 'Inference Latency', 'ms', 'Reds')
    ]

    for col, title, unit, cmap in metrics:
        # Lưu CSV
        out_csv = os.path.join(output_dir, f'{col.split()[0].replace("@", "_")}_comparison.csv')
        df_out = df_plot[['Method', col]].copy()
        df_out.to_csv(out_csv, index=False)
        print(f"Đã lưu: {out_csv}")
        
        # Vẽ biểu đồ
        plt.figure(figsize=(10, 6))
        ax = sns.barplot(x='Method', y=col, hue='Method', data=df_plot, palette=cmap, edgecolor="black", legend=False)
        
        plt.title(f'Comparison of {title}', fontsize=16, fontweight='bold', pad=20)
        plt.ylabel(f'{title} ({unit})', fontsize=14)
        plt.xlabel('', fontsize=14)
        plt.xticks(fontsize=12, rotation=15)
        
        # Thêm số liệu lên đỉnh cột
        max_val = df_plot[col].max()
        plt.ylim(0, max_val * 1.25 if max_val > 0 else 1)
        
        for p in ax.patches:
            height = p.get_height()
            ax.annotate(f'{height:.2f}{unit}',
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom',
                        fontsize=12, fontweight='bold',
                        xytext=(0, 5),
                        textcoords='offset points')

        sns.despine()
        plt.tight_layout()
        img_path = os.path.join(output_dir, f'{col.split()[0].replace("@", "_")}_chart.png')
        plt.savefig(img_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"Đã lưu ảnh: {img_path}")

if __name__ == "__main__":
    main()
