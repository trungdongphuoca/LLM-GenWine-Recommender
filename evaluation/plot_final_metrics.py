import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns

def main():
    # Cấu hình thẩm mỹ (Nền trắng, trực quan)
    sns.set_theme(style="whitegrid")
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['font.family'] = 'sans-serif'
    
    output_dir = 'results/final_metrics'
    os.makedirs(output_dir, exist_ok=True)

    # Dữ liệu
    models = ['Baseline (Text IDs)', 'TIGER (Hierarchical IDs)']
    
    data = {
        'Valid_ID_Rate': [0.0, 99.61],
        'Exact_Match': [0.0, 0.15],
        'Cluster_Match': [0.0, 9.67],  # Baseline không có khái niệm Cluster nên coi như 0
        'Latency_ms': [3500.0, 2277.5]
    }

    metrics = [
        ('Valid_ID_Rate', 'Tỷ lệ sinh mã hợp lệ (Valid ID Rate) %', '%', 'blue'),
        ('Exact_Match', 'Độ chính xác tuyệt đối (Exact Match / Recall@1) %', '%', 'green'),
        ('Cluster_Match', 'Tỷ lệ đoán trúng Cụm hương vị (Cluster Match) %', '%', 'orange'),
        ('Latency_ms', 'Độ trễ trung bình mỗi truy vấn (Latency) ms', 'ms', 'red')
    ]

    for key, title, unit, color in metrics:
        # 1. Lưu ra file CSV riêng cho từng thước đo
        df = pd.DataFrame({
            'Model': models,
            key: data[key]
        })
        csv_path = os.path.join(output_dir, f'{key}_evaluation.csv')
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"Đã lưu dữ liệu: {csv_path}")

        # 2. Vẽ biểu đồ riêng
        plt.figure(figsize=(8, 6))
        # Màu sắc tùy chỉnh theo từng metric
        if color == 'blue':
            pal = ['#ADD8E6', '#00008B']
        elif color == 'green':
            pal = ['#90EE90', '#006400']
        elif color == 'orange':
            pal = ['#FFDAB9', '#FF8C00']
        else: # red
            pal = ['#F08080', '#8B0000']
            
        ax = sns.barplot(x='Model', y=key, hue='Model', data=df, palette=pal, edgecolor="black", legend=False)
        
        plt.title(title, fontsize=14, fontweight='bold', pad=20)
        plt.ylabel(f'{key} ({unit})', fontsize=12)
        plt.xlabel('', fontsize=12)
        
        # Tùy chỉnh trục Y để có khoảng trống phía trên cho text
        max_val = max(data[key])
        plt.ylim(0, max_val * 1.2 if max_val > 0 else 1)

        # Gắn label giá trị lên từng cột
        for p in ax.patches:
            height = p.get_height()
            ax.annotate(f'{height:.2f} {unit}',
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom',
                        fontsize=12, fontweight='bold',
                        xytext=(0, 5),
                        textcoords='offset points')

        # Xóa viền trên và phải cho đẹp
        sns.despine()

        # Lưu ảnh
        img_path = os.path.join(output_dir, f'{key}_comparison.png')
        plt.tight_layout()
        plt.savefig(img_path, dpi=300, bbox_inches='tight', facecolor='white', transparent=False)
        plt.close()
        print(f"Đã lưu biểu đồ: {img_path}")

if __name__ == "__main__":
    main()
