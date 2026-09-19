# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Văn Quốc Việt (2A202602973)
**Nhóm:** Violet
**Ngày:** 2026-09-19

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Mỗi đoạn văn bản được embedding biến thành một vector. Độ tương tự cosine đo góc giữa hai vector: cosine gần 1 nghĩa là hai vector gần như cùng hướng, tức là hai đoạn văn nói về cùng một ý, dù có thể dùng từ ngữ khác nhau. Cosine gần 0 nghĩa là hai đoạn gần như không liên quan về nghĩa.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên cần đạt điểm trung bình từ 3.20 và điểm rèn luyện từ 80 để nhận học bổng loại Giỏi."
- Câu B: "Muốn được học bổng mức Giỏi, bạn phải có GPA tối thiểu 3.2 và rèn luyện 80 điểm trở lên."
- Tại sao tương đồng: Hai câu diễn đạt cùng một điều kiện học bổng (cùng mức, cùng ngưỡng điểm), chỉ khác cách dùng từ ("điểm trung bình" và "GPA", "cần đạt" và "phải có"). Embedding tốt nắm được nghĩa chứ không chỉ khớp từ, nên hai vector gần cùng hướng.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Hạn nộp hồ sơ học bổng là 17h00 ngày 25/08/2026."
- Câu B: "Thư viện mở cửa phục vụ bạn đọc từ thứ Hai đến thứ Sáu."
- Tại sao khác: Hai câu thuộc hai chủ đề khác nhau (thủ tục học bổng và giờ mở cửa thư viện), gần như không chung khái niệm nào. Vì vậy vector của chúng chỉ theo những hướng khác nhau trong không gian embedding.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine chỉ quan tâm tới **hướng** của vector (nội dung nói về gì), không phụ thuộc vào **độ dài** vector. Độ dài vector thường bị ảnh hưởng bởi độ dài văn bản hoặc tần suất từ. Khoảng cách Euclid thì bị độ dài chi phối: một chunk ngắn và một chunk dài cùng nói về "điều kiện học bổng" có thể cách xa nhau theo Euclid dù nghĩa giống nhau. Ngoài ra, khi vector đã được chuẩn hoá về độ dài 1, cosine chỉ là tích vô hướng (dot product), rất nhanh để tính khi xếp hạng hàng nghìn chunk.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> - Mỗi chunk mới bắt đầu cách chunk trước một bước (step) = `chunk_size - overlap` = 500 − 50 = **450** ký tự.
> - Số chunk = ⌈(độ_dài − overlap) / (chunk_size − overlap)⌉ = ⌈(10.000 − 50) / 450⌉ = ⌈9.950 / 450⌉ = ⌈22,11⌉ = **23**.
> - Kiểm tra: các chunk bắt đầu tại vị trí 0, 450, 900, …, 9.900. Chunk thứ 23 bắt đầu ở 9.900 và chỉ còn 100 ký tự cuối.
>
> *Đáp án:* **23 chunks**. Kết quả trùng khi chạy `FixedSizeChunker(chunk_size=500, overlap=50)` trên chuỗi 10.000 ký tự: 23 chunk, chunk cuối dài 100 ký tự.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Số chunk **tăng từ 23 lên 25**: bước giảm còn 500 − 100 = 400, nên ⌈(10.000 − 100) / 400⌉ = ⌈24,75⌉ = 25 (chạy `FixedSizeChunker` cũng ra 25 chunk, chunk cuối dài 400 ký tự). Overlap lớn hơn giúp một câu hoặc một ý bị cắt ở ranh giới chunk vẫn xuất hiện đầy đủ trong chunk kế tiếp. Ví dụ dòng điều kiện "3.20 ≤ ĐTBHB < 3.60 | Từ 80 điểm trở lên" không bị tách đôi, nên retrieval ít bỏ sót thông tin hơn. Đổi lại là có nhiều chunk hơn, nội dung trùng lặp nhiều hơn và tốn thêm chi phí embedding/lưu trữ.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> **Tách câu:** dùng `re.split(r"(?<=[.!?])\s+", text)`. Phần `(?<=[.!?])` là *lookbehind*: nó chỉ kiểm tra ký tự đứng trước chứ không "ăn" ký tự đó, nên cắt tại khoảng trắng *sau* dấu câu mà dấu câu vẫn nằm lại cuối câu. Nếu dùng `[.!?]\s+` thì dấu câu bị nuốt mất.
>
> **Gom chunk:** mỗi `max_sentences_per_chunk` câu liên tiếp nối lại bằng dấu cách, mỗi câu được `strip()` và bỏ câu rỗng. Text rỗng hoặc chỉ có khoảng trắng trả `[]`.
>
> **Edge case biết nhưng chưa xử lý** (đã kiểm chứng bằng cách chạy thử):
> - Chữ viết tắt và số có dấu chấm theo sau là khoảng trắng bị cắt sai. `"Liên hệ TS. Nguyễn Văn A. Điểm tối thiểu là 7. 5 điểm."` bị tách thành `['Liên hệ TS.', 'Nguyễn Văn A.', 'Điểm tối thiểu là 7.', '5 điểm.']`.
> - Bảng Markdown và danh sách không có dấu kết câu nên cả bảng thành một "câu". Chunk có thể dài 1.339 ký tự vì chunker không có giới hạn độ dài.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử separator theo thứ tự `["\n\n", "\n", ". ", " ", ""]`, cắt theo ranh giới lớn trước để giữ nghĩa, và chạy theo **hai chiều**:
> - **Đệ quy xuống:** mảnh nào vẫn dài hơn `chunk_size` thì gọi lại `_split` với danh sách separator còn lại.
> - **Gom lên:** nối các mảnh ngắn liền kề cho tới sát `chunk_size`. Không có bước này thì văn bản nhiều dòng ngắn sẽ vụn thành hàng trăm chunk.
>
> Separator được giữ ở cuối mỗi mảnh (`part + separator`) để không mất dấu chấm hay xuống dòng.
>
> Có 3 trường hợp dừng (base case):
> 1. Text đã ≤ `chunk_size` thì trả `[text]`.
> 2. Hết separator, gồm cả trường hợp người dùng truyền `separators=[]`.
> 3. Separator là `""`.
>
> Trường hợp 2 và 3 cắt cứng theo từng đoạn `chunk_size` ký tự. Nếu separator không có trong text thì chuyển sang separator kế tiếp. `chunk()` gọi `_split(text, self.separators)`, rồi `strip()` và bỏ các mảnh rỗng.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> **Lưu trữ:** chỉ dùng list trong bộ nhớ (`self._store`). Mình bỏ nhánh ChromaDB vì code mẫu gán `_use_chroma = True` trước khi tạo client; máy nào có sẵn `chromadb` thì mọi method sẽ rẽ vào nhánh chưa được viết.
>
> **Hàm phụ `_make_record`:** chuẩn hoá mỗi `Document` thành một record gồm `id`, `content`, `metadata`, `embedding`. Metadata được **copy** (`dict(doc.metadata)`) để người gọi sửa dict bên ngoài không làm thay đổi store, và luôn có `doc_id` (mặc định lấy `doc.id`). `add_documents` không tự chunk: 1 Document = 1 record.
>
> **Hàm phụ `_search_records`:** embed câu hỏi, tính `_dot(query, record_embedding)` cho mọi record, sắp xếp giảm dần, lấy `top_k`. Kết quả trả về bỏ trường `embedding` để in ra dễ đọc. Mọi embedder trong lab đều trả vector đã chuẩn hoá (‖v‖ = 1, mình đã kiểm tra với Gemini), nên dot product chính là cosine. `search()` chỉ gọi `_search_records` trên toàn bộ store.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> **Lọc trước, search sau.** Lấy các record có *mọi* cặp key/value trong `metadata_filter` khớp, rồi đưa tập đó vào cùng hàm `_search_records` mà `search()` dùng, nên hai đường không thể cho kết quả lệch nhau. Nếu làm ngược (lấy top-k rồi mới bỏ kết quả không khớp), k chỗ có thể đã bị tài liệu sai đối tượng chiếm hết, và kết quả còn lại 0 dù store vẫn có tài liệu hợp lệ. `metadata_filter=None` thì tìm trên toàn store.
>
> **Xoá:** `delete_document` giữ lại các record có `metadata["doc_id"] != doc_id`, nên xoá được mọi chunk `file#0`, `file#1`… của cùng một file. Trả `True` nếu số record giảm.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> **Ba bước:**
> 1. `store.search(question, top_k)`.
> 2. Dựng prompt.
> 3. Gọi `llm_fn(prompt)`.
>
> **Cách đưa ngữ cảnh vào prompt:** mỗi chunk được **đánh số kèm nguồn**, dạng `[1] (nguồn: doc_id, source_url)` rồi đến nội dung. Prompt yêu cầu model:
> - chỉ dùng thông tin trong phần NGỮ CẢNH;
> - trích số `[n]` khi dùng một đoạn, để câu trả lời truy vết được về đúng chunk và đúng file (tiêu chí Source Traceability);
> - nếu ngữ cảnh không có đáp án thì trả lời "Không tìm thấy thông tin liên quan…", không suy đoán quy định.
>
> **Store rỗng:** trả luôn câu thông báo, không gọi LLM.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
$ pytest tests/ -v
collecting ... collected 42 items

TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
TestProjectStructure::test_src_package_exists PASSED [  4%]
TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
TestSentenceChunker::test_returns_list PASSED    [ 33%]
TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
TestRecursiveChunker::test_returns_list PASSED   [ 45%]
TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.04s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Dự đoán được ghi **trước khi chạy** `compute_similarity()`. Embedder: `gemini-embedding-001` (vector đã chuẩn hoá). Thứ hạng dự đoán, từ giống nhất đến khác nhất: 5 > 1 > 3 > 4 > 2.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên cần điểm trung bình từ 3.20 để nhận học bổng loại Giỏi. | Muốn được học bổng mức Giỏi, bạn phải có GPA tối thiểu 3.2. | cao (cùng nghĩa, khác từ ngữ) | 0,8923 | ✅ Cao, nhưng chỉ xếp thứ 3 (dự đoán thứ 2) |
| 2 | Hạn nộp hồ sơ học bổng là 17h00 ngày 25/08/2026. | Thư viện mở cửa phục vụ bạn đọc từ thứ Hai đến thứ Sáu. | thấp (khác chủ đề) | 0,6551 | ✅ Thấp nhất trong 5 cặp, dù con số tuyệt đối vẫn khá cao |
| 3 | Học bổng này dành cho sinh viên có hoàn cảnh khó khăn. | Học bổng này không dành cho sinh viên có hoàn cảnh khó khăn. | cao (dù nghĩa trái ngược, gần như trùng từ) | 0,9439 | ✅ Cao, và **cao hơn cả cặp 1** cùng nghĩa |
| 4 | Scholarship application deadline for undergraduate students | Hạn nộp hồ sơ học bổng cho sinh viên đại học | cao (cùng nghĩa, khác ngôn ngữ), nhưng thấp hơn cặp 1 | 0,8159 | ✅ |
| 5 | Mỗi suất học bổng trị giá 5.000.000 đồng. | Mỗi suất học bổng trị giá 50.000.000 đồng. | cao (chỉ khác một chữ số) | 0,9574 | ✅ Cao nhất |

