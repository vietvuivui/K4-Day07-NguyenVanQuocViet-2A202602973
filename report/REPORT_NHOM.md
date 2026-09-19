# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Violet
**Thành viên:** Nguyễn Văn Quốc Việt (2A202602973), Nguyễn Phát Thịnh (2A202602645), Lê Nguyễn Thái Dương (2A202602383), Vũ Việt Hoàng (2A202602398)
**Ngày:** 2026-09-19

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Học bổng đại học tại Việt Nam, gồm thông báo và quy định học bổng của các trường (FTU, HSB, NEU, UEH, ULIS, VIMARU, VTTU) và một quỹ học bổng bên ngoài (Quỹ Vallet), thuộc chủ đề L3A "dịch vụ/quy định đại học".

**Tại sao nhóm chọn chủ đề này?**
> Học bổng là câu hỏi sinh viên tra cứu thường xuyên, và câu trả lời có đáp án kiểm chứng được (số tiền, số suất, ngưỡng điểm, hạn nộp). Nhờ vậy dễ viết gold answer trích nguyên văn. Các thông báo học bổng có cấu trúc mục rõ ràng (Đối tượng / Tiêu chí / Hồ sơ / Hạn nộp) nên phù hợp để thử chunk theo heading. Ngoài ra, nhiều tài liệu dùng chung từ vựng ("học bổng", "hồ sơ", "hạn nộp", "điểm trung bình"), nên đây là bài kiểm tra khó và thực tế cho retrieval và metadata filter.

### Danh sách tài liệu (Data Inventory)

Toàn bộ corpus nằm trong `data/hoc-bong/`, và được kiểm kê trong `data/hoc-bong/sources.csv`. Số ký tự là độ dài phần nội dung sau khi làm sạch, không tính frontmatter.

| # | Tên tài liệu (`doc_id`) | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | `ftu-hoc-bong-toto-2026` — FTU: Học bổng Công ty TNHH TOTO Việt Nam 2026 | https://qldt.ftu.edu.vn/thong-bao-xet-chon-hoc-bong-cong-ty-tnhh-toto-viet-nam-nam-2026/ | 2026-09-19 / not-stated (đăng 18/08/2026) | 4.042 | audience=student, student_level=undergraduate, institution=ftu, department=ftu-academic-affairs, category=scholarship, language=vi |
| 2 | `hsb-hoc-bong-tan-sinh-vien-2026` — HSB: Học bổng cho các chương trình đại học 2026 | https://www.hsb.edu.vn/news/undergraduate-incoming-scholarship-2026 | 2026-09-19 / not-stated (đăng 03/03/2026) | 7.230 | audience=student, student_level=prospective, institution=hsb, department=hsb-undergraduate-office, category=scholarship, language=vi |
| 3 | `neu-hoc-bong-vung-tuong-lai-2025-2026` — NEU: Học bổng "Vững tương lai" 2025-2026 | https://mis.neu.edu.vn/vi/tin-tuc-khoa-htttql/trien-khai-va-thu-ho-so-hoc-bong-vung-tuong-lai-nam-hoc-2025-2026 | 2026-09-19 / not-stated (đăng 13/08/2026) | 1.703 | audience=student, student_level=undergraduate, institution=neu, department=neu-student-union, category=scholarship, language=vi |
| 4 | `ueh-ke-hoach-xet-hoc-bong-2026` — UEH: Kế hoạch xét học bổng năm 2026 | https://dsa.ueh.edu.vn/tin-tuc/kh-xet-hb-ueh-2026/ | 2026-09-19 / not-stated (đăng 23/02/2026) | 5.027 | audience=student, student_level=undergraduate, institution=ueh, department=ueh-student-affairs, category=scholarship, language=vi |
| 5 | `ulis-hoc-bong-kt-2025-2026` — ULIS: Học bổng K-T 2025-2026 | https://student.ulis.vnu.edu.vn/thong-bao-chuong-trinh-hoc-bong-k-t-nam-hoc-2025-2026/ | 2026-09-19 / not-stated | 2.098 | audience=student, student_level=undergraduate, institution=ulis, department=ulis-student-affairs, category=scholarship, language=vi |
| 6 | `vallet-hoc-bong-sau-dai-hoc` — Quỹ Vallet: Học bổng sau đại học miền Bắc 2026 | https://rvn-vallet.org/hoc-bong-khoi-sau-dai-hoc/ | 2026-09-19 / **02-2026/TB-HBSĐHMB** (26/05/2026) | 6.686 | audience=student, student_level=graduate, institution=vallet, department=external-foundation, category=scholarship, language=vi |
| 7 | `vimaru-hbkkht-tieu-chuan-sinh-vien` — VIMARU: Tiêu chuẩn học bổng KKHT (phần sinh viên) | https://sme.vimaru.edu.vn/ctsv/quy-trinh-cap-hoc-bong-khuyen-khich-hoc-tap-cho-sinh-vien | 2026-09-19 / not-stated | 2.381 | audience=student, student_level=undergraduate, institution=vimaru, department=vimaru-sme-student-affairs, category=scholarship, language=vi |
| 8 | `vimaru-hbkkht-quy-trinh-xet-duyet` — VIMARU: Quy trình xét duyệt học bổng KKHT (phần cán bộ) | https://sme.vimaru.edu.vn/ctsv/quy-trinh-cap-hoc-bong-khuyen-khich-hoc-tap-cho-sinh-vien | 2026-09-19 / not-stated | 3.165 | audience=staff, institution=vimaru, department=vimaru-sme-student-affairs, category=scholarship, language=vi |
| 9 | `vttu-hoc-bong-hoc-gia-fulbright-2025-2026` — VTTU: Học bổng Học giả Fulbright 2025-2026 | https://vttu.edu.vn/thong-bao-ve-chuong-trinh-hoc-bong-hoc-gia-fulbright-viet-nam-va-hoc-gia-hoa-ky-asean-nam-hoc-2025-2026/ | 2026-09-19 / not-stated | 2.602 | audience=faculty, institution=vttu, department=vttu-research-international, category=scholarship, language=vi |

**Tổng:** 9 tài liệu, 34.934 ký tự. Phân bố audience: `student` 7, `staff` 1, `faculty` 1.

