# Generative Retrieval for Explainable Wine Recommendation using Large Language Models

**Tác giả:** Trần Thành Trung — MSHV: 251805014  
**GVHD:** TS. Trần Trung Tín  
**Trường:** Đại học Tôn Đức Thắng — Khoa Công nghệ Thông tin  
**Năm:** 2026

---

## 📌 Tóm tắt

Hệ thống gợi ý rượu vang kết hợp **Generative Retrieval** (TIGER-style Semantic-ID Generative Retrieval với Llama-3-8B LoRA) và **Collaborative Filtering** trên hai tập dữ liệu:
- **Winemag-130K**: 129,915 chai rượu vang quốc tế → đánh giá Cold-Start
- **Sapo (Việt Nam)**: 305 sản phẩm, 400+ khách hàng → đánh giá Warm-Start

### Kết quả chính — Tập test chuẩn (N=12,991, Cold-Start)

| Phương pháp | Recall@1 | Recall@10 | NDCG@10 | MRR | Latency |
|:---|:---:|:---:|:---:|:---:|:---:|
| TF-IDF CF | 0.31% | 2.59% | 1.23% | 0.82% | 1.1ms |
| BM25 | 1.07% | 5.54% | 2.95% | 2.17% | 1.5ms |
| BM25+ Enhanced | 7.31% | 14.45% | 11.06% | 9.94% | 1.6ms |
| Struct-Filter BM25 | 7.39% | 14.84% | 11.31% | 10.15% | 1.4ms |
| GNN-Filter | 0.21% | 1.71% | 0.80% | 0.53% | 1.1ms |
| TIGER Greedy | 0.15% | 0.15% | 0.15% | 0.15% | 2,278ms |
| Model 1 — TIGER-style + Price Rerank | 2.42% | 7.76% | 4.87% | 3.97% | 15,703ms |
| **Model 2 — Parser-Filter-Sommelier** | **10.03%** | **39.42%** | **22.86%** | **17.79%** | **86.6ms** |

### 🔥 Noisy Realistic Mixed Benchmark (N=12,991 — truy vấn nhiễu thực tế)

> 50% Nhóm A: câu hỏi từ tập test bị gây nhiễu nặng (xóa giống nho, sai chính tả).  
> 50% Nhóm B: câu hỏi ngắn 7–10 từ thực tế từ kinh nghiệm bán hàng (không dùng tên giống nho).

| Phương pháp | Recall@1 | Recall@10 | NDCG@10 | MRR |
|:---|:---:|:---:|:---:|:---:|
| TF-IDF CF | 0.06% | 0.69% | 0.32% | 0.21% |
| BM25 | 0.18% | 0.79% | 0.44% | 0.34% |
| Struct-Filter BM25 | 0.18% | 0.79% | 0.44% | 0.34% |
| TIGER Greedy | 8.51% | 8.51% | 8.51% | 8.51% |
| Model 2 — Parser-Filter-Sommelier | 4.98% | 20.87% | 11.83% | 9.08% |
| **Model 1 — TIGER-style + Price Rerank** | **33.49%** | **75.84%** | **54.42%** | **47.56%** |

> 📁 Kết quả đầy đủ: [`results/noisy_query_12k_all_models_results.csv`](results/noisy_query_12k_all_models_results.csv)  
> 📄 Báo cáo chi tiết: [`results/noisy_realistic_evaluation_report.docx`](results/noisy_realistic_evaluation_report.docx)  
> 📝 Log đánh giá: [`results/run_logs/run_noisy_query_all_models.log`](results/run_logs/run_noisy_query_all_models.log)

---

## 📁 Cấu trúc thư mục

```
CD3/
├── data/
│   ├── raw/                     # Winemag 130K CSV gốc
│   ├── processed/               # Catalog + test/train/val sets với Semantic ID
│   │   ├── wine_catalog_semantic.csv   # 130K wines + Semantic_ID + Cluster
│   │   ├── wine_train_130k.jsonl
│   │   ├── wine_val_130k.jsonl
│   │   └── wine_test_130k.jsonl
│   └── sapo/                    # Dữ liệu Sapo (đã ẩn danh)
│       ├── sapo_catalog.csv
│       ├── sapo_interactions.csv
│       └── sapo_test.jsonl
├── src/
│   ├── data/                    # Data preprocessing scripts
│   ├── models/                  # Model definitions
│   └── training/                # LoRA fine-tuning scripts
├── evaluation/                  # Evaluation scripts
├── demo/
│   ├── app.py                   # Flask backend (BM25/TF-IDF/CF/LLM demo)
│   ├── index.html               # Web UI demo
│   └── error_analysis_data.json # Pre-computed error analysis
├── results/                     # Saved evaluation results
│   ├── constrained_eval_beam10_500.csv  # TIGER beam search results
│   ├── baseline_comparison.csv          # All baseline results
│   └── sapo_ablation_results.csv        # Sapo ablation study
├── Sapo/                        # Sapo raw data + ablation scripts
├── thesis/                      # project document
├── requirements.txt
└── README.md
```

---

## ⚙️ Cài đặt môi trường

### Yêu cầu
- Python 3.10+
- CUDA 11.8+ (để fine-tune, không bắt buộc để chạy demo)
- RAM: ≥ 16GB (để load Winemag 130K index)