Thứ hạng thực tế: 5 (0,957) > 3 (0,944) > 1 (0,892) > 4 (0,816) > 2 (0,655). So với dự đoán 5 > 1 > 3 > 4 > 2, chỉ lệch ở vị trí của cặp 1 và cặp 3. Nhận định cao/thấp đúng cả 5/5.

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> **Bất ngờ nhất là cặp 3.** Câu "dành cho" và câu "**không** dành cho" có nghĩa trái ngược, vậy mà giống nhau (0,944) hơn cả hai câu cùng nghĩa nhưng khác từ ngữ ở cặp 1 (0,892). Cặp 5 (5 triệu và 50 triệu) cũng giống nhau tới 0,957.
>
> Điều này cho thấy embedding chủ yếu nắm **chủ đề và từ vựng chung**; nó rất kém nhạy với phủ định và con số, là hai thứ quyết định đáp án trong văn bản quy định. Thêm nữa, ngay cả hai câu khác chủ đề vẫn được 0,655, nên với Gemini embedding không thể dùng một ngưỡng tuyệt đối kiểu "> 0,5 là liên quan"; phải so sánh thứ hạng tương đối.
>
> Hệ quả cho RAG: retrieval chỉ đưa về đúng *đoạn nói về chủ đề đó*. Kiểm tra điều kiện "có/không", mức tiền hay đối tượng áp dụng là việc của metadata filter và của LLM khi đọc ngữ cảnh.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