**Quy trình thu thập và làm sạch:**
- **Crawl:** dùng `scripts/fetch_public_pages.py` với `data/urls.csv`. Script kiểm robots.txt, giãn cách ≥ 1 giây, dùng User-Agent riêng của lab.
- **Làm sạch tay từng file:**
  - Xoá menu, tin liên quan, link Google Form và số điện thoại cá nhân của cán bộ.
  - Giữ nguyên điều khoản, con số và mốc thời gian.
  - Đặt lại cấu trúc heading `##` / `###` theo mục của văn bản gốc.
- **Sửa lỗi của crawler:** crawler làm phẳng bảng mức học bổng HSB 1.1 (các ô `colspan` bị trộn), nên đọc sai cặp mức tiền–điều kiện. Nhóm dựng lại bảng từ HTML gốc.
- **Tách tài liệu theo audience:** trang VIMARU gộp tiêu chuẩn cho sinh viên và các bước xét duyệt của cố vấn học tập/Hội đồng khoa/Phòng CTSV. Nhóm tách thành 2 file (`student` và `staff`) để `search_with_filter()` có việc thật để lọc.
- **Lỗi của chính nguồn:** giữ nguyên văn và ghi chú "(nguyên văn nguồn)", không tự sửa số liệu. Ví dụ UEH ghi "28/4/2026 – 18/5/2025", Vallet có 2 dòng "tham gia cuộc thi quốc tế không có giải" với điểm khác nhau.
- **Kiểm tra checkpoint 2** (script trong `docs/DATA_COLLECTION.md` mục 6): 9/9 file đủ metadata, `sources.csv` khớp 1-1, audience có 3 giá trị.

**Nguồn đã thử nhưng loại khỏi corpus:**

| Nguồn | Lý do loại |
|---|---|
| vn.usembassy.gov (Fulbright Visiting Scholar) | `disallowed by robots.txt` |
| vietnamplus.vn (tin Fulbright) | robots.txt trả về nội dung nén gzip làm crawler crash (`UnicodeDecodeError`); ngoài ra đây là báo, không phải nguồn chính thức của trường |
| ctsv.ued.udn.vn (quy định học bổng KKHT) | Trang chống bot, chỉ trả về "Please wait while we check your connection security" |
| daotao.ueh.edu.vn (quy định KKHT 2013) | Crawl được nhưng là quy định cũ (2013), chỉ dành cho sinh viên, không bổ sung được audience mới |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ. Tất cả là trang công khai được robots.txt cho phép; số điện thoại và tên cán bộ liên hệ đã được lược bỏ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata. `document_version` chỉ ghi số hiệu khi nguồn thực sự nêu (Vallet); các file còn lại ghi `not-stated`, còn ngày đăng (nếu có) được ghi riêng ở `published_at`.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string (slug, trùng tên file) | `vimaru-hbkkht-tieu-chuan-sinh-vien` | Khoá duy nhất để `delete_document()` và để truy ngược chunk về tài liệu khi chấm "chunk nào chứa thông tin". |
| `title` | string | `FTU - Học bổng Công ty TNHH TOTO Việt Nam 2026` | Hiển thị nguồn trong câu trả lời của agent, giúp kiểm tra grounding. |
| `source_url` | string (URL) | `https://rvn-vallet.org/hoc-bong-khoi-sau-dai-hoc/` | Minh bạch nguồn; agent trích dẫn được link gốc. |
| `retrieved_at` | date `YYYY-MM-DD` | `2026-09-19` | Biết dữ liệu được lấy khi nào, vì thông báo học bổng thay đổi theo năm. |
| `document_version` | string | `02-2026/TB-HBSĐHMB` / `not-stated` | Phân biệt văn bản có số hiệu chính thức với tin đăng thường; không bịa số hiệu. |
| `published_at` | date (tuỳ chọn) | `2026-08-18` | Lọc hoặc ưu tiên thông báo mới nhất khi nhiều năm cùng tồn tại. |
| `audience` | enum: `student` / `faculty` / `staff` / `all` | `staff` | **Chiều lọc chính.** Loại chunk dành cho cán bộ/giảng viên khi sinh viên hỏi (vd. hai file VIMARU dùng chung từ vựng "phân loại học tập, rèn luyện"). |
| `student_level` | enum: `prospective` / `undergraduate` / `graduate` | `graduate` | Tách học bổng tân sinh viên (HSB), đại học và sau đại học (Vallet) vì điều kiện rất khác nhau. |
| `institution` | string | `ueh` | Lọc theo trường khi câu hỏi nêu tên trường ("Học bổng UEH…"), tránh lấy nhầm quy định của trường khác. |
| `department` | string | `ftu-academic-affairs` | Cho biết đơn vị ban hành (phòng đào tạo, hội sinh viên, quỹ ngoài). |
| `category` | string | `scholarship` | Hiện mọi file đều là `scholarship`; giữ trường này để mở rộng corpus sang học phí, KTX… mà không đổi schema. |
| `language` | string | `vi` | Toàn bộ corpus là tiếng Việt (đã kiểm tra không bị tự dịch). Dùng để chọn embedder đa ngữ phù hợp. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

