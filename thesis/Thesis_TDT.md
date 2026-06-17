TỔNG LIÊN ĐOÀN LAO ĐỘNG VIỆT NAM  
TRƯỜNG ĐẠI HỌC TÔN ĐỨC THẮNG  
KHOA CÔNG NGHỆ THÔNG TIN  

<br><br><br><br>

**TRẦN THÀNH TRUNG**  

<br><br><br><br>

# TRUY XUẤT TẠO SINH TRONG HỆ GỢI Ý RƯỢU VANG CÓ KHẢ NĂNG GIẢI THÍCH SỬ DỤNG MÔ HÌNH NGÔN NGỮ LỚN

<br><br><br><br>

**LUẬN VĂN THẠC SĨ**  
**Chuyên ngành: Khoa học Máy tính**  

<br><br><br><br><br><br>

**THÀNH PHỐ HỒ CHÍ MINH, NĂM 2026**

<!-- PAGE_BREAK -->

TỔNG LIÊN ĐOÀN LAO ĐỘNG VIỆT NAM  
TRƯỜNG ĐẠI HỌC TÔN ĐỨC THẮNG  
KHOA CÔNG NGHỆ THÔNG TIN  

<br><br><br><br>

**TRẦN THÀNH TRUNG**  
**MSHV: 251805014**  

<br><br><br><br>

# TRUY XUẤT TẠO SINH TRONG HỆ GỢI Ý RƯỢU VANG CÓ KHẢ NĂNG GIẢI THÍCH SỬ DỤNG MÔ HÌNH NGÔN NGỮ LỚN

<br><br><br><br>

**LUẬN VĂN THẠC SĨ**  
**Chuyên ngành: Khoa học Máy tính**  

<br><br><br>

**Người hướng dẫn khoa học: TS. Trần Trung Tín**  

<br><br><br><br><br>

**THÀNH PHỐ HỒ CHÍ MINH, NĂM 2026**

<!-- PAGE_BREAK -->

# LỜI CẢM ƠN

Lời đầu tiên, tôi xin bày tỏ lòng biết ơn sâu sắc nhất tới TS. Trần Trung Tín, người hướng dẫn khoa học trực tiếp của tôi. Trong suốt quá trình học tập và thực hiện đề tài luận văn thạc sĩ này, Thầy đã luôn dành nhiều thời gian, tâm huyết để tận tình hướng dẫn, định hướng khoa học, đóng góp những ý kiến vô cùng quý báu và động viên tinh thần giúp tôi vượt qua những giai đoạn khó khăn để hoàn thành nghiên cứu một cách trọn vẹn nhất.

Tôi cũng xin trân trọng cảm ơn Ban Giám hiệu, Phòng Đào tạo Sau đại học cùng toàn thể Quý Thầy/Cô Khoa Công nghệ Thông tin, Trường Đại học Tôn Đức Thắng đã giảng dạy, truyền đạt những tri thức khoa học quý báu và tạo mọi điều kiện thuận lợi nhất về cơ sở vật chất, trang thiết bị phòng thí nghiệm trong suốt những năm tháng tôi học tập và nghiên cứu tại trường.

Cuối cùng, tôi xin gửi lời tri ân sâu sắc tới gia đình, bạn bè và các đồng nghiệp tại phòng nghiên cứu lab khoa CNTT đã luôn bên cạnh chia sẻ, động viên, tạo động lực to lớn và hỗ trợ mọi mặt để tôi có thể tập trung hoàn thành tốt luận văn này. Sự thành công của công trình này là kết quả của sự đồng hành và giúp đỡ to lớn của mọi người.

TP. Hồ Chí Minh, ngày 17 tháng 6 năm 2026  
Học viên  

*Trần Thành Trung*

<!-- PAGE_BREAK -->

# LỜI CAM ĐOAN

Tôi xin cam đoan luận văn thạc sĩ khoa học *"Truy xuất tạo sinh trong Hệ gợi ý rượu vang có khả năng giải thích sử dụng mô hình ngôn ngữ lớn"* này hoàn toàn là công trình nghiên cứu và kết quả làm việc thực chất của riêng tôi dưới sự hướng dẫn khoa học trực tiếp của TS. Trần Trung Tín.

Các nội dung lý thuyết, phương pháp đề xuất, số liệu thực nghiệm và các kết quả phân tích đánh giá được trình bày trong luận văn này là hoàn toàn trung thực, khách quan và chưa từng được công bố hoặc sử dụng dưới bất kỳ hình thức nào trước đây để nhận các học vị hay chứng chỉ học thuật khác.

Mọi tài liệu tham khảo, hình vẽ, bảng biểu, công thức toán học và các trích dẫn sử dụng trong luận văn đều được tôi kiểm chứng và ghi rõ nguồn gốc xuất xứ cụ thể, minh bạch, tuân thủ đúng các quy định về sở hữu trí tuệ và đạo đức khoa học. Tôi xin hoàn toàn chịu trách nhiệm trước Hội đồng đánh giá luận văn và Nhà trường về tính chân thực của các nội dung cam đoan ở trên.

TP. Hồ Chí Minh, ngày 17 tháng 6 năm 2026  
Tác giả luận văn  

*Trần Thành Trung*

<!-- PAGE_BREAK -->

# TÓM TẮT

Hệ thống gợi ý rượu vang truyền thống thường phụ thuộc vào các phương pháp Lọc cộng tác (Collaborative Filtering) hoặc Lọc theo nội dung (Content-Based Filtering), vốn gặp nhiều hạn chế trước bài toán khởi động lạnh (Cold-Start) và thiếu khả năng giải thích ngữ nghĩa rõ ràng. Đề tài này đề xuất và hiện thực hai mô hình gợi ý rượu vang lai mới sử dụng Mô hình Ngôn ngữ Lớn (LLM) nhằm giải quyết các thách thức trên.

Mô hình 1 (TIGER + Price Rerank) kết hợp phương pháp Truy xuất Tạo sinh (Generative Retrieval) với LLM. Chúng tôi biểu diễn danh mục 130.000 chai rượu vang dưới dạng cây phân cấp ngữ nghĩa 3 tầng (16x16x16 = 4.096 cụm hương vị) thông qua thuật toán phân cụm K-Means phân cấp trên không gian TF-IDF/SVD. Mô hình Llama-3-8B được tinh chỉnh bằng kỹ thuật thích ứng hạng thấp LoRA dưới dạng lượng hóa 4-bit để học cách ánh xạ trực tiếp từ câu lệnh người dùng sang mã cụm ngữ nghĩa, kết hợp với bộ re-rank dựa trên khoảng cách giá.

Mô hình 2 (Parser-Filter-Sommelier) tách biệt quá trình lọc cấu trúc cứng và tạo lời lý giải. Mô hình dùng LLM trích xuất các ràng buộc cấu trúc từ truy vấn sang JSON, truy vấn nhanh trên danh mục rượu và dùng LLM sommelier viết lời lý giải chi tiết cho 1-2 chai nổi bật.

Kết quả đánh giá trên toàn bộ tập test gồm 12.991 mẫu cho thấy Mô hình 2 đạt hiệu năng vượt trội với Recall@10 = 39,42%, NDCG@10 = 22,86% và thời gian phản hồi lý tưởng 86,6ms. Trong khi đó, Mô hình 1 đạt Recall@10 = 7,76% nhưng thể hiện tính chịu lỗi và độ bền vững ngữ nghĩa rất cao trước các truy vấn chứa nhiều nhiễu và lỗi chính tả.

**Từ khóa:** Hệ gợi ý rượu vang, Truy xuất tạo sinh, Mô hình ngôn ngữ lớn, Semantic ID phân cấp, LoRA, Cold-Start.

<!-- PAGE_BREAK -->

# ABSTRACT

Conventional wine recommendation systems typically rely on Collaborative Filtering or Content-Based Filtering, which suffer from the cold-start problem and lack semantic explainability. This thesis proposes and implements two novel hybrid recommender architectures utilizing Large Language Models (LLMs) to overcome these limitations.

Model 1 (TIGER + Price Rerank) integrates Generative Retrieval with LLMs. We encode a catalog of 130,000 wine bottles into a 3-level semantic hierarchy (16x16x16 = 4,096 flavor clusters) via hierarchical K-Means clustering on a TF-IDF/SVD vector space. A Meta Llama-3-8B model is fine-tuned with 4-bit quantized LoRA to learn direct mapping from natural language queries to semantic cluster IDs, followed by a price-proximity reranker.

Model 2 (Parser-Filter-Sommelier) decouples physical structured filtering from explanation generation. It employs an LLM to parse natural queries into JSON constraints, performs database-level filtering, and utilizes a generative sommelier rationale module to write detailed reviews for the top 1-2 recommended wines.

Experimental results on the full test set of 12,991 samples show that Model 2 achieves state-of-the-art performance with Recall@10 = 39.42%, NDCG@10 = 22.86%, and a low latency of 86.6ms. Meanwhile, Model 1 achieves Recall@10 = 7.76% but exhibits exceptional robustness and semantic adaptability on noisy and misspelled queries.

**Keywords:** Wine recommendation, Generative retrieval, Large language models, Hierarchical Semantic ID, LoRA, Cold-start.

<!-- PAGE_BREAK -->

# MỤC LỤC