**Cấu hình của tôi:**
- Chiến lược: `HeadingChunker(chunk_size=500)` (trong `bench.py` đặt `STRATEGY = "heading"`), 144 chunk, dài trung bình 349 ký tự.
- Embedder: `gemini-embedding-001`. LLM của agent: `gemini-flash-lite-latest`. `top_k = 3`.
- Output đầy đủ ở `ket_qua_benchmark.txt`. Lệnh chạy: `python bench.py --strategy heading --answers gemini`.
- "Có liên quan" được chấm ở mức nội dung: ngữ cảnh top-3 phải chứa câu bằng chứng của gold answer.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Học bổng KKHT ở Viện Cơ khí VIMARU được xét như thế nào? (filter `student`) | `vimaru-hbkkht-tieu-chuan-sinh-vien#0`: đoạn giới thiệu nguồn của tài liệu, không có tiêu chuẩn | 0,811 | **Một phần.** Top-1 không liên quan; hạng 3 (`#5`, 0,728) là mục "Điều kiện để được đưa vào diện xét"; bảng ngưỡng điểm chỉ ở **hạng 7** | Liệt kê đúng 5 điều kiện vào diện xét (ĐTBHB Khá trở lên, điểm C lần 1, đúng tiến độ, rèn luyện Khá, không bị kỷ luật) nhưng **thiếu ba mức Khá/Giỏi/Xuất sắc**. Đúng một phần |
| 2 | Học bổng Vallet sau đại học 2026 có bao nhiêu suất, mỗi suất bao nhiêu? | `vallet-hoc-bong-sau-dai-hoc#8`: mục "## 2. Giá trị và số lượng học bổng" | 0,865 | **Có** (top-1) | "42 suất, giá trị mỗi suất 34.000.000 VNĐ/suất [1]". **Đúng hoàn toàn** |
| 3 | Quy trình xét học bổng hỗ trợ đột xuất của UEH gồm những bước nào, mất bao lâu? | `ueh-ke-hoach-xet-hoc-bong-2026#20`: nửa sau bảng "4.2. Các mốc thời gian" (bước chi trả, 05–10 ngày) | 0,874 | **Có.** Top-1 và hạng 2 (`#19`) là hai nửa của cùng bảng | Đủ 4 bước kèm thời gian: thường xuyên / 03–05 / 01–03 / 05–10 ngày làm việc. **Đúng hoàn toàn** |
| 4 | Hồ sơ đăng ký học bổng K-T của ULIS gồm những giấy tờ gì? | `ulis-hoc-bong-kt-2025-2026#0`: đoạn mở đầu chỉ có tiêu đề và "Đơn vị ban hành" | 0,824 | **Có** (hạng 2, `#5`: nửa sau danh sách hồ sơ) | Chỉ liệt kê **3/6 giấy tờ** (bài viết về Quỹ K-T, bài phát biểu cảm tưởng, giấy chứng nhận thành tích); thiếu bản tự giới thiệu, bảng điểm, minh chứng hoàn cảnh. Đúng một phần |
| 5 | Tân sinh viên HSB muốn được tài trợ 100% học phí cần điểm bao nhiêu, hoàn trả thế nào? | `hsb-hoc-bong-tan-sinh-vien-2026#10`: phần đầu mục "### 1.3 Tài trợ học phí toàn phần" (mức 100%, trả lại trong 10 năm) | 0,792 | **Có.** Top-1 chứa điều kiện hoàn trả, hạng 3 (`#11`) chứa điều kiện điểm | "THPT từ 24/30 (không môn nào dưới 7) hoặc ĐGNL từ 90/150; TB 3 năm THPT từ 8,0; trả lại học phí cho Quỹ HSB trong vòng 10 năm kể từ khi ra trường". **Đúng hoàn toàn** |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 4 / 5 (Q2, Q3, Q4, Q5). Q1 chỉ lấy được nửa sau của gold answer.
- Chấm theo `doc_id`: 10/10. Chấm theo nội dung: **8/10**.
- Agent trả lời đúng hoàn toàn 3/5 câu (Q2, Q3, Q5), đúng một phần 2/5 (Q1, Q4), và không bịa thông tin ở câu nào.