**Đặc điểm corpus ảnh hưởng tới chunking:**
- Tài liệu ngắn, từ 1.703 đến 7.230 ký tự.
- Tổ chức theo heading: tổng cộng 44 heading `##` và 16 heading `###`.
- Có nhiều **bảng Markdown**: mức học bổng HSB, lịch xét học bổng UEH, bảng tiêu chuẩn và lưu hồ sơ VIMARU.
- Nhiều câu dài liệt kê điều kiện. Một số dòng bảng không có dấu chấm câu, nên cách tách theo câu sẽ khó cắt đúng.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare(body, chunk_size=500)` trên 3 tài liệu đại diện cho 3 kiểu cấu trúc: bảng lớn (HSB), bảng lịch (UEH) và văn bản ngắn nhiều mục (VIMARU sinh viên).
- Frontmatter YAML đã được bỏ trước khi đo.
- `chunk_size=500` được dùng thống nhất với `bench.py` (fixed_size có overlap 50, by_sentences gom 3 câu/chunk).
- Dòng `heading` (chiến lược custom của nhóm) được thêm để so sánh.
- Lệnh tái tạo: `python bench.py --baseline`.

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình (min–max) | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `hsb-hoc-bong-tan-sinh-vien-2026` (7.230 ký tự) | FixedSizeChunker (`fixed_size`) | 16 | 498,8 (480–500) | **Không.** Cắt giữa dòng bảng và giữa từ. Ví dụ chunk thứ 2 bắt đầu bằng `u) \| 25 \| Không yêu cầu…` và kết thúc ở `…hoàn cảnh khó kh`, mất luôn dòng tiêu đề bảng |
| `hsb-hoc-bong-tan-sinh-vien-2026` | SentenceChunker (`by_sentences`) | 15 | 480,0 (60–1.339) | **Kém.** Bảng không có dấu chấm câu nên nhiều heading và cả bảng bị gộp thành một "câu"; chunk dài nhất 1.339 ký tự, vượt xa 500 |
| `hsb-hoc-bong-tan-sinh-vien-2026` | RecursiveChunker (`recursive`) | 22 | 327,0 (73–487) | **Khá.** Cắt ở dòng trống nên giữ nguyên đoạn và từng dòng bảng, nhưng chunk nằm giữa mục không mang tên mục/tên trường |
| `hsb-hoc-bong-tan-sinh-vien-2026` | HeadingChunker (`heading`, custom) | 32 | 363,6 (161–497) | **Tốt.** Mỗi chunk là một mục và mở đầu bằng đường dẫn heading (`# Học bổng… HSB` → `### 1.3 Tài trợ học phí…`). Bảng dài bị tách nhưng từng mảnh vẫn có heading |
| `ueh-ke-hoach-xet-hoc-bong-2026` (5.027 ký tự) | FixedSizeChunker (`fixed_size`) | 12 | 464,8 (77–500) | **Không.** Cắt ngang các dòng của bảng mốc thời gian |
| `ueh-ke-hoach-xet-hoc-bong-2026` | SentenceChunker (`by_sentences`) | 10 | 501,1 (160–1.395) | **Kém.** Bảng lịch bị gộp thành chunk 1.395 ký tự |
| `ueh-ke-hoach-xet-hoc-bong-2026` | RecursiveChunker (`recursive`) | 16 | 312,6 (36–485) | **Khá.** Có chunk vụn 36 ký tự (chỉ còn một dòng heading) |
| `ueh-ke-hoach-xet-hoc-bong-2026` | HeadingChunker (`heading`, custom) | 21 | 347,3 (166–484) | **Tốt.** Bảng `4.2` nằm cùng chunk với `## 4. Học bổng Hỗ trợ đột xuất` |
| `vimaru-hbkkht-tieu-chuan-sinh-vien` (2.381 ký tự) | FixedSizeChunker (`fixed_size`) | 6 | 438,5 (131–500) | **Một phần.** Bảng tiêu chuẩn nằm trọn trong một chunk, nhưng chunk bắt đầu giữa heading (`" cụ thể cho các mức học bổng"`) |
| `vimaru-hbkkht-tieu-chuan-sinh-vien` | SentenceChunker (`by_sentences`) | 4 | 593,2 (511–645) | **Kém.** Mọi chunk đều vượt 500 ký tự; heading của mục sau bị dính vào cuối câu của mục trước (`…trong năm học. ## `) |
| `vimaru-hbkkht-tieu-chuan-sinh-vien` | RecursiveChunker (`recursive`) | 7 | 338,6 (133–484) | **Khá.** Bảng tiêu chuẩn nằm cùng heading của nó nhưng bị gộp thêm mục "Thời gian cấp học bổng" |
| `vimaru-hbkkht-tieu-chuan-sinh-vien` | HeadingChunker (`heading`, custom) | 10 | 309,8 (191–461) | **Tốt.** Chunk bảng tiêu chuẩn chỉ gồm tiêu đề tài liệu, heading mục và bảng, không lẫn mục khác |

**Nhận xét baseline:**
- **Fixed-size** đều nhất về độ dài nhưng bỏ qua cấu trúc, nên thường cắt ngang bảng, thứ nguy hiểm nhất với corpus toàn con số.
- **SentenceChunker** không hợp với corpus này: bảng Markdown và danh sách gạch đầu dòng không có dấu kết câu, nên không có giới hạn độ dài.
- **Recursive** là phương án tổng quát tốt nhất trong 3 chiến lược có sẵn.
- **Heading** tạo nhiều chunk hơn (lặp lại đường dẫn heading ở mỗi chunk) nhưng mỗi chunk tự mô tả được nó thuộc tài liệu nào, mục nào.

### Chiến lược của từng thành viên

> **Phân vai:**
> - R1 · Data: Nguyễn Văn Quốc Việt.
> - R2 · Benchmark: Lê Nguyễn Thái Dương.
> - R3 · Strategy: Nguyễn Phát Thịnh, điều phối để không ai trùng chiến lược và chạy baseline cho nhóm.
> - Report & Demo Lead: Vũ Việt Hoàng.
>
> Chiến lược chunk theo heading (bắt buộc theo ràng buộc L3A) do Nguyễn Văn Quốc Việt thực hiện.