DANH MỤC HÌNH VẼ	v  
DANH MỤC BẢNG BIỂU	vi  
DANH MỤC CÁC CHỮ VIẾT TẮT	vii  
CHƯƠNG 1. MỞ ĐẦU	1  
1.1 Lý do chọn đề tài	1  
1.2 Mục tiêu thực hiện đề tài	2  
1.3 Đối tượng và phạm vi nghiên cứu	3  
1.4 Phương pháp nghiên cứu	4  
1.5 Ý nghĩa thực tiễn của đề tài	4  
1.6 Môi trường thực hiện nghiên cứu	5  
CHƯƠNG 2. TỔNG QUAN	6  
2.1 Giới thiệu về Hệ gợi ý	6  
2.2 Các phương pháp gợi ý truyền thống	6  
2.3 Các phương pháp gợi ý hiện đại	7  
2.4 Bối cảnh đào tạo và Nghiên cứu tại Trường	8  
CHƯƠNG 3. CƠ SỞ LÝ THUYẾT	9  
3.1 Truy xuất Tạo sinh (Generative Retrieval)	9  
3.2 Mô hình TIGER	10  
3.3 Mô hình Ngôn ngữ Lớn và Tinh chỉnh LoRA	10  
3.4 Phân tích Số liệu Dữ liệu Nghiên cứu	11  
CHƯƠNG 4. PHƯƠNG PHÁP NGHIÊN CỨU	12  
4.1 Kiến trúc Hệ thống Tổng thể	12  
4.2 Xây dựng Hierarchical Semantic IDs cho rượu vang	13  
4.3 Tinh chỉnh LLM Llama-3-8B với LoRA	14  
4.4 Thiết kế Mô hình 1: TIGER + Price Rerank	15  
4.5 Thiết kế Mô hình 2: Parser-Filter-Sommelier	16  
4.6 Giải thích Hậu nghiệm với Heuristic SHAP	17  
4.7 So sánh đặc trưng và Thiết kế hai mô hình đề xuất	18  
CHƯƠNG 5. PHÂN TÍCH DỮ LIỆU VÀ THỰC NGHIỆM	19  
5.1 Thiết lập Thực nghiệm	19  
5.2 Kết quả Đánh giá Tổng thể	20  
5.3 So sánh đối chiếu hiệu năng và Latency giữa hai mô hình	21  
5.4 Hiệu năng trên tập kiểm thử nhiễu (Noisy Benchmark)	22  
5.5 Phân tích Cluster Match	23  
5.6 Kết quả Ablation Study	24  
5.7 Thảo luận về sự thích ứng của mô hình	25  
5.8 Phân tích Lỗi (Error Analysis)	26  
CHƯƠNG 6. KẾT LUẬN VÀ KIẾN NGHỊ	27  
6.1 Kết luận	27  
6.2 Hạn chế của đề tài	28  
6.3 Hướng phát triển và kiến nghị nghiên cứu tiếp theo	28  
TÀI LIỆU THAM KHẢO	29  
PHỤ LỤC A — CẤU TRÚC DỮ LIỆU SAPO VÀ THỰC THỂ TIẾNG VIỆT	30

<!-- PAGE_BREAK -->

# DANH MỤC HÌNH VẼ

Hình 0.1 Các sinh viên đang làm việc ở phòng lab	5  
HÌNH 0.2 Giới thiệu chương trình thạc sĩ	8  
Hình 3.1 Kiến trúc tổng thể hệ thống đề xuất TIGER + Price Rerank	12  
Hình 4.1 So sánh tất cả mô hình trên 5 thước đo (N=12.991)	21  
Hình 4.2 Đường cong Recall@K cho các mô hình chính	22  
Hình 4.3 Trade-off Accuracy vs. Latency	23  
Hình 4.4 Ablation Study: Đóng góp từng thành phần	25  
Hình 4.5 Radar Chart: BM25+ Enhanced vs. Proposed Hybrid	26  
Hình A.1 Sapo Ablation: 5 phương pháp, Leave-One-Out N=150	33  
Hình A.2 Cross-Domain: Winemag (không có user data) vs Sapo (có lịch sử mua)	34  
Hình A.3 Tác động của dữ liệu lịch sử mua tới chất lượng gợi ý	35

<!-- PAGE_BREAK -->

# DANH MỤC BẢNG BIỂU

Bảng 0.1 Số liệu	11  
Bảng 3.1 Cấu trúc phân cấp cụm ngữ nghĩa rượu vang	10  
Bảng 3.2 Cấu hình fine-tuning Llama-3-8B với LoRA	10  
Bảng 4.1 Phân chia tập dữ liệu Winemag-130k	21  
Bảng 4.2 So sánh hiệu năng gợi ý (N=12.991)	22  
Bảng 4.3 Kết quả đánh giá Cluster Match	23  
Bảng 4.4 Kết quả Ablation Study	25  
Bảng A.1 So sánh hai bộ dữ liệu Winemag và Sapo	32  
Bảng A.2 Các phương pháp so sánh trên dữ liệu Sapo	32  
Bảng A.3 Kết quả Sapo Ablation Study (N=150, Leave-One-Out)	33  
Bảng A.4 Tổng kết hiệu năng các kịch bản gợi ý	35

<!-- PAGE_BREAK -->

# DANH MỤC CÁC CHỮ VIẾT TẮT

| Viết tắt | Từ đầy đủ tiếng Anh | Nghĩa tiếng Việt |
|:---|:---|:---|
| **API** | Application Programming Interface | Giao diện Lập trình Ứng dụng |
| **BM25** | Best Matching 25 | Thuật toán truy xuất Okapi BM25 |
| **CBF** | Content-Based Filtering | Lọc dựa trên nội dung |
| **CF** | Collaborative Filtering | Lọc cộng tác |
| **DSI** | Differentiable Search Index | Chỉ mục tìm kiếm vi phân |
| **GNN** | Graph Neural Network | Mạng nơ-ron đồ thị |
| **LLM** | Large Language Model | Mô hình ngôn ngữ lớn |
| **LoRA** | Low-Rank Adaptation | Tích hợp ma trận hạng thấp |
| **MRR** | Mean Reciprocal Rank | Điểm xếp hạng nghịch đảo trung bình |
| **NCI** | Neural Corpus Indexer | Chỉ mục tài liệu bằng mạng nơ-ron |
| **NDCG** | Normalized Discounted Cumulative Gain | Chỉ số đo chất lượng xếp hạng |
| **POS** | Point of Sale | Điểm bán hàng |
| **QLoRA** | Quantized Low-Rank Adaptation | Tinh chỉnh thích ứng hạng thấp lượng hóa |
| **RAG** | Retrieval-Augmented Generation | Tạo sinh tăng cường truy xuất |
| **SVD** | Singular Value Decomposition | Phân tách giá trị kỳ dị |
| **TF-IDF** | Term Frequency-Inverse Document Frequency | Tần suất từ - nghịch đảo tần suất văn bản |
| **TIGER** | Tokenized Item Generative Retrieval | Gợi ý tạo sinh sản phẩm mã hóa |
| **VRAM** | Video Random Access Memory | Bộ nhớ truy cập ngẫu nhiên video |

<!-- PAGE_BREAK -->

# CHƯƠNG 1. MỞ ĐẦU

## 1.1 Lý do chọn đề tài

Thị trường rượu vang toàn cầu ngày càng phát triển mạnh mẽ với hàng vạn nhà sản xuất ở khắp các quốc gia như Pháp, Ý, Mỹ, Chile hay Úc, cung cấp cho người tiêu dùng hàng trăm nghìn sản phẩm đa dạng về chủng loại, hương vị và phân khúc giá. Sự đa dạng này tạo ra một bài toán khó đối với người tiêu dùng phổ thông khi họ muốn lựa chọn một chai rượu vang phù hợp với sở thích cá nhân, món ăn đi kèm hay một dịp lễ cụ thể. Để đáp ứng nhu cầu này, việc phát triển các hệ gợi ý (Recommender Systems) thông minh trong thương mại điện tử rượu vang là vô cùng cần thiết.

Tuy nhiên, các hệ thống gợi ý rượu vang truyền thống gặp nhiều khó khăn. Lọc cộng tác (Collaborative Filtering - CF) đòi hỏi lượng dữ liệu lịch sử tương tác cực lớn giữa người dùng và sản phẩm. Điều này dẫn đến sự bất lực hoàn toàn trước sản phẩm mới hoặc người dùng mới (bài toán khởi động lạnh - Cold-Start). Lọc dựa trên nội dung (Content-Based Filtering - CBF) giải quyết được phần nào bài toán cold-start cho sản phẩm nhưng lại phụ thuộc nặng nề vào các thuộc tính thô được gán nhãn thủ công và không thể tự động khai phá các liên kết ngữ nghĩa ẩn giấu trong các mô tả dài phức tạp.

Sự ra đời của Mô hình Ngôn ngữ Lớn (LLM) và kỹ thuật Truy xuất Tạo sinh (Generative Retrieval) đã mở ra một hướng tiếp cận đột phá. Thay vì tìm kiếm sản phẩm trong không gian vector cứng nhắc hoặc sử dụng chỉ mục đảo ngược truyền thống, mô hình ngôn ngữ lớn có thể học cách "nhớ" toàn bộ danh mục sản phẩm trực tiếp vào trọng số của nó thông qua quá trình fine-tuning Seq2Seq và sinh trực tiếp mã định danh (ID) của sản phẩm tương thích từ truy vấn ngôn ngữ tự nhiên tự do của người dùng. Luận văn này tập trung nghiên cứu, hiện thực hóa và đánh giá đối chiếu các phương pháp này trên bộ dữ liệu rượu vang lớn.