**Hai lỗi của chiến lược heading mà tôi rút ra từ bảng trên:**
1. **Chunk gần như chỉ có tiêu đề lại thắng.** Đoạn mở đầu `ulis…#0` (chỉ có tiêu đề và đơn vị ban hành) và `vimaru…#0` (giới thiệu nguồn) đứng top-1. Lý do là chúng gần như chỉ chứa đúng những từ khoá của câu hỏi ("học bổng K-T", "ULIS", "khuyến khích học tập"), không có nội dung nào khác làm loãng vector. Cách sửa: gộp đoạn mở đầu ngắn vào mục kế tiếp, hoặc bỏ chunk dưới khoảng 150 ký tự.
2. **Mục dài bị tách thì mất một nửa danh sách.** Mục "4. Hồ sơ đăng ký" của ULIS dài hơn 500 ký tự nên bị cắt làm 2 chunk (`#4`, `#5`). Cả hai đều mang heading, nhưng chỉ `#5` lọt top-3, nên agent chỉ liệt kê được 3/6 giấy tờ. Cách sửa: nâng `chunk_size` riêng cho HeadingChunker (ví dụ 800) để mục danh sách không bị chia, hoặc khi một mảnh của mục lọt top-k thì tự kéo thêm các mảnh cùng mục vào ngữ cảnh.

**A/B metadata filter (Q1) trên chiến lược của tôi:**
- Không filter: top-3 là `tieu-chuan-sinh-vien#0` (0,811, student) · **`quy-trinh-xet-duyet#0` (0,781, staff)** · `tieu-chuan-sinh-vien#1` (0,746). Agent trả lời *"Không tìm thấy thông tin liên quan"*.
- Có filter `student`: chunk `staff` bị loại, mục "Điều kiện diện xét" (`#5`) được vào top-3. Agent liệt kê được điều kiện cho sinh viên.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> So với FixedSize của bạn Lê Nguyễn Thái Dương, cùng đạt 8/10 nhưng trượt ở câu khác: FixedSize lấy được bảng ngưỡng điểm Q1 (hạng 2) mà heading của tôi bỏ lỡ, vì chunk dài 481 ký tự chứa trọn cả mục và phần chữ quanh bảng. Ngược lại, FixedSize trượt Q2 vì "42 suất" bị trộn với mục khác.
>
> Bài học của tôi: **chunk nhỏ và "sạch" chưa chắc tốt hơn**. Trong một tài liệu ngắn, chunk quá nhỏ làm các mục có điểm sát nhau, và việc mục nào lọt top-3 gần như ngẫu nhiên.
>
> Điều thứ hai tôi học được là phải chấm theo nội dung: nếu chỉ kiểm `doc_id`, cả 4 chiến lược đều đạt 10/10 và tôi sẽ không phát hiện ra hai lỗi ở trên.
>
> Từ RecursiveChunker của bạn Nguyễn Phát Thịnh (4/10), tôi thấy vì sao chunker của mình cần gắn lại heading: cùng một dòng `"- Bài phát biểu cảm tưởng…"`, khi đứng một mình thì xếp hạng 10, còn khi có tiêu đề `## 4. Hồ sơ đăng ký học bổng` đi kèm thì lên hạng 2.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá | Căn cứ |
|----------|-------------------|--------|
| Khởi động (Warm-up) | 5 / 5 | Giải thích cosine kèm ví dụ cao/thấp trong chủ đề học bổng. Bài toán chunk (23 → 25 chunk) có kiểm chứng bằng cách chạy `FixedSizeChunker` |
| Hướng tiếp cận của tôi (My Approach) | 9 / 10 | Giải thích đủ regex lookbehind, 3 trường hợp dừng của đệ quy, lọc trước search sau, cấu trúc prompt có trích dẫn; nêu rõ edge case chưa xử lý (chữ viết tắt, bảng không có dấu câu). Trừ 1đ vì chưa sửa các edge case đó |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 | `pytest tests/ -v` → 42 passed (output thật ở mục 3) |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 | Dự đoán ghi trước khi chạy; đúng hướng cao/thấp 5/5, lệch thứ hạng 1 cặp; có phản ngẫm về phủ định và con số |
| Kết quả truy xuất của tôi (Competition Results) | 8 / 10 | Chấm theo `docs/SCORING.md`: Q2, Q3, Q5 được 2đ (chunk liên quan ở top-1 và agent trả lời đúng); Q1 được 1đ (chỉ lấy được mục điều kiện diện xét, agent trả lời thiếu bảng ngưỡng điểm); Q4 được 1đ (chunk liên quan ở hạng 2, agent chỉ liệt kê 3/6 giấy tờ) |
| **Tổng phần cá nhân** | **57 / 60** | |