**Thành viên 1 — Nguyễn Văn Quốc Việt (2A202602973) (R1 · Data)**
- **Loại chiến lược:** custom — chunk theo heading/mục (`HeadingChunker`), bắt buộc theo ràng buộc L3A.
- **Mô tả & lý do chọn cho chủ đề này:** Mỗi thông báo học bổng chia mục rõ ràng (Đối tượng, Tiêu chí, Hồ sơ, Hạn nộp…), và mỗi câu benchmark thường chỉ cần đúng một mục. Tách tại các dòng `##`/`###` giúp mỗi chunk là một đơn vị nghĩa trọn vẹn, và bảng không bị cắt ngang. Nên gắn tiêu đề tài liệu cùng heading cha vào đầu mỗi chunk để chunk ngắn (vd. "## 2. Giá trị mỗi suất học bổng") vẫn mang ngữ cảnh "ULIS – học bổng K-T". Mục nào quá dài thì chia tiếp bằng `RecursiveChunker`.
- **Cấu hình:** `HeadingChunker(chunk_size=500)`, trong `bench.py` đặt `STRATEGY = "heading"`.
- **Code snippet (nếu custom):** Trích từ `src/chunking.py`:
```python
class HeadingChunker:
    HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")

    def chunk(self, text: str) -> list[str]:
        chunks, path, body_lines = [], [], []   # path = heading của mục hiện tại + các heading cha

        def flush() -> None:
            body = "\n".join(body_lines).strip()
            if body:
                chunks.extend(self._section_chunks([line for _, line in path], body))
            body_lines.clear()

        for line in text.splitlines():
            match = self.HEADING_PATTERN.match(line)
            if not match:
                body_lines.append(line)
                continue
            flush()                                   # gặp heading mới -> đóng mục trước
            level = len(match.group(1))
            while path and path[-1][0] >= level:      # bỏ các heading cùng cấp / cấp sâu hơn
                path.pop()
            path.append((level, line.strip()))
        flush()
        return chunks

    def _section_chunks(self, headings: list[str], body: str) -> list[str]:
        prefix = "\n".join(headings)
        whole = f"{prefix}\n{body}" if prefix else body
        if len(whole) <= self.chunk_size:
            return [whole]
        # Mục quá dài: cắt tiếp bằng RecursiveChunker và gắn lại đường dẫn heading vào TỪNG mảnh con
        body_budget = max(100, self.chunk_size - len(prefix) - 1)
        pieces = RecursiveChunker(chunk_size=body_budget).chunk(body)
        return [f"{prefix}\n{piece}" if prefix else piece for piece in pieces]
```

**Thành viên 2 — Nguyễn Phát Thịnh (2A202602645) (R3 · Strategy)**
- **Loại chiến lược:** `RecursiveChunker` (separators `["\n\n", "\n", ". ", " ", ""]`, chunk_size = 500). Trong `bench.py` đặt `STRATEGY = "recursive"`.
- **Mô tả & lý do chọn:** Corpus đã được làm sạch với dòng trống giữa các đoạn, mục và bảng. Vì vậy ưu tiên tách theo `\n\n` sẽ gần với cách chia theo đoạn mà không cần biết cú pháp heading. Đây là phương án tổng quát để so với chunk theo heading: cho thấy lợi ích đến từ cấu trúc văn bản hay chỉ từ việc cắt đúng ranh giới đoạn.
- **Code snippet (nếu custom):** Không (dùng lớp có sẵn).

**Thành viên 3 — Lê Nguyễn Thái Dương (2A202602383) (R2 · Benchmark)**
- **Loại chiến lược:** `FixedSizeChunker` có overlap (chunk_size = 500, overlap = 50). Trong `bench.py` đặt `STRATEGY = "fixed_size"`.
- **Mô tả & lý do chọn:** Đây là đường cơ sở đơn giản nhất. Overlap giúp giảm rủi ro cắt đôi một điều kiện (vd. "3.20 ≤ ĐTBHB < 3.60 | Từ 80 điểm"). So sánh với 2 chiến lược trên để đo xem cắt bỏ qua cấu trúc làm mất bao nhiêu điểm retrieval trên văn bản nhiều bảng.
- **Code snippet (nếu custom):** Không (dùng lớp có sẵn).

**Thành viên 4 — Vũ Việt Hoàng (2A202602398) (Report & Demo Lead)**
- **Loại chiến lược:** `SentenceChunker` (gom 3 câu/chunk). Trong `bench.py` đặt `STRATEGY = "by_sentences"`.
- **Mô tả & lý do chọn:** Kiểm tra giả thuyết "cắt theo ranh giới câu giữ được ý trọn vẹn" trên văn bản quy định. Đây là đối chứng cho hai chiến lược dựa trên cấu trúc (recursive, heading): nếu corpus chủ yếu là câu văn thì cách này đủ tốt, còn nếu corpus nhiều bảng và danh sách thì nó sẽ lộ điểm yếu. Ngoài chiến lược riêng, thành viên này gom kết quả cả nhóm và dẫn phần thuyết trình.
- **Code snippet (nếu custom):** Không (dùng lớp có sẵn).

### So Sánh Giữa Các Thành Viên

**Điều kiện đo chung:**
- Embedder `gemini-embedding-001` (vector 3072 chiều, đã chuẩn hoá). **Không dùng mock.**
- `chunk_size=500`, `top_k=3`, cùng 9 tài liệu và cùng 5 câu hỏi. Mỗi thành viên chỉ đổi dòng `STRATEGY` trong `bench.py`.
- Output đầy đủ nằm trong `results/ket_qua_benchmark_<chiến lược>.txt`, bảng tổng hợp ở `results/ket_qua_benchmark_tong_hop.txt`.
- Điểm chấm ở **mức nội dung**: tài liệu gold ở top-1 **và** ngữ cảnh top-3 chứa câu bằng chứng thì 2đ; tài liệu gold ở top-2/3 và ngữ cảnh chứa câu bằng chứng thì 1đ; không thoả thì 0đ. Q1 tính bản có filter `student`.