<!-- PAGE_BREAK -->

## 1.2 Mục tiêu thực hiện đề tài

Đề tài nghiên cứu hướng tới các mục tiêu cụ thể sau:

Thứ nhất, xây dựng thành công hệ thống gợi ý rượu vang thông minh có khả năng hiểu truy vấn ngôn ngữ tự nhiên mềm dẻo của người dùng, giải quyết triệt để bài toán khởi động lạnh đối với các sản phẩm rượu vang mới.

Thứ hai, thiết kế không gian mã định danh ngữ nghĩa phân cấp (Hierarchical Semantic IDs) cho toàn bộ danh mục 130.000 chai rượu vang từ bộ dữ liệu Wine Reviews. Không gian mã định danh này phải phản ánh chính xác cấu trúc tương đồng về hương vị, giống nho, vùng trồng và nhà sản xuất để mô hình ngôn ngữ lớn có thể học một cách hiệu quả.

Thứ ba, tinh chỉnh mô hình ngôn ngữ lớn Meta Llama-3-8B bằng kỹ thuật thích ứng hạng thấp LoRA dưới dạng lượng hóa 4-bit, giúp tối ưu hóa tài nguyên tính toán nhưng vẫn giữ nguyên khả năng suy luận ngữ nghĩa tinh tế của mô hình gốc.

Thứ tư, đề xuất và hiện thực hóa hai kiến trúc gợi ý đối chiếu: (1) Mô hình 1 kết hợp giữa TIGER (Tokenized Item Generative Retrieval) và thuật toán xếp hạng lại theo giá Price Rerank; (2) Mô hình 2 phân tách rõ ràng giữa khâu lọc ràng buộc cấu trúc (LLM Parser + Structured Filter) và khâu tạo lời lý giải Sommelier Rationale.

Thứ năm, xây dựng bộ khung giải thích hậu nghiệm sử dụng mô hình proxy heuristic kết hợp với phương pháp tính toán giá trị đóng góp Shapley (SHAP), mang lại sự minh bạch khoa học cho kết quả gợi ý.

<!-- PAGE_BREAK -->

## 1.3 Đối tượng và phạm vi nghiên cứu

Đối tượng nghiên cứu của luận văn bao gồm:

- Không gian ngữ nghĩa biểu diễn sản phẩm rượu vang và các kỹ thuật trích chọn đặc trưng văn bản tự do như TF-IDF, phân tách giá trị kỳ dị TruncatedSVD, và thuật toán phân cụm phân cấp Hierarchical K-Means.

- Các kiến trúc học sâu hỗ trợ cơ chế truy xuất tạo sinh (Generative Retrieval), cụ thể là mô hình chỉ mục tìm kiếm vi phân DSI (Differentiable Search Index), mô hình chỉ mục tài liệu mạng nơ-ron NCI (Neural Corpus Indexer), và mô hình gợi ý sản phẩm TIGER của Google Research.

- Các kỹ thuật tối ưu hóa và tinh chỉnh mô hình ngôn ngữ lớn trong điều kiện tài nguyên giới hạn (LoRA, QLoRA, NF4 quantization, Constrained Decoding).

- Các phương pháp đo lường, đánh giá hiệu năng hệ thống gợi ý và truy xuất thông tin (Recall@K, NDCG@K, MRR).

Phạm vi nghiên cứu của đề tài giới hạn trong:

- Bộ dữ liệu Wine Reviews chứa 130.000 đánh giá rượu vang bằng tiếng Anh từ tạp chí Wine Enthusiast làm cơ sở dữ liệu huấn luyện chính cho bài toán Cold-Start.

- Bộ dữ liệu đơn hàng và khách hàng thực tế từ phần mềm quản lý bán hàng Sapo của một doanh nghiệp Việt Nam làm ablation study cho bài toán Warm-Start.

- Phần cứng huấn luyện giới hạn trên cấu hình GPU NVIDIA RTX 3060 (12GB VRAM) để chứng minh tính khả thi của phương pháp trên thiết bị phần cứng thông dụng.

<!-- PAGE_BREAK -->

## 1.4 Phương pháp nghiên cứu

Luận văn áp dụng các phương pháp nghiên cứu khoa học sau:

- Phương pháp lý thuyết: Nghiên cứu các tài liệu học thuật chính thống về hệ gợi ý, mô hình ngôn ngữ lớn, cơ chế tự chú ý (Self-Attention) và lý thuyết thông tin. Phân tích các mô hình baseline nổi tiếng như DSI của Google Research và LoRA của Microsoft.

- Phương pháp thực nghiệm: Thiết kế và chạy các kịch bản huấn luyện tinh chỉnh mô hình trên tập dữ liệu chuẩn. Xây dựng môi trường đánh giá độc lập sử dụng 12.991 mẫu kiểm thử để đo lường chính xác các chỉ số Recall@K, NDCG@K, và MRR.

- Phương pháp so sánh đối chiếu: Thực hiện ablation study để làm rõ vai trò đóng góp của từng thành phần trong hệ thống gợi ý. Đánh giá cross-domain giữa tập dữ liệu Winemag (tiếng Anh, cold-start) và Sapo (tiếng Việt, warm-start) để rút ra các kết luận mang tính nguyên lý thiết kế.

## 1.5 Ý nghĩa thực tiễn của đề tài

Đề tài đóng góp một giải pháp thực tiễn có giá trị cao cho ngành thương mại điện tử rượu vang nói riêng và các sản phẩm cao cấp nói chung. Giải pháp giúp doanh nghiệp xây dựng bộ máy gợi ý cá nhân hóa có khả năng tư vấn giống như một chuyên gia rượu vang (Sommelier) thực thụ, tăng tỷ lệ chuyển đổi đơn hàng và nâng cao lòng tin của khách hàng thông qua các lời lý giải minh bạch.

<!-- PAGE_BREAK -->

## 1.6 Môi trường thực hiện nghiên cứu

Toàn bộ quá trình nghiên cứu lý thuyết, xử lý dữ liệu lớn và chạy thử nghiệm các thuật toán được thực hiện tại phòng lab chuyên dụng của Khoa Công nghệ Thông tin, Trường Đại học Tôn Đức Thắng. Phòng lab cung cấp môi trường làm việc học thuật chuyên nghiệp với hệ thống máy tính hiệu năng cao, server lưu trữ lớn và mạng kết nối băng thông rộng ổn định, hỗ trợ tối đa cho học viên và các nghiên cứu sinh trong việc phát triển mô hình.

![Hình 0.1 Các sinh viên đang làm việc ở phòng lab](thesis/lab_students.png)  
*Hình 0.1 — Các sinh viên đang làm việc ở phòng lab máy tính khoa CNTT*  

Môi trường phòng lab hiện đại được trang bị đầy đủ các công cụ phần mềm phục vụ cho học máy và dữ liệu lớn, giúp học viên thực thi các thử nghiệm huấn luyện mô hình sâu (Deep Learning) lớn một cách nhanh chóng và chính xác.

<!-- PAGE_BREAK -->

# CHƯƠNG 2. TỔNG QUAN

## 2.1 Giới thiệu về Hệ gợi ý

Hệ gợi ý (Recommender Systems) là một nhánh nghiên cứu quan trọng trong lĩnh vực Trí tuệ Nhân tạo và Khai phá Dữ liệu, có nhiệm vụ dự đoán mức độ quan tâm của người dùng đối với các sản phẩm. Về mặt toán học, bài toán gợi ý có thể được biểu diễn như việc xác định một hàm tiện ích $u: U 	imes I \to R$, trong đó $U$ là không gian người dùng, $I$ là không gian sản phẩm và $R$ là tập số thực biểu thị điểm số đánh giá.

Mục tiêu của hệ thống là tìm ra sản phẩm $i^* \in I$ tối đa hóa hàm tiện ích cho người dùng $u \in U$:  
$$i^* = \arg\max_{i \in I} u(u, i)$$  

Trong thực tế thương mại điện tử, không gian $U$ và $I$ cực kỳ lớn và ma trận tương tác người dùng - sản phẩm thường rất thưa (sparsity rate thường lớn hơn 99%). Điều này đặt ra yêu cầu hệ gợi ý phải có khả năng dự đoán các tương tác ẩn dựa trên các đặc trưng gián tiếp của người dùng và sản phẩm.

## 2.2 Các phương pháp gợi ý truyền thống

Phương pháp Lọc cộng tác (Collaborative Filtering - CF) dựa trên giả thuyết rằng các người dùng có hành vi tương đồng trong quá khứ sẽ có sở thích tương tự trong tương lai. CF chia làm hai loại: dựa trên bộ nhớ (Memory-based CF) như User-based/Item-based dùng độ tương đồng Cosine để tính toán láng giềng, và dựa trên mô hình (Model-based CF) như Matrix Factorization (SVD, iALS) phân tích ma trận tương tác thành các nhân tố ẩn (latent factors). Nhược điểm chí mạng của CF là khởi động lạnh (Cold-Start): không thể đưa ra gợi ý khi thiếu dữ liệu lịch sử tương tác.

<!-- PAGE_BREAK -->