### Bước 1: Tạo môi trường ảo

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

### Bước 2: Cài dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt` chính:
```
flask>=3.0
pandas>=2.0
numpy>=1.24
scikit-learn>=1.3
rank-bm25>=0.2.2
transformers>=4.40
peft>=0.9           # LoRA fine-tuning
torch>=2.1          # với CUDA
bitsandbytes>=0.43  # 4-bit quantization
```

---

## 🚀 Chạy Demo (Không cần GPU)

Demo sử dụng BM25/TF-IDF thực tế + mô phỏng Inference LLM:

```bash
# Windows
.venv\Scripts\python.exe demo\app.py

# Linux/Mac
.venv/bin/python demo/app.py
```

Mở trình duyệt: **http://localhost:5005**

### Các tính năng Demo:
| Tab | Mô tả |
|-----|-------|
| 🔍 Tìm kiếm | BM25 / TF-IDF / Winemag 130K / TIGER-style Llama-3 (simulated) |
| ⚖️ So sánh | 5 phương pháp song song: M1-M5 |
| 👤 Gợi ý Cá nhân | CF trên dữ liệu Sapo thực (khách hàng đã ẩn danh) |
| 💡 Giải thích | Tại sao hệ thống recommend sản phẩm đó |
| 🔬 Phân tích Lỗi | Error analysis từ N=500 test cases thực tế |
| 📊 Kết quả | Bảng so sánh và SOTA comparison |

---

## 🔬 Reproduce Kết quả

### 1. Chuẩn bị dữ liệu

```bash
# Đã có sẵn trong data/processed/
# Nếu cần re-generate từ raw data:
.venv\Scripts\python.exe src/data/preprocess_winemag.py
```

### 2. Sinh Semantic ID (K-Means Hierarchical)

```bash
.venv\Scripts\python.exe src/data/generate_semantic_ids.py \
  --input data/raw/winemag-data-130k-v2.csv \
  --output data/processed/wine_catalog_semantic.csv \
  --n_clusters 16 --depth 3
```

### 3. Fine-tune Llama-3 với LoRA (cần GPU A100/H100 hoặc Colab Pro)

```bash
# Xem hướng dẫn chi tiết trong colab_instructions.md
# hoặc chạy:
.venv\Scripts\python.exe src/training/train_lora.py \
  --model meta-llama/Meta-Llama-3-8B \
  --train_data data/processed/wine_train_130k.jsonl \
  --output_dir results/training_outputs \
  --lora_r 16 --lora_alpha 32 \
  --num_epochs 3 --batch_size 4
```

### 4. Đánh giá Baseline

```bash
.venv\Scripts\python.exe evaluation/eval_baselines.py \
  --test data/processed/wine_test_130k.jsonl \
  --catalog data/processed/wine_catalog_semantic.csv \
  --n 500
```

### 5. Đánh giá mô hình Generative Retrieval dạng TIGER (TIGER-style)

```bash
# Cần model đã fine-tune
.venv\Scripts\python.exe evaluation/eval_tiger.py \
  --model_path results/training_outputs/checkpoint-best \
  --test data/processed/wine_test_130k.jsonl \
  --output results/constrained_eval_beam10_500.csv \
  --beam_size 10 --n 500
```

### 6. Ablation Study Sapo

```bash
.venv\Scripts\python.exe Sapo/sapo_ablation.py
# Output: results/sapo_ablation_results.csv
```

---

## 📊 Kiến trúc hệ thống

```
Query (Natural Language)
         │
         ▼
   ┌─────────────┐
   │  Llama-3-8B │  ← Fine-tuned với LoRA (rank=16)
   │    LoRA     │     Constrained Decoding
   └──────┬──────┘
          │ Semantic ID: [C1-C2-C3-item]
          ▼
   ┌─────────────┐
   │   Cluster   │  K-Means (16^3 = 4096 clusters)
   │   Filter    │  → Lọc từ 130K xuống ~50 ứng viên
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │    Price    │  Re-rank theo giá gần nhất với query
   │   Reranker  │
   └──────┬──────┘
          │
          ▼
      Top-10 Results + Explanations
```

---

## 📖 Tài liệu tham khảo chính

1. **TIGER** — Rajput et al., 2023. "Recommender Systems with Generative Retrieval." *NeurIPS 2023*.
2. **DSI** — Tay et al., 2022. "Transformer Memory as a Differentiable Search Index." *NeurIPS 2022*.
3. **P5** — Geng et al., 2022. "Recommendation as Language Processing." *RecSys 2022*.
4. **Llama-3** — Meta AI, 2024. "Introducing Meta Llama 3." Meta Blog.
5. **BIGRec** — Hou et al., 2023. "Bridging Language and Items for Retrieval and Recommendation." *arXiv*.

---

## 📝 License & Dữ liệu

- **Winemag dataset**: Nguồn Kaggle (CC BY-NC-SA 4.0)
- **Sapo dataset**: Dữ liệu thực tế được ẩn danh hóa, chỉ dùng cho mục đích nghiên cứu học thuật
- **Code**: MIT License

---

*Đây là đề tài Chuyên đề 3 tại Đại học Tôn Đức Thắng, Khoa Công nghệ Thông tin, 2026.*