| Thành viên | Chiến lược (Strategy) | Số chunk / dài TB | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----|----------------------|-----------|----------|
| Nguyễn Văn Quốc Việt | HeadingChunker (custom) | 144 / 349 | **8** (Q2, Q3, Q4, Q5) | Mỗi chunk mang đường dẫn heading nên mảnh danh sách vẫn biết thuộc trường nào, mục nào. **Duy nhất lấy đúng Q2** ("42 suất" top-1, 0,865). Lấy được Q4, Q5 mà recursive trượt | Trượt Q1: các mục trong cùng tài liệu có điểm sát nhau (hạng 2–7 chỉ trong khoảng 0,746–0,717), nên chunk bảng ngưỡng điểm bị đẩy xuống hạng 7. Nhiều chunk nhất (144) |
| Nguyễn Phát Thịnh | RecursiveChunker | 109 / 319 | 4 (Q1, Q3) | Cắt ở dòng trống nên giữ nguyên dòng bảng; lấy đúng bảng quy trình UEH (Q3 top-1) | Mảnh danh sách bị tách khỏi tiêu đề mục: chunk đáp án Q4 xếp hạng 10, Q5 hạng 12; Q2 hạng 6 |
| Lê Nguyễn Thái Dương | FixedSizeChunker (overlap 50) | 80 / 481 | **8** (Q1, Q3, Q4, Q5) | Chunk dài (481 ký tự) nên thường chứa trọn cả mục và heading của nó; overlap giúp bảng VIMARU không bị cắt đôi | Cắt giữa từ và giữa dòng bảng. Q2: "42 suất" nằm chung chunk với đoạn "cán bộ nhận lương" và mục 3 nên bị pha loãng, xếp hạng 5 |
| Vũ Việt Hoàng | SentenceChunker (3 câu) | 90 / 386 | 4 (Q3, Q4) | Q3, Q4 vẫn lấy được | Bảng và danh sách không có dấu câu nên bị gộp với mục khác; Q1 hạng 4, Q5 hạng 5 |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **HeadingChunker và FixedSize hoà nhau 8/10, nhưng trượt ở hai câu khác nhau.** Điều này có nghĩa chưa có chiến lược nào vượt trội hẳn.
>
> Nhóm chọn **HeadingChunker** cho corpus quy định vì lỗi của nó *sửa được*. Nó trượt Q1 do các mục cùng tài liệu có điểm quá sát nhau, và chỉ cần tăng `top_k` lên 7 là lấy được, hoặc bỏ tiêu đề tài liệu ở mỗi chunk. Ngược lại, lỗi của FixedSize (Q2) là **cấu trúc**: câu trả lời bị trộn với nội dung khác trong một chunk, tăng `top_k` cũng không giúp mà phải đổi cách cắt.
>
> Recursive (4/10) cho thấy cắt đúng ranh giới đoạn là **chưa đủ**. Nếu mảnh con không mang theo tiêu đề mục thì một dòng như `"- Bài phát biểu cảm tưởng…"` không còn gì để nối với câu hỏi "hồ sơ học bổng K-T của ULIS". Đây chính là chi tiết "gắn lại tiêu đề vào từng mảnh con" mà HeadingChunker làm.

### Phân tích lỗi (Failure cases)

**Failure case 1: chunk đúng chủ đề nhưng không có số liệu thắng chunk chứa đáp án** (Q2; recursive, fixed_size, by_sentences)
- **Hỏng ở đâu:** câu hỏi "Học bổng Vallet… có bao nhiêu suất và mỗi suất trị giá bao nhiêu?". Cả 3 chiến lược đều đưa đúng tài liệu Vallet lên top-1, nên chấm theo `doc_id` là 2đ, nhưng không chunk nào trong top-3 chứa "42 suất", nên chấm theo nội dung là 0đ. Chunk đáp án chỉ xếp hạng 6 (recursive), hạng 5 (fixed_size), hạng 4 (by_sentences). Top-1 lại là đoạn mở đầu *"Nhằm khuyến khích, hỗ trợ học viên sau đại học…"* (0,847–0,849). Ở fixed_size, agent (Gemini) trả lời đúng quy tắc chống bịa: *"Không tìm thấy thông tin liên quan trong cơ sở tri thức."*
- **Vì sao:** cosine đo **độ giống chủ đề**, không đo lượng thông tin trả lời được. Đoạn mở đầu nhắc lại gần như mọi từ của câu hỏi ("học bổng Vallet", "học viên sau đại học", "2026") nhưng không có con số nào. Trong khi đó dòng "42 suất / 34.000.000 VNĐ" bị gộp chung chunk với đoạn *"Lưu ý… cán bộ nhận lương"* (recursive, by_sentences) hoặc mục "3. Điều kiện" (fixed_size), nên vector bị pha loãng.
- **Đề xuất sửa:**
  1. Chunk theo heading. Đã kiểm chứng: HeadingChunker tách riêng mục "## 2. Giá trị và số lượng" nên đứng top-1 (0,865).
  2. Kết hợp tìm kiếm từ khoá (BM25) với vector cho câu hỏi về con số.
  3. Tăng `top_k` lên 5–6 rồi rerank.

**Failure case 2: đúng tài liệu nhưng sai mục; top-3 bị chiếm bởi các mục cùng tài liệu** (Q1; HeadingChunker)
- **Hỏng ở đâu:** với filter `student`, cả 3 chỗ top-3 đều thuộc đúng tài liệu gold (`vimaru-hbkkht-tieu-chuan-sinh-vien#0`, `#1`, `#5`), nhưng không chunk nào chứa bảng ngưỡng điểm. Chunk bảng xếp **hạng 7** (0,717). Chấm theo `doc_id` là 2đ, chấm theo nội dung là 0đ.
- **Vì sao:**
  - Tài liệu này ngắn và mọi mục đều nói về cùng một chủ đề, nên điểm của các mục rất sát nhau: hạng 2 là 0,746, hạng 7 là 0,717, chênh chỉ 0,03. Việc mục nào lọt top-3 gần như ngẫu nhiên.
  - HeadingChunker lặp lại tiêu đề tài liệu `# Tiêu chuẩn xét học bổng khuyến khích học tập…` ở đầu *mọi* chunk. Điều đó càng kéo các chunk về gần nhau.
  - Chunk bảng gần như chỉ có ký hiệu (`| 3.20 ≤ ĐTBHB < 3.60 | Từ 80 điểm |`), ít từ ngữ tự nhiên để khớp với câu "được xét như thế nào".
  - Chunk hạng 3 (mục "Điều kiện để được đưa vào diện xét") vẫn chứa **một nửa** gold answer.
- **Đề xuất sửa:**
  1. Chỉ gắn heading của *mục*, không gắn tiêu đề tài liệu, vào chunk; tiêu đề đã có trong metadata `title`.
  2. Viết thêm một câu mô tả trước bảng khi làm sạch dữ liệu, ví dụ "Mức học bổng được xác định theo điểm trung bình học bổng và điểm rèn luyện như sau:".
  3. Với tài liệu ngắn, lấy nhiều chunk từ cùng tài liệu (`top_k` 5–7) hoặc trả về cả tài liệu.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