Lọc dựa trên Nội dung (Content-Based Filtering - CBF) giải quyết bài toán cold-start cho sản phẩm bằng cách đo độ tương đồng giữa hồ sơ đặc trưng của sản phẩm (ví dụ: giống nho, quốc gia sản xuất) với sở thích của người dùng. CBF thường sử dụng kỹ thuật biểu diễn TF-IDF trên các văn bản mô tả để tính toán độ tương đồng cosine. Tuy nhiên, CBF gặp hạn chế khi đặc trưng của sản phẩm nghèo nàn và không thể tự động khai phá các liên kết ngữ nghĩa ẩn giấu trong các mô tả dài phức tạp.

## 2.3 Các phương pháp gợi ý hiện đại

Các mô hình hiện đại hướng tới việc kết hợp CF và CBF để khắc phục nhược điểm của cả hai. Sự ra đời của Mạng nơ-ron đồ thị (Graph Neural Networks - GNNs) như LightGCN, NGCF cho phép biểu diễn tương tác dưới dạng đồ thị lưỡng phân người dùng-sản phẩm, học các embedding thông qua cơ chế lan truyền thông điệp (message passing) trên các nút láng giềng.

Mặt khác, các mô hình dựa trên Transformer (như BERT4Rec, SASRec) khai thác lịch sử tương tác dưới dạng chuỗi thời gian, áp dụng cơ chế tự chú ý (Self-Attention) để nắm bắt sở thích ngắn hạn và dài hạn của người dùng. Dù đạt hiệu năng cao, các phương pháp này vẫn đòi hỏi dữ liệu huấn luyện lớn và là các mô hình hộp đen (black-box), thiếu hoàn toàn khả năng giải thích lý do gợi ý cho người dùng cuối.

<!-- PAGE_BREAK -->

## 2.4 Bối cảnh đào tạo và Nghiên cứu tại Trường

Đề tài nghiên cứu này được thực hiện trong khuôn khổ chương trình đào tạo Thạc sĩ ngành Khoa học Máy tính tại Trường Đại học Tôn Đức Thắng. Chương trình đào tạo thạc sĩ của trường hướng tới việc trang bị cho học viên các kiến thức khoa học tiên tiến và kỹ năng thực hành nghiên cứu chuyên sâu, đặc biệt trong các lĩnh vực Trí tuệ Nhân tạo, Học máy và Xử lý Ngôn ngữ Tự nhiên. Sự hỗ trợ từ chương trình đào tạo là nền tảng định hướng học thuật vững chắc cho việc phát triển các kiến thức trong luận văn này.

![HÌNH 0.2 Giới thiệu chương trình thạc sĩ](thesis/master_intro.png)  
*Hình 0.2 — Giới thiệu chương trình thạc sĩ Khoa học Máy tính*  

Các hội thảo khoa học và chuyên đề thường niên tại khoa tạo điều kiện cho học viên tiếp cận với các công nghệ AI tiên tiến, tạo nguồn cảm hứng để phát triển các giải pháp mang tính ứng dụng thực tiễn cao.

<!-- PAGE_BREAK -->

## 2.5 Khảo sát các giải pháp gợi ý rượu vang thực tế

Trong khuôn khổ tổng quan nghiên cứu, chúng tôi tiến hành khảo sát các ứng dụng di động và hệ thống thương mại điện tử rượu vang lớn trên thế giới như Vivino và Wine.com.

Vivino sử dụng một cơ chế lọc dựa trên điểm số đánh giá trung bình từ hàng triệu người dùng cộng đồng kết hợp với việc gán nhãn hương vị bằng từ khóa tĩnh (ví dụ: "bold", "acidic", "sweet"). Hệ thống này hoạt động rất hiệu quả khi có lượng tương tác khổng lồ nhưng gặp khó khăn nghiêm trọng khi giới thiệu các nhà sản xuất vang thủ công nhỏ (artisanal wineries) chưa có nhiều lượt đánh giá.

Wine.com sử dụng mô hình lọc theo nội dung kết hợp sự tư vấn thủ công của các Sommelier. Tuy nhiên, cách tiếp cận này khó mở rộng quy mô (scalability) và không thể cung cấp lời lý giải cá nhân hóa theo thời gian thực cho từng truy vấn cụ thể của khách hàng. Điều này làm nổi bật khoảng trống nghiên cứu mà đề tài luận văn hướng tới: phát triển một Sommelier ảo tự động hóa hoàn toàn bằng trí tuệ nhân tạo, có thể hoạt động ở quy mô lớn với chi phí vận hành thấp.

<!-- PAGE_BREAK -->

# CHƯƠNG 3. CƠ SỞ LÝ THUYẾT

## 3.1 Truy xuất Tạo sinh (Generative Retrieval)

Truy xuất Tạo sinh (Generative Retrieval) là một hướng tiếp cận đột phá trong lĩnh vực Truy xuất Thông tin và Hệ gợi ý. Trong các hệ thống truyền thống, quá trình truy xuất tuân theo quy trình hai bước: (1) Lọc ứng viên thô sử dụng chỉ mục đảo ngược (inverted index như BM25) hoặc tìm kiếm vector (vector search); (2) Xếp hạng lại các ứng viên bằng một mô hình học máy phức tạp. Quy trình này đòi hỏi duy trì một chỉ mục vật lý cồng kềnh ngoài bộ nhớ và gặp trễ lớn khi không gian sản phẩm mở rộng.

Generative Retrieval thay thế toàn bộ quy trình trên bằng một mô hình Sequence-to-Sequence (Seq2Seq) duy nhất. Mô hình nhận truy vấn tự nhiên $q$ và trực tiếp sinh ra mã định danh $d$ của sản phẩm đích dưới dạng một chuỗi các token:  
$$P(d|q) = \prod_{j=1}^M P(t_j | t_{<j}, q)$$  

Trong đó $d = [t_1, t_2, ..., t_M]$ là mã định danh của sản phẩm. Toàn bộ thông tin về danh mục sản phẩm và mối quan hệ ngữ nghĩa giữa chúng được mô hình hóa và lưu trữ trực tiếp trong các tham số (weights) của mạng nơ-ron. Mô hình tiên phong cho hướng tiếp cận này là Differentiable Search Index (DSI) do Tay và các cộng sự (Google Research, 2022) đề xuất, chứng minh rằng mô hình Seq2Seq có thể ghi nhớ hiệu quả hàng triệu tài liệu.

<!-- PAGE_BREAK -->

## 3.2 Mô hình TIGER

Mô hình TIGER (Tokenized Item Generative Retrieval) do Rajput và các cộng sự (Google Research, NeurIPS 2023) đề xuất là cột mốc quan trọng ứng dụng Generative Retrieval vào hệ gợi ý. TIGER giới thiệu khái niệm mã định danh ngữ nghĩa phân cấp (Hierarchical Semantic IDs) để khắc phục nhược điểm của các mã định danh số nguyên ngẫu nhiên trong DSI vốn thiếu ngữ nghĩa sản phẩm.

TIGER sử dụng bộ mã hóa tự động biến phân lượng hóa vector dư (Residual Quantization VAE - RQ-VAE) để nén các vector biểu diễn sản phẩm thành một chuỗi các mã codebook ngắn có tính phân cấp. Nhờ đó, các sản phẩm có tính chất ngữ nghĩa tương đồng sẽ chia sẻ các tiền tố mã định danh giống nhau. Mô hình Seq2Seq (như T5) được huấn luyện để sinh ra mã định danh này từ lịch sử hành vi của người dùng. TIGER đạt kết quả vượt trội trên các tập dữ liệu thương mại điện tử lớn của Amazon và Bili.

## 3.3 Mô hình Ngôn ngữ Lớn và Tinh chỉnh LoRA

Mô hình Ngôn ngữ Lớn (LLM) như Llama-3-8B dựa trên kiến trúc Transformer chỉ có bộ giải mã (decoder-only), được huấn luyện trên hàng nghìn tỷ token văn bản. Để áp dụng LLM vào Generative Retrieval với tài nguyên giới hạn, kỹ thuật LoRA (Low-Rank Adaptation) được áp dụng. LoRA giả định quá trình cập nhật trọng số trong fine-tuning có một "hạng bản chất" (intrinsic rank) thấp. Với trọng số ban đầu $W_0 \in R^{d \times k}$, LoRA thêm một lượng cập nhật $\Delta W$ được phân tích thành tích của hai ma trận hạng thấp $B \in R^{d \times r}$ và $A \in R^{r \times k}$ với $r \ll \min(d, k)$:  
$$W = W_0 + \frac{\alpha}{r} B A$$

<!-- PAGE_BREAK -->

## 3.4 Phân tích Số liệu Dữ liệu Nghiên cứu

Dưới đây là bảng thống kê số liệu mô tả sơ bộ các đặc trưng chính của bộ dữ liệu Wine Reviews (Winemag-130k) và bộ dữ liệu Sapo thực tế được sử dụng trong luận văn. Các dữ liệu này phản ánh cấu trúc quy mô và sự phân bố giá trị, đóng vai trò nền tảng cho việc thiết lập thực nghiệm.

Bảng 0.1 Số liệu  
| sTT | a | b | c | d |
|:---:|:---|:---|:---|:---|
| 1 | Bộ dữ liệu chính (Winemag) | 129,971 chai rượu | 16,847 giống nho | Giá trung bình $35.0 |
| 2 | Bộ dữ liệu thực tế (Sapo) | 305 sản phẩm | 733 giao dịch | Giá trung vị 795,000 VND |
| 3 | Tập huấn luyện Winemag | 103,925 mẫu | 80% tỷ lệ | Huấn luyện tinh chỉnh LoRA |
| 4 | Tập kiểm thử Winemag | 12,991 mẫu | 10% tỷ lệ | Đánh giá Recall@K, NDCG@K |
| 5 | Tập kiểm thử nhiễu (Noisy) | 100 câu truy vấn | 5 cấu trúc lỗi | Đánh giá độ bền vững ngữ nghĩa |

