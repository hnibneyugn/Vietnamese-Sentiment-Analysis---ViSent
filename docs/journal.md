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

## Module 2 – Container hoá – 2026-11-09
- **Học được:**
  - Tách dự án thành 2 thư mục rõ ràng `backend/` (FastAPI) và `frontend/` (React + TypeScript + Nginx Gateway).
  - Viết `Dockerfile.api` và `Dockerfile.web` theo kiến trúc **Multi-stage build**, chạy bằng quyền **non-root** (`appuser` / `nginx-unprivileged`), có `HEALTHCHECK`, và nạp `model.joblib` qua Read-Only Volume (`./models:/app/models:ro`) thay vì nhúng cứng vào image.
  - Qua 2 thử nghiệm Layer Cache: đặt `COPY package.json` + `RUN npm install` trước `COPY frontend/ ./` giúp tận dụng `CACHED` khi chỉ sửa code giao diện (`App.tsx`); ngược lại nếu đảo thứ tự `COPY` lên trước sẽ làm vỡ cache và bắt chạy lại `npm install` mỗi lần sửa code.
- **Lỗi gặp phải & nguyên nhân:**
  - Ở `Dockerfile.api`: gõ nhầm tên user `appsuer` thay vì `appuser` khiến `docker run` báo lỗi `unable to find user appsuer: no matching entries in passwd file`, và gõ nhầm `model.jiblib` / `./model`.
  - Ở `Dockerfile.web`: truyền `--retries=3s` thay vì số nguyên `--retries=3` gây lỗi `strconv.ParseInt: parsing "3s": invalid syntax`, và thiếu một dấu `/` trong `http://127.0.0.1:8080/`.
- **Trả lời câu hỏi Tự kiểm tra:**
  - *Vì sao tag `latest` nguy hiểm?* -> Vì `:latest` là nhãn động (mutable) bị ghi đè liên tục: không thể biết chính xác container trên Production đang chạy commit nào để giám sát/debug, hai máy chủ kéo `:latest` ở hai thời điểm khác nhau có thể chạy hai bản code khác nhau, và không thể rollback nhanh về bản trước đó khi deploy lỗi.
  - *Multi-stage giúp gì cho kích thước và bảo mật của image?* ->
    1. **Giảm mạnh kích thước image:** Bỏ lại toàn bộ công cụ biên dịch nặng nề (`node_modules` ~200MB, trình biên dịch TypeScript, `pip` cache, `gcc`) ở stage `builder`, chỉ copy thành phẩm (`dist/` nặng vài trăm KB hoặc `/opt/venv`) sang stage `runtime`.
    2. **Tăng cường bảo mật (Giảm bề mặt tấn công - Attack Surface):** Image `runtime` càng ít công cụ thừa (không có `npm`, `pip`, trình biên dịch) thì khi kẻ tấn công khai thác lỗ hổng sẽ càng có ít công cụ để tải mã độc hoặc leo thang đặc quyền, đồng thời giảm số lượng lỗ hổng CVE khi quét bằng Trivy (Module 11).
    3. **Tách bạch các bước (Modular):** Giúp dễ dàng quan sát lỗi xảy ra ở bước cài thư viện/build hay ở bước cấu hình runtime.
- **Điều còn chưa hiểu (hỏi lại sau):**
  - Cách tự động hoá việc chạy lint, pytest và `docker build` mỗi khi push code bằng Jenkins CI (sẽ học ở Module 3).
- **Thời gian thực tế:** 2.0 giờ

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