Mọi gold answer đều trích nguyên văn từ file trong `data/hoc-bong/` và đã được đối chiếu tới từng dòng. 5 câu phủ đủ 4 dạng hỏi (điều kiện, tra số liệu, quy trình, liệt kê) và 5 tài liệu khác nhau. Bộ câu hỏi, tài liệu gold và "câu bằng chứng" dùng để chấm tự động được khai báo trong `QUERIES` của `bench.py`, để mọi thành viên chạy đúng cùng một bộ.

| # | Dạng | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|---|-------|-------------------------------|--------------------------|
| 1 | Điều kiện — **cần `metadata_filter={"audience": "student"}`** | Học bổng khuyến khích học tập ở Viện Cơ khí VIMARU được xét như thế nào? | Theo tiêu chuẩn cho sinh viên: loại Khá 2.50 ≤ ĐTBHB < 3.20 và điểm rèn luyện từ 70; loại Giỏi 3.20 ≤ ĐTBHB < 3.60 và từ 80; loại Xuất sắc ĐTBHB ≥ 3.60 và từ 90 đến 100. Điều kiện vào diện xét: ĐTBHB loại Khá trở lên, điểm học phần C trở lên ở lần thi thứ nhất, học đúng tiến độ, rèn luyện Khá trở lên, không bị kỷ luật từ mức Khiển trách trở lên. | `vimaru-hbkkht-tieu-chuan-sinh-vien`, mục "Tiêu chuẩn cụ thể cho các mức học bổng" và "Điều kiện để được đưa vào diện xét HBKKHT" |
| 2 | Tra số liệu | Học bổng Vallet dành cho học viên sau đại học năm 2026 có bao nhiêu suất và mỗi suất trị giá bao nhiêu? | 42 suất dành cho học viên cao học và nghiên cứu sinh; mỗi suất 34.000.000 VNĐ. | `vallet-hoc-bong-sau-dai-hoc`, mục "2. Giá trị và số lượng học bổng" |
| 3 | Quy trình | Quy trình xét học bổng hỗ trợ đột xuất của UEH gồm những bước nào và mất bao lâu? | 4 bước: (1) tiếp nhận yêu cầu hỗ trợ từ người học/cố vấn học tập — thường xuyên; (2) kiểm tra, phản hồi, yêu cầu bổ sung minh chứng hoàn cảnh khó khăn — 03–05 ngày làm việc; (3) trình xin ý kiến Ban Giám đốc — 01–03 ngày làm việc sau khi bổ sung đủ hồ sơ; (4) chi trả học bổng, cấn trừ học phí — 05–10 ngày làm việc sau khi có tờ trình. | `ueh-ke-hoach-xet-hoc-bong-2026`, mục "4.2. Các mốc thời gian thực hiện" (thuộc "4. Học bổng Hỗ trợ đột xuất") |
| 4 | Liệt kê | Hồ sơ đăng ký học bổng K-T của ULIS gồm những giấy tờ gì? | (1) Bản tự giới thiệu (theo mẫu); (2) bảng điểm năm học 2024-2025 có xác nhận (sinh viên năm nhất: giấy triệu tập trúng tuyển và giấy chứng nhận kết quả thi THPT 2025); (3) minh chứng hoàn cảnh khó khăn; (4) bài viết tìm hiểu về Quỹ học bổng K-T (01–02 trang A4); (5) bài phát biểu cảm tưởng (01–02 trang A4); (6) bản photo giấy chứng nhận thành tích (nếu có). Kèm bản mềm 1 file pdf. | `ulis-hoc-bong-kt-2025-2026`, mục "4. Hồ sơ đăng ký học bổng" |
| 5 | Điều kiện + số liệu | Tân sinh viên HSB muốn được tài trợ 100% học phí có điều kiện thì cần điểm thi bao nhiêu và phải hoàn trả thế nào? | Điểm tổ hợp xét tuyển thi tốt nghiệp THPT từ 24/30 (không môn nào dưới 7) hoặc điểm ĐGNL ĐHQGHN từ 90/150, kèm xác nhận hoàn cảnh khó khăn và điểm TB 3 năm THPT theo tổ hợp từ 8,0. Phải trả lại học phí cho Quỹ Học bổng HSB trong vòng 10 năm kể từ khi ra trường theo hợp đồng ký kết với HSB. | `hsb-hoc-bong-tan-sinh-vien-2026`, mục "1.3 Tài trợ học phí toàn phần có điều kiện" |

**Vì sao Q1 cần metadata filter:** câu hỏi "được xét như thế nào" không nói người hỏi là ai, và corpus có **hai tài liệu cùng chủ đề, cùng từ vựng nhưng khác đối tượng và khác đáp án**. Cả hai được tách từ cùng một trang VIMARU:
- `vimaru-hbkkht-quy-trinh-xet-duyet` (`staff`) trả lời bằng quy trình: cố vấn học tập họp lớp → Hội đồng khoa → Phòng CTSV, kèm hạn nộp theo học kỳ.
- `vimaru-hbkkht-tieu-chuan-sinh-vien` (`student`) trả lời bằng ngưỡng điểm.

Không lọc thì retrieval có thể lấy chunk quy trình của cán bộ, và agent trả lời sai đối tượng. `bench.py` chạy Q1 hai lần (A: không filter, B: filter `student`) để lấy số liệu A/B.

**Cách chấm tự động trong `bench.py`:** một chunk được tính là "liên quan" khi nó thuộc đúng tài liệu gold **và** chứa câu bằng chứng lấy từ đoạn gold:

| Câu | Câu bằng chứng |
|---|---|
| Q1 | `3.20 ≤ ĐTBHB < 3.60` |
| Q2 | `42 suất` |
| Q3 | `Trình xin ý kiến Ban Giám đốc` |
| Q4 | `Bài phát biểu cảm tưởng` |
| Q5 | `24/30` |

`bench.py` chấm **hai mức** cho mỗi câu:

| Mức | Cách chấm | 2đ | 1đ | 0đ |
|---|---|---|---|---|
| **Theo `doc_id`** (dễ dãi) | Chỉ xét tài liệu gold có trong top-3 không | Tài liệu gold ở top-1 | Tài liệu gold ở top-2/3 | Không có |
| **Theo nội dung** (dùng để chấm) | Như trên, **cộng thêm** điều kiện ngữ cảnh top-3 phải chứa câu bằng chứng | Tài liệu gold ở top-1 và ngữ cảnh chứa đáp án | Tài liệu gold ở top-2/3 và ngữ cảnh chứa đáp án | Vắng, hoặc ngữ cảnh không trả lời được |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).
>
> Embedder: `gemini-embedding-001`. Lệnh tái tạo: `python bench.py --strategy all`. Ở CP5, `bench.py` từng chạy bằng `_mock_embed` vì máy chưa có embedder thật; các số liệu mock đó **không được dùng** trong báo cáo này.