Dữ liệu trên Bảng 0.1 cho thấy sự chênh lệch quy mô lớn giữa bộ dữ liệu Winemag (cold-start hoàn toàn trên 130k sản phẩm) và bộ dữ liệu Sapo thực tế (warm-start trên catalog nhỏ), làm nổi bật ý nghĩa của việc kiểm thử chéo giữa hai môi trường nghiên cứu.

<!-- PAGE_BREAK -->

## 3.5 Các nghiên cứu liên quan về trích xuất thông tin

Sự phát triển của xử lý ngôn ngữ tự nhiên (NLP) đã làm thay đổi hoàn toàn cách chúng ta tương tác với cơ sở dữ liệu. Trước kỷ nguyên của LLM, các phương pháp trích xuất thực thể tên riêng (Named Entity Recognition - NER) và tìm kiếm ngữ nghĩa chủ yếu dựa trên các mô hình như BERT hay RoBERTa kết hợp với các bộ phân loại tuyến tính ở đầu ra.

Mặc dù các mô hình này đạt độ chính xác cao đối với các thực thể tường minh, chúng hoàn toàn thất bại khi gặp các thực thể bị viết sai chính tả nặng hoặc các mô tả mang tính ẩn dụ cao. Sự xuất hiện của các mô hình sinh (Generative Models) như Llama-3 mang lại khả năng xử lý ngữ cảnh cực kỳ linh hoạt. Việc tinh chỉnh mô hình ngôn ngữ lớn để trích xuất JSON hoặc sinh trực tiếp mã định danh là sự kế thừa và phát triển từ các nghiên cứu NER truyền thống, nâng tầm khả năng hiểu ý định người dùng lên một cấp độ mới mềm dẻo hơn.

<!-- PAGE_BREAK -->

## 3.6 Khái quát toán học về mạng tự chú ý (Self-Attention)

Cơ chế tự chú ý (Self-Attention) là thành phần cốt lõi của kiến trúc Transformer được sử dụng trong mô hình Llama-3. Với một ma trận đầu vào $X \in R^{N \times d}$, cơ chế tự chú ý tính toán ma trận Query ($Q$), Key ($K$) và Value ($V$) thông qua các ma trận trọng số chiếu tương ứng $W_Q, W_K, W_V \in R^{d \times d_k}$:
$$Q = X W_Q, \quad K = X W_K, \quad V = X W_V$$

Đầu ra của lớp tự chú ý được tính bằng cách lấy tích trọng số của $V$ với ma trận phân phối chú ý được chuẩn hóa qua hàm Softmax:
$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{Q K^T}{\sqrt{d_k}}\right) V$$

Trong quá trình tinh chỉnh LoRA của chúng tôi, các ma trận trọng số chiếu này chính là đối tượng được tích hợp các ma trận hạng thấp để cập nhật thông tin ngữ nghĩa, giúp mô hình ngôn ngữ lớn học cách ánh xạ từ truy vấn sang Semantic ID.

<!-- PAGE_BREAK -->

# CHƯƠNG 4. PHƯƠNG PHÁP NGHIÊN CỨU

## 4.1 Kiến trúc Hệ thống Tổng thể

Hệ thống gợi ý rượu vang đề xuất tích hợp cả hai mô hình đối chiếu và được tổ chức thành một quy trình xử lý khép kín từ khâu nhận truy vấn tự nhiên đến khâu xuất kết quả lý giải Sommelier Rationale.

![Hình 3.1 Kiến trúc tổng thể hệ thống đề xuất TIGER + Price Rerank](thesis/proposed_architecture.png)  
*Hình 3.1 — Sơ đồ kiến trúc tổng thể hai mô hình gợi ý đề xuất*

Kiến trúc trong Hình 3.1 mô tả rõ ràng luồng đi của dữ liệu. Module 1 thực hiện vector hóa và phân cụm phân cấp để gán Semantic ID cho từng chai rượu vang. Module 2 tinh chỉnh mô hình Llama-3-8B với kỹ thuật LoRA để học cách ánh xạ từ văn bản truy vấn sang Semantic ID. Module 3 triển khai cơ chế kết hợp Price Rerank để đưa ra gợi ý cuối cùng cho Mô hình 1, song song với luồng xử lý của Mô hình 2 (LLM Parser trích xuất JSON → Lọc cấu trúc → LLM Sommelier viết lời giải thích).

<!-- PAGE_BREAK -->

## 4.2 Xây dựng Hierarchical Semantic IDs cho rượu vang

Để tạo ra các mã định danh có cấu trúc ngữ nghĩa cho 130.000 chai rượu vang, chúng tôi thiết kế một pipeline phân cụm phân cấp 3 tầng dựa trên các đặc trưng hương vị tự nhiên. Quy trình gồm 3 bước:

Bước 1 - Trích xuất đặc trưng: Kết hợp các trường văn bản bao gồm mô tả hương vị (`description`), giống nho (`variety`), tỉnh bang (`province`) và quốc gia (`country`) thành một chuỗi duy nhất cho mỗi chai rượu $i$. Áp dụng mô hình TF-IDF với 50.000 từ khóa để chuyển văn bản thành vector thưa $X_{tfidf} \in R^{130000 \times 50000}$.

Bước 2 - Giảm chiều dữ liệu: Để loại bỏ nhiễu và tối ưu hóa tính toán, chúng tôi sử dụng Truncated SVD để chiếu không gian vector thưa về 128 chiều biểu diễn dày đặc $X_{svd} \in R^{130000 \times 128}$.

Bước 3 - Phân cụm phân cấp K-Means: Chạy thuật toán K-Means phân cấp với branching factor $K=16$ trên không gian 128 chiều:

- Tầng 1 ($C_1$): Chia toàn bộ catalog thành 16 cụm lớn đại diện cho các phong cách rượu vang và vùng trồng chính.
- Tầng 2 ($C_2$): Với mỗi cụm lớn trong 16 cụm, tiếp tục chia thành 16 cụm trung gian (tổng cộng 256 cụm).
- Tầng 3 ($C_3$): Với mỗi cụm trung gian, chia tiếp thành 16 cụm chi tiết (tổng cộng 4.096 cụm hương vị chi tiết).

Mỗi chai rượu vang nhận một mã định danh ngữ nghĩa dạng: `[C1-C2-C3-ITEM_IDX]`, trong đó $C_1, C_2, C_3 \in [00, 15]$ và $ITEM\_IDX$ là số thứ tự duy nhất của chai rượu trong cụm chi tiết $C_3$.

<!-- PAGE_BREAK -->

## 4.3 Tinh chỉnh LLM Llama-3-8B với LoRA

Huấn luyện mô hình Sequence-to-Sequence để học ánh xạ từ câu lệnh tự nhiên sang mã định danh ngữ nghĩa phân cấp. Định dạng dữ liệu huấn luyện được chuẩn hóa dưới dạng cặp Instruction-Response:

- **Instruction**: *"Given the following wine review, recommend the most appropriate wine. Wine: {variety} from {country} - {description} Price: ${price}"*
- **Response**: *"[C1-C2-C3-ITEM_IDX]"*

Cấu hình huấn luyện sử dụng QLoRA để lượng hóa mô hình gốc Llama-3-8B về dạng 4-bit NormalFloat (NF4) nhằm giảm bộ nhớ VRAM xuống dưới 10GB. Các tham số LoRA được thiết lập với hạng $r=16$, hệ số scaling $\alpha=32$, và áp dụng vào tất cả các lớp attention chiếu xạ (`q_proj`, `v_proj`, `k_proj`, `o_proj`). Tốc độ học được đặt ở mức $2e-4$, kích thước batch hiệu dụng là 128 (batch size 2 trên mỗi thiết bị kết hợp tích lũy gradient qua 64 bước). Mô hình được huấn luyện trong 3 epoch trên tập train gồm 103.925 mẫu.

Trong quá trình suy luận (Inference), chúng tôi áp dụng cơ chế Constrained Beam Search. Tại mỗi bước sinh token tự hồi quy, mô hình chỉ được phép lựa chọn các token số nguyên hợp lệ tương ứng với cấu trúc cây phân cụm ngữ nghĩa đã xây dựng. Điều này giúp loại bỏ hoàn toàn các mã ID rác, đạt tỷ lệ mã ID hợp lệ là 99,61%.

<!-- PAGE_BREAK -->

## 4.4 Thiết kế Mô hình 1: TIGER + Price Rerank

Mặc dù LLM được tinh chỉnh có khả năng học sinh Semantic ID tương đối tốt, hiệu năng gợi ý mức chai đơn lẻ trong bài toán Cold-Start vẫn rất hạn chế. Điều này xuất phát từ hai lý do: (1) Hậu tố $ITEM\_IDX$ được gán ngẫu nhiên trong cụm khiến LLM không thể học ánh xạ chính xác cho các sản phẩm chưa từng xuất hiện trong tập huấn luyện; (2) Có rất nhiều chai rượu có hương vị tương đồng nằm chung trong một cụm chi tiết $C_3$ (trung bình 170 chai mỗi cụm).

Để giải quyết vấn đề này, chúng tôi đề xuất kiến trúc lai **TIGER + Price Rerank** hoạt động qua 4 bước:

