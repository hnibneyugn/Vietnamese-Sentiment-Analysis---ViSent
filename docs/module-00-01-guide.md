# HƯỚNG DẪN THỰC HÀNH TỪNG BƯỚC: MODULE 0 & MODULE 1

Tài liệu này giúp bạn thực hiện đúng quy trình **5 bước (Học nhanh → Làm theo → Kiểm tra → Phá thử → Ghi chú)** trên chính máy tính của bạn.

---

## PHẦN 1: MODULE 0 — MÔI TRƯỜNG (`m0-done`)

### 1. Chẩn đoán hiện trạng máy của bạn
Qua kiểm tra tự động ban đầu trên máy của bạn:
- **Git:** `2.55.0.windows.5` (Đã có)
- **Python (quản lý qua `uv`):** `3.14.7` & **`uv`:** `0.13.0` (Đã có — dùng lệnh `uv run python ...` thay vì `py` hay `python` trực tiếp vì `python.exe` mặc định của Windows đang trỏ vào stub Microsoft Store)
- **Node.js:** `v24.20.0` (Đã có)
- **GPU Host:** `NVIDIA GeForce RTX 4060 Laptop GPU (8188 MiB)` (Đã nhận diện tốt!)
- **Docker CLI:** `29.8.2` (Đã cài, nhưng **Docker Desktop đang tắt** và chưa cài bản phân phối `Ubuntu` trên WSL2).

### 2. Các bước bạn cần làm ngay (20–30 phút)

#### Bước 2.1: Cấu hình giới hạn RAM cho WSL2 (`.wslconfig`)
Để tránh WSL2 và Docker ngốn hết RAM của Windows khi sau này chạy Jenkins + MLflow + GPU:
```powershell
Copy-Item .\scripts\wslconfig.example "$env:USERPROFILE\.wslconfig"
```

#### Bước 2.2: Cài đặt Ubuntu trên WSL2 (nếu bạn muốn dùng môi trường Linux chuẩn)
```powershell
wsl --install -d Ubuntu-22.04
```
*(Nếu chưa muốn cài Ubuntu ngay, bạn vẫn có thể chạy Docker Desktop trực tiếp từ PowerShell).*

#### Bước 2.3: Bật Docker Desktop & Kiểm tra GPU trong Container
1. Mở ứng dụng **Docker Desktop** trên Windows và chờ trạng thái chuyển sang **Engine running**.
2. Chạy lệnh kiểm tra GPU bên trong container CUDA:
```powershell
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```
3. Chạy bác sĩ kiểm tra hệ thống:
```powershell
uv run python scripts/doctor.py
```
Khi tất cả các mục báo `[OK]`, bạn đã đạt tiêu chí **"Xong khi..."** của Module 0!

#### Bước 2.4: Phá thử & Ghi chú (Bắt buộc)
1. **Thử nghiệm 1:** Quit hẳn Docker Desktop ở khay hệ thống (System Tray), sau đó chạy lại `uv run python scripts/doctor.py` hoặc `docker ps`. Đọc kỹ thông báo lỗi pipe `//./pipe/dockerDesktopLinuxEngine` để nhớ dấu hiệu khi Daemon chết.
2. **Thử nghiệm 2:** Sửa `$env:USERPROFILE\.wslconfig` thành `memory=256MB`, chạy `wsl --shutdown`, rồi bật lại Docker Desktop xem chuyện gì xảy ra (nhớ đổi lại `memory=8GB` sau khi thử xong!).
3. Ghi lại kết quả vào [docs/journal.md](journal.md) và đánh tag:
```powershell
git add .
git commit -m "feat(m0): setup workspace, Makefile and environment doctor"
git tag m0-done
```

---

## PHẦN 2: MODULE 1 — APP ML TỐI THIỂU (`m1-done`)

### Mục tiêu Module 1
Xây dựng pipeline huấn luyện cực nhanh (**TF-IDF + Logistic Regression**) trên dữ liệu tiếng Việt tại `data/raw/reviews_sample.csv`, bọc trong **FastAPI** có kiểm tra dữ liệu đầu vào chặt chẽ bằng **Pydantic**, và đạt **>= 90% test coverage** với `pytest`.

### Cấu trúc file bạn sẽ hoàn thiện ở Module 1
```text
visent/
├── requirements.txt             # Danh sách thư viện (scikit-learn, fastapi, uvicorn, pytest...)
├── ml/
│   └── src/
│       ├── preprocess.py        # Hàm chuẩn hoá văn bản tiếng Việt (xoá khoảng trắng thừa, chữ thường...)
│       └── models/
│           └── train.py         # Đọc CSV -> TF-IDF + LogisticRegression -> lưu models/model.joblib
├── app/
│   └── api/
│       ├── schemas.py           # Pydantic: PredictRequest (min_length=1, max_length=2000), PredictResponse
│       └── main.py              # FastAPI: GET /health, POST /predict
└── tests/
    └── test_api.py              # Kiểm tra happy path, chuỗi rỗng, chuỗi 1 triệu ký tự, JSON sai...
```

### Nhiệm vụ thực hành trong Module 1
1. **Bước 1 (Tiền xử lý & Train):** Viết `ml/src/preprocess.py` và `ml/src/models/train.py` huấn luyện pipeline `TfidfVectorizer(ngram_range=(1, 2))` kết hợp `LogisticRegression`, xuất ra `models/model.joblib`.
2. **Bước 2 (Serving API):** Viết `app/api/main.py` cung cấp:
   - `GET /health` → `{"status": "ok", "model_loaded": true}`
   - `POST /predict` → Nhận `{"text": "..."}` và trả về `{"label": "positive", "confidence": 0.85}`
3. **Bước 3 (Phá thử & Validation):**
   - Gửi chuỗi rỗng `""` hoặc toàn khoảng trắng `"   "` → API phải trả về `422 Unprocessable Entity`.
   - Gửi chuỗi dài 1.000.000 ký tự → API phải chặn ngay ở tầng Pydantic (`max_length`).
   - Gửi JSON sai cú pháp hoặc thiếu trường `text` → Trả về `422`.
4. **Bước 4 (Kiểm thử):** Chạy `pytest` đảm bảo xanh 100% và ghi nhật ký `m1-done`.

> 💡 **Gợi ý:** Khi bạn đã sẵn sàng bắt tay vào **Module 1**, hãy nhắn cho mình: *"Bắt đầu Module 1"* (hoặc tự viết trước rồi nhờ mình review/hướng dẫn từng file).