**Chấm hai mức, và chênh lệch giữa chúng** (mỗi ô ghi `theo doc_id / theo nội dung`):

| Chiến lược | Q1 (filter) | Q2 | Q3 | Q4 | Q5 | Q1 không filter | **Tổng theo `doc_id`** | **Tổng theo nội dung** |
|---|---|---|---|---|---|---|---|---|
| fixed_size | 2/2 | 2/**0** | 2/2 | 2/2 | 2/2 | 2/**0** | 10/10 | **8/10** |
| heading | 2/**0** | 2/2 | 2/2 | 2/2 | 2/2 | 2/**0** | 10/10 | **8/10** |
| recursive | 2/2 | 2/**0** | 2/2 | 2/**0** | 2/**0** | 2/**0** | 10/10 | **4/10** |
| by_sentences | 2/**0** | 2/**0** | 2/2 | 2/2 | 2/**0** | 2/**0** | 10/10 | **4/10** |

> **Phát hiện đáng giá nhất:** chấm theo `doc_id` thì **cả 4 chiến lược đều đạt 10/10**, vì tài liệu gold luôn đứng top-1 ở mọi câu. Nếu dừng ở mức đó, nhóm sẽ kết luận "chiến lược nào cũng như nhau". Chấm theo nội dung mới lộ ra khoảng cách 8 và 4, và cho thấy **8/20 lượt truy xuất** (5 câu × 4 chiến lược) lấy đúng tài liệu mà ngữ cảnh vẫn không đủ để trả lời. Nếu tính thêm 4 lượt Q1 không filter thì con số là **12/24**. Lý do là corpus gồm những tài liệu ngắn, chỉ về một chủ đề, nên tìm đúng tài liệu thì dễ, còn tìm đúng *mục* trong tài liệu mới là phần khó.

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | VIMARU: xét HB KKHT (filter `student`) | fixed_size (chunk bảng ở hạng 2) | fixed_size ✅, recursive ✅ (hạng 3), heading ❌ (hạng 7), by_sentences ❌ (hạng 4) | Không filter thì **cả 4 chiến lược đều 0đ** (xem A/B bên dưới) |
| 2 | Vallet: số suất và giá trị | **heading** (top-1, 0,865) | Chỉ heading ✅ | Xem failure case 1 (mục 2) |
| 3 | UEH: quy trình hỗ trợ đột xuất | fixed_size, recursive, by_sentences (top-1) | Cả 4 ✅ (heading hạng 2) | Bảng 4.2 bị heading tách thành 2 chunk (#19, #20), cả 2 đều nằm trong top-3 |
| 4 | ULIS: hồ sơ học bổng K-T | heading, by_sentences (hạng 2) | heading ✅, fixed_size ✅ (hạng 3), by_sentences ✅, recursive ❌ (hạng 10) | Mảnh danh sách của recursive không có tiêu đề mục |
| 5 | HSB: tài trợ 100% học phí | fixed_size (top-1) | fixed_size ✅, heading ✅ (hạng 3), recursive ❌ (hạng 12), by_sentences ❌ (hạng 5) | Cùng nguyên nhân với Q4 |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> **Có, ở Q1, và thấy rõ ở cả 4 chiến lược.** Top-3 của hai lần chạy khác nhau (id, score, audience):
>
> | Chiến lược | A) Không filter | B) `{"audience": "student"}` |
> |---|---|---|
> | fixed_size | `tieu-chuan-sinh-vien#0` 0,823 student · **`quy-trinh-xet-duyet#0` 0,758 staff** · **`quy-trinh-xet-duyet#4` 0,700 staff** | `tieu-chuan-sinh-vien#0` 0,823 · **`#4` 0,688 (bảng ngưỡng điểm)** · `#3` 0,686 |
> | recursive | `tieu-chuan-sinh-vien#0` 0,806 · **`quy-trinh-xet-duyet#0` 0,781 staff** · `tieu-chuan-sinh-vien#1` 0,742 | `#0` 0,806 · `#1` 0,742 · **`#5` 0,691 (bảng ngưỡng điểm)** |
> | heading | `tieu-chuan-sinh-vien#0` 0,811 · **`quy-trinh-xet-duyet#0` 0,781 staff** · `tieu-chuan-sinh-vien#1` 0,746 | `#0` 0,811 · `#1` 0,746 · `#5` 0,728 |
> | by_sentences | `tieu-chuan-sinh-vien#0` 0,823 · **`quy-trinh-xet-duyet#0` 0,769 staff** · `ueh-…#2` 0,712 | `#0` 0,823 · `ueh-…#2` 0,712 · `tieu-chuan-sinh-vien#2` 0,699 |
>
> Không lọc thì chunk quy trình của **cán bộ** (`staff`) luôn đứng **hạng 2** ở mọi chiến lược (fixed_size còn thêm một chunk `staff` ở hạng 3). Nó chiếm đúng chỗ mà chunk bảng ngưỡng điểm lẽ ra được vào, nên điểm nội dung là 0/4 chiến lược. Có filter thì chunk `staff` bị loại, fixed_size và recursive kéo được bảng ngưỡng điểm vào top-3, và điểm nội dung tăng từ 0 lên 2 ở hai chiến lược này.
>
> Hậu quả ở mức câu trả lời, kiểm chứng bằng Gemini làm LLM trên fixed_size:
> - Không filter, agent trả lời bằng **quy trình của cán bộ**: *"quy trình xét duyệt được thực hiện qua các bước/bộ phận gồm cố vấn học tập, Hội đồng khoa và Phòng Công tác sinh viên (CTSV)… Thời hạn thực hiện: Học kỳ I trước ngày 15/04, học kỳ II trước ngày 30/09 hàng năm"*. Đây là đáp án sai đối tượng cho một sinh viên.
> - Có filter, agent liệt kê đúng điều kiện diện xét và ba mức Khá/Giỏi/Xuất sắc kèm ngưỡng ĐTBHB và điểm rèn luyện.
>
> Đánh đổi của filter: lọc cứng theo `audience` sẽ loại cả tài liệu `all` nếu corpus có. Corpus này không có tài liệu `all`, nhưng nếu mở rộng thì nên lọc theo `audience ∈ {student, all}`.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> - **Metadata chỉ có giá trị khi dữ liệu có nhiều hơn một giá trị để lọc.** Lượt thu thập đầu tiên cho ra 6/6 tài liệu `audience: student`, nên filter vô dụng. Nhóm phải chủ động tìm nguồn cho giảng viên (Fulbright) và tách trang VIMARU thành 2 file theo audience.
> - **Output crawler không đáng tin nếu không đọc lại.** Crawler làm phẳng bảng HSB (ô `colspan` bị trộn), khiến cặp "mức tiền – điều kiện" bị đọc sai. Nếu chunk trên bản thô, agent có thể trả lời sai số tiền mà vẫn trông như có căn cứ. Bản thô còn chứa khoảng 80% là menu và tin không liên quan (FTU: file thô 26 KB, bản sạch 5,6 KB).
> - **Chấm theo `doc_id` thổi phồng kết quả.** Cả 4 chiến lược đều 10/10 theo `doc_id`, nhưng theo nội dung chỉ còn 8 / 8 / 4 / 4. Lấy đúng tài liệu mà ngữ cảnh không chứa đáp án là lỗi phổ biến nhất của hệ thống.
> - **Metadata filter đổi đáp án từ sai đối tượng sang đúng đối tượng.** Không lọc thì chunk quy trình của cán bộ đứng hạng 2 ở mọi chiến lược, và agent trả lời sinh viên bằng hạn nộp của Phòng CTSV. Lọc `audience=student` thì agent trả lời đúng ngưỡng điểm.

**Failure case (tóm tắt, chi tiết ở mục 2):**
> 1. **Q2 (recursive, fixed_size, by_sentences):** đoạn mở đầu đúng chủ đề nhưng không có số liệu (0,85) thắng chunk chứa "42 suất" (hạng 4–6), vì cosine đo độ giống chủ đề chứ không đo thông tin trả lời được. Sửa: chunk theo heading (đã kiểm chứng: top-1), hoặc kết hợp BM25.
> 2. **Q1 (heading):** top-3 toàn đúng tài liệu nhưng sai mục; chunk bảng ở hạng 7 vì các mục cùng tài liệu chỉ chênh 0,03 điểm. Sửa: bỏ tiêu đề tài liệu lặp lại ở mọi chunk, thêm câu mô tả trước bảng, tăng `top_k` với tài liệu ngắn.
> 3. **Q4, Q5 (recursive):** mảnh danh sách bị tách khỏi tiêu đề mục (`"- Bài phát biểu cảm tưởng…"`) nên xếp hạng 10 và 12. Sửa: gắn lại heading vào mảnh con, đúng như HeadingChunker làm (đưa lên hạng 2 và 3).

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng tài liệu và cùng câu hỏi, nhưng **mỗi chiến lược trượt ở câu khác nhau**:
> - FixedSize trượt Q2, vì đáp án bị trộn với nội dung khác trong một chunk dài.
> - Heading trượt Q1, vì chunk quá nhỏ và quá giống nhau trong một tài liệu ngắn.
> - Recursive trượt Q4, Q5, vì mảnh con mất tiêu đề mục.
>
> Vì vậy tổng điểm (8 và 8) che mất sự khác biệt; phải xem từng câu mới hiểu được vì sao.
>
> Bài học lớn nhất: **chunk phải tự mô tả được nó thuộc mục nào**, và **chấm theo nội dung chứ không theo `doc_id`**. Nếu chỉ chấm theo `doc_id` thì 4 chiến lược đều đạt 10/10, và nhóm đã không học được gì từ lần so sánh này.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ chọn nguồn theo **chiều lọc định dùng ngay từ đầu**: tìm các văn bản quy định có phần dành cho nhiều đối tượng (quy chế học bổng có mục trách nhiệm của khoa/cố vấn học tập), thay vì gom thông báo học bổng rồi mới phát hiện toàn bộ là `student`. Nhóm cũng sẽ ưu tiên các văn bản quy định có số hiệu (như Vallet) thay vì tin đăng, để `document_version` có giá trị thật. Ngoài ra, nên kiểm robots.txt và thử "View Page Source" trước khi đưa URL vào danh sách, để khỏi mất thời gian với trang bị chặn hoặc có cơ chế chống bot.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá | Căn cứ |
|----------|-------------------|--------|
| Lựa chọn tài liệu (Document Set Quality) | 9 / 10 | 9 tài liệu công khai, đủ metadata, `sources.csv` khớp 1-1, làm sạch tay, ghi rõ nguồn đã loại và lý do; tách VIMARU theo audience để filter có việc thật. Trừ 1đ vì audience lệch (7 `student` / 1 `staff` / 1 `faculty`) và phần lớn là tin đăng, ít văn bản quy định có số hiệu |
| Thiết kế chiến lược (Strategy Design) | 13 / 15 | 4 chiến lược không trùng nhau, trong đó có chiến lược custom theo heading; có baseline, chấm hai mức, A/B filter và 3 failure case có nguyên nhân và cách sửa. Trừ 2đ vì mọi chiến lược dùng chung `chunk_size=500`, chưa thử tinh chỉnh tham số (vd. `top_k`, `chunk_size` riêng cho heading) để kiểm chứng các cách sửa đã đề xuất |
| Chất lượng truy xuất (Retrieval Quality) | 8 / 10 | Chiến lược tốt nhất của nhóm (heading và fixed_size) đạt 8/10 khi chấm theo nội dung; không chiến lược nào trả lời đủ cả 5 câu |
| Thuyết trình (Demo) | 4 / 5 (dự kiến) | Đã chuẩn bị `bench.py` chạy được và demo A/B Q1; điểm chính thức phụ thuộc buổi thuyết trình |
| **Tổng phần nhóm** | **34 / 40** | |