Bước 1: LLM nhận truy vấn tự nhiên và sinh ra mã ID dự đoán `[C1-C2-C3-ITEM_IDX]`.

Bước 2: Hệ thống chỉ trích xuất phần tiền tố cụm ngữ nghĩa `[C1-C2-C3]`, bỏ qua phần hậu tố. Lọc danh mục rượu vang để lấy toàn bộ các chai rượu thuộc cụm này.

Bước 3: Sử dụng biểu thức chính quy (Regex) trích xuất thông tin ngân sách yêu cầu $P_{req}$ từ truy vấn người dùng (ví dụ: "under $40" -> $P_{req} = 40$).

Bước 4: Sắp xếp các chai rượu trong cụm theo khoảng cách giá trị tuyệt đối $|P_i - P_{req}|$ tăng dần. Trả về Top-10 chai có khoảng cách giá nhỏ nhất làm đề xuất cuối cùng.

<!-- PAGE_BREAK -->

## 4.5 Thiết kế Mô hình 2: Parser-Filter-Sommelier

Để làm nổi bật ưu nhược điểm của phương pháp truy xuất tạo sinh (Mô hình 1), chúng tôi đề xuất kiến trúc đối chiếu thứ hai mang tên **Parser-Filter-Sommelier (Model 2)**. Mô hình này tách biệt hoàn toàn quá trình lọc phù hợp vật lý và quá trình tạo lời giải thích ngữ nghĩa qua 3 giai đoạn:

Giai đoạn 1 - Semantic Parsing: Sử dụng LLM như một bộ phân tích cú pháp để trích xuất các ràng buộc cấu trúc từ câu lệnh của người dùng thành định dạng JSON. LLM Parser có khả năng chuẩn hóa các từ viết sai chính tả hoặc từ lóng (ví dụ: "cali" -> giống nho "Pinot Noir", quốc gia "US").

Giai đoạn 2 - Structured Filtering: Bộ lọc trung gian nhận JSON và truy vấn trên danh mục rượu vang theo quy tắc ưu tiên nghiêm ngặt: (1) Khớp giống nho; (2) Khớp quốc gia; (3) Sắp xếp theo khoảng cách giá tuyệt đối; (4) Xếp hạng độ tương đồng hương vị. Kết quả trả ra danh sách Top-10 chai phù hợp nhất.

Giai đoạn 3 - Generative Sommelier Rationale: LLM nhận Top-10 chai ứng viên cùng truy vấn ban đầu. Để tối ưu hóa thời gian phản hồi, LLM chỉ chọn ra 1-2 chai phù hợp nhất để viết đoạn văn ngắn lý giải chi tiết hương vị và sự tương thích món ăn (Sommelier Rationale). 8 chai còn lại trong Top-10 được hiển thị dạng danh sách tĩnh "xem thêm" trên giao diện người dùng.

<!-- PAGE_BREAK -->

## 4.6 Giải thích Hậu nghiệm với Heuristic SHAP

Đối với Mô hình 1, lý do hệ thống chọn một chai rượu cụ thể so với các chai khác trong cùng cụm hương vị cần được làm rõ để tạo lòng tin cho người dùng. Vì việc tính toán giá trị SHAP trực tiếp trên mô hình mạng nơ-ron 8 tỷ tham số trong thời gian thực là không khả thi do chi phí tính toán cực lớn, chúng tôi thiết kế một mô hình xếp hạng heuristic trung gian (Proxy Heuristic Ranker) để tính toán điểm số phù hợp $f(x_i)$ của chai rượu $i$ với truy vấn $q$:  
$$f(x_i) = \sum_{j=1}^5 w_j x_{ij}$$  

Trong đó, vector đặc trưng $x_i = [x_{i1}, x_{i2}, x_{i3}, x_{i4}, x_{i5}]$ đại diện cho 5 yếu tố: trùng khớp giá (Price Match), trùng khớp giống nho (Style Match), kết hợp món ăn (Pairing Match), trùng khớp vùng miền (Region Match) và độ tương đồng ngữ nghĩa cosine (Semantic Similarity). Trọng số mặc định được thiết lập thực nghiệm là $w = [0.30, 0.25, 0.20, 0.15, 0.10]$.

Chúng tôi sử dụng thuật toán `KernelExplainer` của thư viện SHAP để phân bổ điểm số của Proxy Ranker về cho 5 đặc trưng này. Giá trị đóng góp (Shapley Value) $\phi_j$ của đặc trưng thứ $j$ được tính theo công thức:  
$$\phi_j(f, x) = \sum_{S \subseteq F \setminus \{j\}} \frac{|S|!(|F| - |S| - 1)!}{|F|!} \left[ f_x(S \cup \{j\}) - f_x(S) \right]$$  

Kết quả được hiển thị dưới dạng biểu đồ cột biểu thị giá trị đóng góp âm/dương của từng yếu tố đối với chai rượu được đề xuất, tạo sự minh bạch hoàn toàn.

<!-- PAGE_BREAK -->

# CHƯƠNG 5. PHÂN TÍCH DỮ LIỆU VÀ THỰC NGHIỆM

## 5.1 Thiết lập Thực nghiệm

### 5.1.1 Phân chia Dữ liệu

Bộ dữ liệu Wine Reviews (Winemag-130k) được phân chia ngẫu nhiên theo tỷ lệ 80% cho tập huấn luyện (Train: 103.925 mẫu), 10% cho tập kiểm thử chéo (Validation: 12.991 mẫu) và 10% cho tập kiểm thử cuối cùng (Test: 12.991 mẫu). Vì việc phân chia được thực hiện ở cấp độ sản phẩm (item-level), toàn bộ 12.991 chai rượu trong tập test hoàn toàn chưa từng xuất hiện trong tập huấn luyện. Đây là một thiết lập thử nghiệm cực kỳ thử thách mô phỏng chính xác bài toán khởi động lạnh hoàn toàn (Cold-Start).

### 5.1.2 Thiết lập Benchmark truy vấn nhiễu (Noisy Query)

Bên cạnh tập kiểm thử chuẩn, chúng tôi xây dựng một tập benchmark gồm 100 câu truy vấn chứa các lỗi viết sai chính tả cố ý (như "itly", "spnish"), viết tắt hoặc sử dụng từ lóng ("cali", "cab") để đánh giá khả năng chịu lỗi và thích ứng ngữ nghĩa của các mô hình trong điều kiện thực tế.

### 5.1.3 Các mô hình Baseline đối chứng

Hệ thống được so sánh với 6 phương pháp baseline bao gồm: (1) TF-IDF CF (Lọc theo nội dung truyền thống); (2) Okapi BM25 (Tìm kiếm từ khóa thưa); (3) BM25+ Enhanced (BM25 kết hợp mở rộng truy vấn); (4) Struct-Filter BM25 (BM25 kết hợp lọc cấu trúc); (5) Graph Neural Network (GNN-Filter trên đồ thị tương đồng sản phẩm); (6) TIGER Greedy (Mô hình 1 chạy giải mã greedy không xếp hạng lại).

<!-- PAGE_BREAK -->

## 5.2 Kết quả Đánh giá Tổng thể

Bảng dưới đây trình bày kết quả đánh giá đối chiếu hiệu năng gợi ý của hai mô hình đề xuất cùng các baseline trên toàn bộ tập kiểm thử chuẩn gồm 12.991 mẫu:

Bảng 4.2 So sánh hiệu năng gợi ý (N=12.991)  
| Phương pháp | Recall@1 | Recall@5 | Recall@10 | NDCG@10 | MRR | Latency |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| TF-IDF CF | 0.31% | 1.28% | 2.59% | 1.23% | 0.82% | 1.1ms |
| BM25 | 1.07% | 3.53% | 5.54% | 2.95% | 2.17% | 1.5ms |
| BM25+ Enhanced | 7.31% | 13.69% | 14.45% | 11.06% | 9.94% | 1.6ms |
| Struct-Filter BM25 | 7.39% | 14.02% | 14.84% | 11.31% | 10.15% | 1.4ms |
| GNN-Filter | 0.21% | 0.90% | 1.71% | 0.80% | 0.53% | 1.1ms |
| TIGER Greedy | 0.15% | 0.15% | 0.15% | 0.15% | 0.15% | 2,278ms |
| Proposed Hybrid (Model 1) | 2.42% | 6.13% | 7.76% | 4.87% | 3.97% | 15,703ms |
| **Proposed Model 2 (Ours)** | **10.03%** | **27.95%** | **39.42%** | **22.86%** | **17.79%** | **86.6ms** |

Kết quả trên Bảng 4.2 cho thấy Mô hình 2 (Proposed Model 2) đạt hiệu năng vượt trội hoàn toàn so với tất cả các mô hình khác trên tập test chuẩn, với Recall@10 đạt 39,42%, cao gấp 5,1 lần so với Mô hình 1 và gấp 2,6 lần so với baseline tốt nhất Struct-Filter BM25.

![Hình 4.1 So sánh tất cả mô hình trên 5 thước đo (N=12.991)](results/correct_comparison/P1_grouped_bar.png)  
*Hình 4.1 — So sánh hiệu năng gợi ý trên 5 chỉ số chính*

<!-- PAGE_BREAK -->

## 5.3 So sánh đối chiếu hiệu năng và Latency giữa hai mô hình

