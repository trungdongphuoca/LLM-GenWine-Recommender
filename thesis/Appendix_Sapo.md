# PHỤ LỤC A — SAPO ABLATION STUDY
## Đánh giá trên Dữ liệu Rượu vang Thực tế Việt Nam (Sapo)

---

## A.1. Giới thiệu

Để kiểm chứng tính tổng quát hóa của phương pháp và làm rõ vai trò của **dữ liệu lịch sử người dùng**, luận văn thực hiện thêm một ablation study độc lập trên bộ dữ liệu **Sapo** — dữ liệu kinh doanh rượu vang thực tế của một cửa hàng tại Việt Nam.

Đây là điểm khác biệt cốt lõi so với bộ dữ liệu Winemag:

| Đặc điểm | Winemag (chính) | **Sapo (ablation)** |
|----------|----------------|---------------------|
| Ngôn ngữ | Tiếng Anh | **Tiếng Việt** |
| Catalog | 130,000 SP | **305 SP** |
| Lịch sử tương tác | ❌ Không có | ✅ **733 interactions** |
| Khách hàng | ❌ Không có | ✅ **400 khách** |
| Loại bài toán | Cold-Start hoàn toàn | **Warm-Start + Cold-Start** |
| Nguồn dữ liệu | Wine Enthusiast Magazine | **POS + Zalo + Facebook** |
| Đánh giá | 500 mẫu ngẫu nhiên | **Leave-One-Out (N=150)** |

---

## A.2. Mô tả Dữ liệu Sapo

### A.2.1. Catalog Sản phẩm

- **305 sản phẩm** rượu vang unique (sau khi de-duplicate theo SKU)
- Phân loại: Rượu Vang Đỏ (240), Trắng (52), Bịch (9), Hồng (8)
- Giá bán: 70,000 – 6,280,000 VND (trung vị: 795,000 VND)
- **85.4% sản phẩm có mô tả chi tiết** bằng tiếng Việt
- Nhãn hiệu nổi bật: Montes, Antawara, Grant Burge, San Marzano

### A.2.2. Dữ liệu Đơn hàng và Khách hàng

- **980 đơn hàng** từ 5 kênh: POS (67%), Zalo (22%), Facebook (5%), Admin (3%), Website (3%)
- **400 khách hàng** unique có ít nhất 1 lần mua
- **202 khách hàng** mua ≥2 sản phẩm khác nhau → đủ điều kiện Leave-One-Out
- **150 mẫu test** sau khi lọc SKU hợp lệ trong catalog

### A.2.3. Phương pháp Đánh giá: Leave-One-Out

> Với mỗi khách hàng có ≥2 sản phẩm đã mua (theo thứ tự thời gian):
> - **Context**: tất cả sản phẩm đã mua trừ sản phẩm cuối cùng
> - **Ground truth**: sản phẩm cuối cùng đã mua
> - **Mục tiêu**: gợi ý đúng sản phẩm ground truth trong top-K

---

## A.3. Các Phương pháp So sánh

| ID | Tên | Mô tả | Dùng lịch sử? |
|----|-----|-------|--------------|
| **M1** | Content TF-IDF | TF-IDF cosine trên mô tả sản phẩm | ❌ |
| **M2** | Content BM25 | BM25 trên mô tả sản phẩm | ❌ |
| **M3** | Collaborative Filtering | User-Item cosine similarity matrix | ✅ |
| **M4** | Session-Based | SVD embedding trung bình của history items | ✅ |
| **M5** | Hybrid CF + Content | CF candidates → Content rerank | ✅ |

---

## A.4. Kết quả

### Bảng A.1 — Kết quả Sapo Ablation Study (N=150, Leave-One-Out)

