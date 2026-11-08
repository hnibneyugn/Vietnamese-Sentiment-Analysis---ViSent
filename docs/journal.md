# Nhật ký học tập — ViSent MLOps (`docs/journal.md`)

> Quy tắc: Cuối mỗi module, dành **15 phút** ghi tối thiểu 5 dòng về những gì đã làm, lỗi thực tế gặp phải (đặc biệt ở bước **Phá thử**), và câu trả lời cho phần **Tự kiểm tra** trước khi đánh tag `git tag m<số>-done`.

---

## Module 0 – Môi trường – 2026-11-04
- **Học được:**
  - Sự khác biệt giữa Docker Image (khuôn mẫu bất biến theo layer), Container (tiến trình đang chạy có lớp đọc-ghi tạm thời), và Volume (vùng lưu trữ bền vững nằm ngoài vòng đời container).
  - Cách WSL2 chia sẻ nhân Linux và chuyển tiếp GPU NVIDIA từ Windows Host vào container thông qua NVIDIA Container Toolkit.
- **Lỗi gặp phải & nguyên nhân:**
  - *(Ghi lại khi bạn thử tắt Docker Desktop rồi chạy `doctor.py`, hoặc khi hạ RAM `.wslconfig` xuống quá thấp)*
- **Trả lời câu hỏi Tự kiểm tra:**
  - *Image khác container ở điểm nào?* -> image là một bộ cấu hình được thiết kế sẵn còn container là một nơi để chứa những cái image đó
  - *Dữ liệu trong container mất khi nào?* -> dữ liệu trong coontainer mất khi container bị xóa
- **Điều còn chưa hiểu (hỏi lại sau):**
  - ...
- **Thời gian thực tế:** 0,5 giờ

---

## Module 1 – App ML tối thiểu – 2026-11-08
- **Học được:**
  - Xây dựng pipeline ML cơ bản gồm tiền xử lý tiếng Việt (`NFC`, chữ thường, lọc ký tự đặc biệt) + `TfidfVectorizer` + `LogisticRegression` và đóng gói bằng `joblib`.
  - Phục vụ mô hình qua FastAPI (`/health`, `/predict`) kết hợp kiểm tra dữ liệu đầu vào chặt chẽ bằng Pydantic (`min_length`, `max_length`, `extra="forbid"`, `@field_validator`).
- **Lỗi gặp phải & nguyên nhân:**
  - Khi chạy `curl.exe` trên Windows PowerShell với dấu `"..."` chứa ký tự `@` (`!!! @@@`), PowerShell hiểu nhầm `@` là toán tử splatting và làm vỡ cú pháp JSON gây lỗi `422` hoặc `ParserError`. Khắc phục bằng toán tử `--%` của PowerShell hoặc `Invoke-RestMethod`.
  - Plugin `anyio` của pytest gây treo trên Windows sandbox khi mở socket loopback; khắc phục bằng cờ `-p no:anyio` và tách hàm `initialize_app_state`.
- **Trả lời câu hỏi Tự kiểm tra:**
  - *Vì sao nên validate đầu vào ngay tại biên API?* ->
    1. **Tránh dự đoán rác (Garbage In, Garbage Out):** Chuỗi rỗng hoặc toàn ký tự `!!! @@@` sau khi lọc sẽ thành vector toàn số `0`, khiến model trả về một nhãn ngẫu nhiên với confidence ảo.
    2. **Bảo vệ tài nguyên & chống DoS (Fail-fast):** Chặn chuỗi 1 triệu ký tự ngay ở tầng HTTP/Pydantic giúp tránh tốn RAM/CPU (hoặc tràn VRAM với PhoBERT ở Module 8).
    3. **Phân tách trách nhiệm & mã lỗi rõ ràng:** Trả về đúng mã `422 Unprocessable Entity` (lỗi từ phía client gửi sai) thay vì để lọt vào `model.predict_proba()` gây crash `500 Internal Server Error`.
- **Điều còn chưa hiểu (hỏi lại sau):**
  - Cách đóng gói toàn bộ môi trường Python + FastAPI + Frontend vào Docker container mà không nhúng cứng file model vào image (sẽ học ở Module 2).
- **Thời gian thực tế:** 2.5 giờ

---

## Module 2 – Container hoá – <ngày>
- **Học được:**
- **Lỗi gặp phải & nguyên nhân:**
- **Trả lời câu hỏi Tự kiểm tra:**
  - *Vì sao tag `latest` nguy hiểm? Multi-stage giúp gì cho kích thước image?* ->
- **Điều còn chưa hiểu (hỏi lại sau):**
- **Thời gian thực tế:**

---

## Module 3 – CI đầu tiên với Jenkins – <ngày>
- **Học được:**
- **Lỗi gặp phải & nguyên nhân:**
- **Trả lời câu hỏi Tự kiểm tra:**
- **Điều còn chưa hiểu (hỏi lại sau):**
- **Thời gian thực tế:**

---

## Module 4 – CD: Registry, Gitea, Webhook – <ngày>
- **Học được:**
- **Lỗi gặp phải & nguyên nhân:**
- **Trả lời câu hỏi Tự kiểm tra:**
- **Điều còn chưa hiểu (hỏi lại sau):**
- **Thời gian thực tế:**

---

## Module 5 – Version dữ liệu với DVC – <ngày>
- **Học được:**
- **Lỗi gặp phải & nguyên nhân:**
- **Trả lời câu hỏi Tự kiểm tra:**
- **Điều còn chưa hiểu (hỏi lại sau):**
- **Thời gian thực tế:**

---

## Module 6 – Theo dõi thí nghiệm với MLflow – <ngày>
- **Học được:**
- **Lỗi gặp phải & nguyên nhân:**
- **Trả lời câu hỏi Tự kiểm tra:**
- **Điều còn chưa hiểu (hỏi lại sau):**
- **Thời gian thực tế:**

---

## Module 7 – Pipeline huấn luyện tự động + Model Registry – <ngày>
- **Học được:**
- **Lỗi gặp phải & nguyên nhân:**
- **Trả lời câu hỏi Tự kiểm tra:**
- **Điều còn chưa hiểu (hỏi lại sau):**
- **Thời gian thực tế:**

---

## Module 8 – Nâng cấp lên PhoBERT + ONNX + GPU – <ngày>
- **Học được:**
- **Lỗi gặp phải & nguyên nhân:**
- **Trả lời câu hỏi Tự kiểm tra:**
- **Điều còn chưa hiểu (hỏi lại sau):**
- **Thời gian thực tế:**

---

## Module 9 – Giám sát – <ngày>
- **Học được:**
- **Lỗi gặp phải & nguyên nhân:**
- **Trả lời câu hỏi Tự kiểm tra:**
- **Điều còn chưa hiểu (hỏi lại sau):**
- **Thời gian thực tế:**

---

## Module 10 – Drift và Retrain tự động – <ngày>
- **Học được:**
- **Lỗi gặp phải & nguyên nhân:**
- **Trả lời câu hỏi Tự kiểm tra:**
- **Điều còn chưa hiểu (hỏi lại sau):**
- **Thời gian thực tế:**

---

## Module 11 – Hardening – <ngày>
- **Học được:**
- **Lỗi gặp phải & nguyên nhân:**
- **Trả lời câu hỏi Tự kiểm tra:**
- **Điều còn chưa hiểu (hỏi lại sau):**
- **Thời gian thực tế:**

---

## Module 12 – Capstone – <ngày>
- **Học được:**
- **Lỗi gặp phải & nguyên nhân:**
- **Điều còn chưa hiểu (hỏi lại sau):**
- **Thời gian thực tế:**