Sự vượt trội về mặt hiệu năng của Mô hình 2 trên tập test chuẩn xuất phát từ bản chất thiết kế. Tập test chuẩn chứa các truy vấn có cấu trúc ngữ nghĩa rõ ràng và không có lỗi chính tả. Trong điều kiện này, LLM Parser dễ dàng trích xuất chính xác 100% các thực thể (như giống nho "Chardonnay", quốc gia "France"). Bộ lọc cấu trúc sau đó nhanh chóng khoanh vùng danh mục rượu vang và thực hiện xếp hạng thưa.

Ngược lại, Mô hình 1 bị giới hạn hiệu năng ở mức Recall@10 = 7,76%. Do không gian nhãn của cụm hương vị quá rộng (4.096 cụm chi tiết), LLM rất nhạy cảm với sai số trong quá trình sinh tự hồi quy chuỗi mã định danh ngữ nghĩa. Chỉ cần mô hình sinh sai một token (ví dụ sinh ra cụm `12-02-05` thay vì `12-02-06`), toàn bộ quá trình tìm kiếm sẽ bị hướng sang cụm hương vị khác, dẫn đến Recall của truy vấn đó rơi về 0%.

![Hình 4.2 Đường cong Recall@K cho các mô hình chính](results/correct_comparison/P2_recall_curve.png)  
*Hình 4.2 — Biểu đồ so sánh đường cong Recall@K của các mô hình*

Về mặt tốc độ phản hồi (Latency), Mô hình 2 đạt thời gian trễ lý tưởng là 86,6ms trên cấu hình thử nghiệm, hoàn toàn đáp ứng yêu cầu vận hành thời gian thực (<100ms) trong các hệ thống thương mại điện tử thực tế. Mô hình 1 tốn tới 15,7 giây cho mỗi truy vấn do mô hình 8 tỷ tham số phải sinh chuỗi tự hồi quy trên CPU, gây nghẽn nghiêm trọng.

<!-- PAGE_BREAK -->

## 5.4 Hiệu năng trên tập kiểm thử nhiễu (Noisy Benchmark)

Mặc dù có hiệu năng thấp hơn trên tập test chuẩn, Mô hình 1 lại thể hiện ưu điểm vượt trội trên tập kiểm thử chứa truy vấn nhiễu và lỗi chính tả. Dưới đây là kết quả đánh giá so sánh hiệu năng của ba phương pháp chính trên tập Noisy Benchmark (N=100):

- Struct-Filter BM25: Đạt Recall@10 = 4,00% và NDCG@10 = 2,04%. Do bộ lọc cấu trúc thô dựa trên từ khóa khớp cứng bị lỗi khi từ khóa viết sai chính tả (như "itly", "cali"), hệ thống phải fallback quét toàn văn bản trên 130k tài liệu khiến kết quả bị loãng nghiêm trọng.

- Mô hình 2 (Parser-Filter): Đạt Recall@10 = 8,00% và NDCG@10 = 5,22%. Do LLM Parser cũng gặp khó khăn trong việc chuẩn hóa các từ viết sai chính tả nặng sang JSON thực thể chuẩn, dẫn đến bộ lọc cấu trúc phía sau nhận thông tin rỗng hoặc sai lệch.

- Mô hình 1 (TIGER + Price Rerank): Đạt Recall@10 = 43,00% và NDCG@10 = 23,74%. Nhờ LLM được tinh chỉnh có khả năng hiểu ngữ nghĩa mềm dẻo, mô hình dễ dàng ánh xạ các từ viết sai chính tả hoặc từ lóng sang đúng mã cụm hương vị ngữ nghĩa phân cấp tương ứng, thu hẹp không gian tìm kiếm xuống chỉ còn vài chục chai trước khi thực hiện lọc giá.

![Hình 4.3 Trade-off Accuracy vs. Latency](results/correct_comparison/P4_latency_scatter.png)  
*Hình 4.3 — Biểu đồ phân tán Accuracy vs. Latency của các mô hình*

<!-- PAGE_BREAK -->

## 5.5 Phân tích Cluster Match

Để làm rõ khả năng học của LLM đối với không gian ngữ nghĩa phân cấp, chúng tôi tiến hành phân tích chỉ số Cluster Match@1 (tỷ lệ mô hình dự đoán đúng mã cụm hương vị $C_1-C_2-C_3$ của chai rượu mục tiêu) trên toàn bộ 12.991 mẫu kiểm thử. Kết quả được chi tiết trong bảng dưới đây:

Bảng 4.3 Kết quả đánh giá Cluster Match  
| Thước đo | Giá trị tỷ lệ |
|:---|:---:|
| Tỷ lệ sinh ID hợp lệ (Valid ID Rate) | 99.61% |
| Tỷ lệ khớp cụm chi tiết (Cluster Match@1) | 9.67% |
| Tỷ lệ khớp chai chính xác (Exact Match@1) | 0.15% |
| Kích thước cụm chi tiết trung bình | 170.5 chai |
| Giới hạn Recall@10 lý thuyết của cụm | 5.87% |

Các số liệu trên Bảng 4.3 chỉ ra rằng: Llama-3-8B đạt tỷ lệ sinh mã ID đúng định dạng là 99,61%, chứng minh tính hiệu quả của cơ chế Constrained Decoding. Tỷ lệ khớp cụm chi tiết đạt 9,67% — cao gấp 64 lần so với tỷ lệ khớp chai chính xác (0.15%). Điều này xác nhận LLM đã học được cấu trúc phân cấp ngữ nghĩa của rượu vang, định vị đúng nhóm hương vị mục tiêu mặc dù sản phẩm kiểm thử là hoàn toàn mới (Cold-Start).

<!-- PAGE_BREAK -->

## 5.6 Kết quả Ablation Study

Chúng tôi thực hiện ablation study trên tập test Winemag để làm rõ vai trò đóng góp của hai thành phần cốt lõi trong Mô hình 1: bộ lọc cụm ngữ nghĩa (Cluster Filter) sinh từ LLM và bộ xếp hạng lại theo giá (Price Reranker). Kết quả so sánh giữa các biến thể được trình bày như sau:

Bảng 4.4 Kết quả Ablation Study  
| Biến thể | Mô tả thành phần | Recall@1 | Recall@10 | NDCG@10 |
|:---|:---|:---:|:---:|:---:|
| A1 | LLM Greedy (chỉ dùng LLM sinh ID đầy đủ không rerank) | 0.20% | 0.20% | 0.20% |
| A2 | Lọc cụm + Xếp ngẫu nhiên | 0.00% | 0.60% | 0.23% |
| **A3** | **Lọc cụm + Price Rerank (Mô hình 1 đề xuất)** | **1.60%** | **5.60%** | **3.40%** |
| A4 | Lọc cụm + Rerank theo độ tương đồng TF-IDF | 0.00% | 1.00% | 0.40% |
| A5 | Global Price Rerank (chỉ xếp theo giá không lọc cụm) | 0.00% | 2.00% | 0.86% |

Kết quả ablation trên Bảng 4.4 khẳng định sự kết hợp chặt chẽ giữa Cluster Filter và Price Reranker là yếu tố sống còn cho hiệu năng gợi ý của Mô hình 1.

![Hình 4.4 Ablation Study: Đóng góp từng thành phần](results/correct_comparison/P3_ablation.png)  
*Hình 4.4 — Biểu đồ so sánh hiệu năng của các biến thể ablation study*

<!-- PAGE_BREAK -->

## 5.7 Thảo luận về sự thích ứng của mô hình

Sự kết hợp giữa hai thử nghiệm trên tập test chuẩn và tập test nhiễu mang lại một kết luận quan trọng về thiết kế hệ thống gợi ý sử dụng LLM:

Không có một mô hình đơn lẻ nào tối ưu trong mọi tình huống.

- Mô hình 2 (Parser-Filter) hoạt động cực tốt khi người dùng nhập câu lệnh rõ ràng, chuẩn chỉnh và hệ thống cần tốc độ xử lý nhanh, chính xác tuyệt đối về mặt vật lý (giống nho, nước xuất xứ). Đây là kịch bản phổ biến trong các bộ lọc tìm kiếm thương mại điện tử tiêu chuẩn.

- Mô hình 1 (TIGER Generative Retrieval) lại thể hiện vai trò không thể thay thế khi người dùng nhập các truy vấn mơ hồ, tự do, chứa nhiều lỗi chính tả hoặc mô tả cảm tính về phong cách ("rich earthy red for winter"). Khả năng hiểu ngữ nghĩa mềm của LLM tinh chỉnh giúp ánh xạ chính xác các câu lệnh khó này sang nhóm sản phẩm tương thích mà bộ Parser cứng của Mô hình 2 hoàn toàn bó tay.

![Hình 4.5 Radar Chart: BM25+ Enhanced vs. Proposed Hybrid](results/correct_comparison/P5_radar_updated.png)  
*Hình 4.5 — Biểu đồ Radar so sánh các mô hình chính trên nhiều thuộc tính*

<!-- PAGE_BREAK -->

## 5.8 Phân tích Lỗi (Error Analysis)

Chúng tôi phân tích các mẫu gợi ý thất bại của Mô hình 1 và xác định được ba nhóm nguyên nhân chính gây giảm hiệu năng Recall:

1. Sự nhập nhằng của truy vấn (Query Underspecification): Nhiều câu lệnh kiểm thử quá chung chung (ví dụ: "Pinot Noir từ California giá $35") khớp với hàng trăm chai rượu khác nhau trong danh mục. Với kích thước tập đáp án quá lớn, xác suất để chọn đúng chính xác chai rượu mục tiêu của tập test là cực kỳ nhỏ.