| Phương pháp | Recall@1 | Recall@5 | Recall@10 | NDCG@10 | MRR |
|:------------|:--------:|:--------:|:---------:|:-------:|:---:|
| M1: Content TF-IDF (no history) | 1.33% | 15.33% | 18.67% | 9.86% | 7.06% |
| M2: Content BM25 (no history) | 0.67% | 14.00% | 21.33% | 10.39% | 6.98% |
| **M3: Collaborative Filtering** | **56.00%** | **74.67%** | **81.33%** | **68.52%** | **64.45%** |
| M4: Session-Based | 10.00% | 20.00% | 22.67% | 16.22% | 14.15% |
| M5: Hybrid CF + Content | 11.33% | 25.33% | 34.67% | 21.41% | 17.38% |

---

## A.5. Phân tích và Thảo luận

### A.5.1. Phát hiện chính: Lịch sử tương tác người dùng là yếu tố then chốt

Kết quả cho thấy sự khác biệt **đột biến** giữa các phương pháp có và không có lịch sử người dùng:

| | Content-only (M1/M2) | Có lịch sử (M3) | Tăng |
|--|:---:|:---:|:---:|
| Recall@1 | ~1.0% | **56.0%** | **+56×** |
| Recall@10 | ~20.0% | **81.3%** | **+4×** |
| NDCG@10 | ~10.1% | **68.5%** | **+6.8×** |

**Lý giải:** Trên catalog nhỏ (305 sản phẩm), khi một khách hàng đã mua một số chai rượu, các khách hàng "láng giềng" (similar users) trong CF rất dễ tìm thấy và có hành vi mua sắm gần như giống nhau → CF đạt hiệu suất cực cao.

### A.5.2. So sánh Cross-Domain: Sapo vs Winemag

**Kết luận cốt lõi về thiết kế hệ thống:**

> Khi **không có** dữ liệu tương tác người dùng (Winemag — Cold-Start hoàn toàn):
> → TIGER + Price Rerank đạt Recall@10 = **5.60%** — là phương pháp tốt nhất
>
> Khi **có** dữ liệu tương tác người dùng (Sapo — Warm-Start):
> → Collaborative Filtering đạt Recall@10 = **81.33%** — vượt trội tuyệt đối

Điều này khẳng định nguyên lý thiết kế hệ thống gợi ý thực tế:

```
Có user history (warm-start)  →  Ưu tiên Collaborative Filtering
Không có user history (cold-start)  →  Dùng TIGER + Semantic Filter
```

### A.5.3. Tại sao M5 (Hybrid) không vượt M3 (CF)?

Trên catalog nhỏ (305 SP), CF đã "over-fit" tốt vào hành vi mua sắm lặp lại. Content rerank trong M5 thực ra gây nhiễu khi khách hàng có xu hướng mua **đúng cùng loại** rượu nhiều lần (ví dụ: khách VIP chuyên mua Cabernet Sauvignon Pháp 500k–800k). Điều này là đặc thù của domain nhỏ với khách hàng trung thành cao.

### A.5.4. Ý nghĩa với Hướng Phát triển

Kết quả Sapo mở ra hướng phát triển rõ ràng cho hệ thống TIGER:

> **Hướng tiếp theo:** Tích hợp lịch sử mua vào context của LLM:
> - Input: *"Khách đã mua: [Cabernet Pháp 500k, Merlot Ý 350k]. Gợi ý tiếp?"*
> - LLM sinh Semantic ID của sản phẩm phù hợp nhất
> - Kết hợp CF (user similarity) + LLM (semantic understanding) → **Warm-start + Cold-start hybrid**

---

## A.6. Tổng kết Ablation Study

| Scenario | Dataset | Best Method | Recall@10 |
|----------|---------|-------------|-----------|
| Cold-Start (no user data) | Winemag | TIGER + Price Rerank | **5.60%** |
| Warm-Start (with user history) | Sapo | Collaborative Filtering | **81.33%** |
| Warm-Start + Content | Sapo | Hybrid CF + Content | **34.67%** |

**Kết luận:** Dữ liệu lịch sử người dùng cải thiện Recall@10 lên **+14.5×** so với không có (81.33% vs 5.60%), khẳng định đây là tài nguyên quý giá nhất trong hệ thống gợi ý thực tế.