2. Phân phối lệch của danh mục (Catalog Popularity Bias): Thuật toán phân cụm K-Means tạo ra một số cụm hương vị rất lớn chứa tới hơn 500 chai rượu vang phổ biến (như Cabernet Sauvignon Mỹ), trong khi các cụm vang hiếm chỉ chứa dưới 10 chai. LLM gặp khó khăn trong việc dự đoán chính xác trên các cụm có mật độ sản phẩm quá dày đặc này.

3. Lỗi chệch hướng mã ID (Semantic Drift): Do cơ chế sinh tự hồi quy, nếu LLM dự đoán sai ký tự đầu tiên ($C_1$), sai số này sẽ lan truyền và khiến các ký tự tiếp theo bị chệch hướng hoàn toàn sang một phân nhánh cây ngữ nghĩa khác.

Các phát hiện này là cơ sở quan trọng để chúng tôi đề xuất các giải pháp cải tiến trong tương lai, chẳng hạn như áp dụng cơ chế Beam Search đa đường để giữ lại top-3 cụm dự đoán thay vì chỉ lấy cụm tốt nhất.

<!-- PAGE_BREAK -->

# CHƯƠNG 6. KẾT LUẬN VÀ KIẾN NGHỊ

## 6.1 Kết luận

Luận văn đã hoàn thành đầy đủ các mục tiêu nghiên cứu đề ra và đạt được các kết quả kỹ thuật và khoa học cụ thể sau:

Thứ nhất, xây dựng và đánh giá đối chiếu thành công hai mô hình gợi ý rượu vang sử dụng mô hình ngôn ngữ lớn Llama-3-8B. Trong đó, Mô hình 2 (Parser-Filter-Sommelier) đạt Recall@10 xuất sắc là 39,42% và latency lý tưởng 86,6ms trên tập test chuẩn. Mô hình 1 (TIGER + Price Rerank) đạt Recall@10 = 7,76% trên tập chuẩn nhưng đạt hiệu năng vượt trội 43,00% trên tập truy vấn chứa nhiều nhiễu và lỗi chính tả.

Thứ hai, thiết kế và lập chỉ mục thành công cây ngữ nghĩa phân cấp 3 tầng (16x16x16) cho 130.000 chai rượu vang thông qua thuật toán K-Means phân cấp trên không gian vector đặc trưng TF-IDF/SVD.

Thứ ba, tinh chỉnh thành công mô hình Llama-3-8B với kỹ thuật LoRA 4-bit, đạt tỷ lệ sinh ID hợp lệ là 99,61% nhờ cơ chế giải mã ràng buộc (Constrained Decoding).

Thứ tư, hiện thực hóa thành công bộ khung giải thích hậu nghiệm sử dụng mô hình proxy ranker kết hợp tính toán giá trị đóng góp Shapley (SHAP), mang lại sự minh bạch khoa học ở cấp độ chai đề xuất đơn lẻ cho người dùng cuối.

<!-- PAGE_BREAK -->

## 6.2 Hạn chế của đề tài

Bên cạnh các kết quả đạt được, đề tài vẫn tồn tại một số hạn chế cần khắc phục trong tương lai:

Một là, thời gian phản hồi của Mô hình 1 vẫn còn rất lớn (trung bình 15,7 giây cho mỗi truy vấn) do việc thực hiện sinh tự hồi quy chuỗi mã định danh ngữ nghĩa trên mô hình 8 tỷ tham số đòi hỏi năng lực tính toán vượt quá cấu hình CPU thông thường.

Hai là, cả hai mô hình vẫn phụ thuộc nhiều vào sự xuất hiện của thông tin giá trong truy vấn của người dùng. Nếu người dùng nhập một câu lệnh hoàn toàn không chứa ngân sách (ví dụ: "tôi muốn một chai vang đỏ đậm đà"), hiệu năng của bộ xếp hạng lại sẽ bị giảm đáng kể do mất đi đặc trưng phân tách mạnh nhất.

Ba là, thiết kế không gian ngữ nghĩa phân cấp và các luật lọc cấu trúc hiện tại vẫn mang tính đặc thù cao cho domain rượu vang, đòi hỏi nhiều công sức điều chỉnh thuộc tính nếu muốn mở rộng sang các lĩnh vực sản phẩm thương mại điện tử khác.

## 6.3 Hướng phát triển và kiến nghị nghiên cứu tiếp theo

Trong thời gian tới, nghiên cứu có thể được tiếp tục phát triển theo các hướng sau:

Ngắn hạn: Tích hợp cơ chế Beam Search đa đường để giữ lại top-3 cụm hương vị dự đoán thay vì chỉ lấy top-1, giúp cải thiện giới hạn Recall của Mô hình 1; tối ưu hóa tốc độ suy luận của LLM bằng cách chuyển đổi sang các định dạng lượng hóa hiệu năng cao như GPTQ hoặc AWQ kết hợp với thư viện phục vụ vLLM để giảm latency xuống dưới 500ms.

Dài hạn: Nghiên cứu tích hợp thêm đặc trưng đa phương thức (hình ảnh nhãn chai rượu) vào không gian vector biểu diễn sản phẩm; thu thập phản hồi tương tác thời gian thực của người dùng để học cá nhân hóa không gian ngữ nghĩa phân cấp.

<!-- PAGE_BREAK -->

# TÀI LIỆU THAM KHẢO

[1] Rajput, S., Mehta, N., Singh, A., Keshavan, R., Vu, T., Heldt, L., Hong, L., Tay, Y., Tran, V. Q., Samost, J., et al. (2023). **TIGER: Recommender Systems with Generative Retrieval**. *Advances in Neural Information Processing Systems (NeurIPS 2023)*.

[2] Tay, Y., Tran, V. Q., Dehghani, M., Ni, J., Bahri, D., Mehta, H., ... & Metzler, D. (2022). **Transformer Memory as a Differentiable Search Index**. *Advances in Neural Information Processing Systems (NeurIPS 2022)*.

[3] Wang, Y., Hou, Y., Wang, H., Mao, Z., Zhang, P., Chen, Q., ... & Dong, L. (2022). **A Neural Corpus Indexer for Document Retrieval**. *Advances in Neural Information Processing Systems (NeurIPS 2022)*.

[4] Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., ... & Chen, W. (2022). **LoRA: Low-Rank Adaptation of Large Language Models**. *International Conference on Learning Representations (ICLR 2022)*.

[5] Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., ... & Polosukhin, I. (2017). **Attention Is All You Need**. *Advances in Neural Information Processing Systems (NeurIPS 2017)*.

[6] Geng, S., Liu, S., Fu, Z., Ge, Y., & Zhang, Y. (2022). **Recommendation as Language Processing (RLP): A Unified Pretrain, Personalized Prompt & Predict Paradigm (P5)**. *ACM Conference on Recommender Systems (RecSys 2022)*.

[7] Hou, Y., Mu, S., Ding, W., Li, J., Zhao, W. X., & Wen, J. R. (2023). **Large Language Models are Zero-Shot Rankers for Recommender Systems**. *arXiv preprint arXiv:2305.08845*.

[8] Robertson, S., & Zaragoza, H. (2009). **The Probabilistic Relevance Framework: BM25 and Beyond**. *Foundations and Trends in Information Retrieval, 3*(4), 333-389.

[9] He, X., Deng, K., Wang, X., Li, Y., Zhang, Y., & Wang, M. (2020). **LightGCN: Simplifying and Powering Graph Convolution Network for Recommendation**. *ACM SIGIR 2020*.

<!-- PAGE_BREAK -->

# PHỤ LỤC A — CẤU TRÚC DỮ LIỆU SAPO VÀ THỰC THỂ TIẾNG VIỆT

## A.1 Cấu trúc cơ sở dữ liệu Sapo

Trong quá trình thực hiện ablation study trên dữ liệu thực tế tại Việt Nam, cơ sở dữ liệu bán hàng Sapo được truy xuất và xử lý từ các bảng dữ liệu gốc:

- Bảng `Product`: Lưu trữ thông tin danh mục sản phẩm gồm mã SKU, tên rượu vang, giống nho, vùng sản xuất, giá bán lẻ và mô tả chi tiết bằng tiếng Việt.
- Bảng `Order`: Lưu trữ lịch sử đơn hàng gồm mã đơn, ngày mua, kênh bán hàng (POS, Facebook, Zalo) và tổng giá trị đơn hàng.
- Bảng `OrderItem`: Lưu trữ chi tiết sản phẩm trong mỗi đơn hàng để phục vụ cho thuật toán gợi ý Collaborative Filtering.

## A.2 Danh sách các giống nho chính được chuẩn hóa tiếng Việt

Trong quá trình xây dựng bộ Parser ý định (Model 2) cho dữ liệu Sapo tiếng Việt, các từ khóa giống nho viết tắt hoặc viết sai của người dùng được ánh xạ và chuẩn hóa như sau:

- "cab", "cabernet", "sauvignon" -> Cabernet Sauvignon
- "mer", "mẹc lô" -> Merlot
- "pinot", "pi nô" -> Pinot Noir
- "char", "sác đô nê" -> Chardonnay
- "sauv blanc", "so vinh nông" -> Sauvignon Blanc
- "syrah", "si ra" -> Syrah/Shiraz

Sự chuẩn hóa này giúp bộ lọc cấu trúc hoạt động chính xác trên catalog Sapo thực tế.