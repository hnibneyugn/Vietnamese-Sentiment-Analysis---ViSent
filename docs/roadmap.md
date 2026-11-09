# LỘ TRÌNH "VỪA HỌC VỪA LÀM": ViSent MLOps + Jenkins (Local)

Bản này sắp xếp lại dự án trong `mlops-local-jenkins-spec.md` thành các **module nhỏ**. Mỗi module = học một khái niệm → làm ngay → kiểm tra → cố tình phá để hiểu sâu. Kết thúc module luôn có một hệ thống **chạy được**.

---

## 0. Cách học

### Vòng lặp cho mỗi module (không bỏ bước nào)

| Bước | Thời lượng | Việc làm |
|---|---|---|
| 1. Học nhanh | 30–60 phút | Đọc/xem tối thiểu để hiểu khái niệm. KHÔNG học hết rồi mới làm |
| 2. Làm theo | 2–4 giờ | Thực hiện các nhiệm vụ trong module, tự gõ, không copy nguyên khối |
| 3. Kiểm tra | 15 phút | Đạt đủ tiêu chí "Xong khi..." |
| 4. Phá thử | 30 phút | Cố tình làm hỏng, quan sát lỗi, sửa lại |
| 5. Ghi chú | 15 phút | Viết 5 dòng: học được gì, lỗi gì, vì sao. Git tag `m<số>-done` |

### Nguyên tắc
1. **Chạy được trước, đẹp sau.** Mỗi module phải có kết quả nhìn thấy được.
2. **Mỗi lần chỉ thêm một công cụ mới.** Không cài Jenkins + MLflow + Prometheus cùng lúc.
3. **Model đơn giản trước (TF-IDF + LR) để vòng lặp MLOps nhanh.** PhoBERT chỉ đưa vào ở Module 8, khi pipeline đã vững. Như vậy mỗi lần train chỉ mất vài giây thay vì nhiều phút, và bạn học DevOps nhanh hơn rất nhiều.
4. **Khi kẹt hơn 45 phút:** ghi lại lỗi, bỏ qua phần đó hoặc hỏi AI kèm log đầy đủ, đừng mắc kẹt cả buổi.
5. **Mọi thứ nằm trong Git**, kể cả cấu hình hạ tầng.

---

## Bản đồ module & Lịch trình 13 tuần (8–10 giờ/tuần)

| Tuần / # | Module | Công cụ mới | Kết quả nhìn thấy | Tag Git |
|---|---|---|---|---|
| Tuần 1 (M0) | Môi trường | WSL2, Docker, GPU | Container thấy GPU (`make doctor` xanh) | `m0-done` |
| Tuần 2 (M1) | App ML tối thiểu | FastAPI, sklearn, pytest | Gọi `/predict` ra kết quả, pytest xanh | `m1-done` |
| Tuần 3 (M2) | Container hoá | Dockerfile, Compose, React, Nginx/Traefik | `docker compose up` chạy cả web + api | `m2-done` |
| Tuần 4 (M3) | CI đầu tiên | Jenkins, pytest, ruff | Push code → Jenkins báo xanh/đỏ | `m3-done` |
| Tuần 5 (M4) | CD | Registry, Gitea, webhook | Push → tự deploy staging + smoke test | `m4-done` |
| Tuần 6 (M5) | Version dữ liệu | DVC, MinIO | Quay lại phiên bản dữ liệu cũ (`dvc repro`) | `m5-done` |
| Tuần 7 (M6) | Theo dõi thí nghiệm | MLflow, Postgres | So sánh nhiều lần train trên UI | `m6-done` |
| Tuần 8 (M7) | Pipeline huấn luyện tự động | Jenkins train, Model Registry | Model tốt hơn mới được lên Production | `m7-done` |
| Tuần 9 (M8) | Nâng cấp model | PhoBERT, ONNX, GPU Agent | Cùng pipeline, model mạnh hơn + ONNX | `m8-done` |
| Tuần 10 (M9) | Giám sát | Prometheus, Grafana, Loki, k6 | Dashboard realtime + Alert | `m9-done` |
| Tuần 11 (M10) | Drift & retrain | Evidently | Drift → tự gọi Jenkins retrain | `m10-done` |
| Tuần 12 (M11) | Hardening | Trivy, hadolint, gitleaks, backup | Pipeline chặn lỗi bảo mật + khôi phục DB | `m11-done` |
| Tuần 13 (M12) | Capstone | Bootstrap, (tuỳ chọn) k3d, Helm, ArgoCD | Dựng lại toàn hệ thống từ đầu bằng 1 lệnh | `m12-done` |

---

## Chi tiết từng Module

### Module 0 – Môi trường
- **Học nhanh:** WSL2 là gì, Docker image vs container vs volume, vì sao GPU trong container cần NVIDIA Container Toolkit.
- **Làm:**
  1. Cài WSL2 + Ubuntu; đặt `.wslconfig` giới hạn RAM.
  2. Cài Docker Desktop (backend WSL2), bật tích hợp với Ubuntu.
  3. Chạy container CUDA mẫu và chạy `nvidia-smi` bên trong.
  4. Tạo repo `visent`, thêm `Makefile` có target `doctor` kiểm tra các công cụ.
- **Xong khi:** `make doctor` (hoặc `py scripts/doctor.py`) in ra phiên bản Docker, Python, Node, Git và thấy RTX 4060 trong container.
- **Phá thử:** Dừng Docker rồi chạy lại lệnh, đọc thông báo lỗi. Đặt RAM WSL2 rất thấp và xem điều gì xảy ra.
- **Tự kiểm tra:** Image khác container ở điểm nào? Dữ liệu trong container mất khi nào?

### Module 1 – App ML tối thiểu
- **Học nhanh:** Pipeline ML cơ bản (tiền xử lý → vector hoá → phân loại), REST API, Pydantic validation.
- **Làm:**
  1. Lấy một bộ dữ liệu sentiment tiếng Việt nhỏ (kiểm tra giấy phép), để ở `data/raw/`.
  2. Viết `ml/src/models/train.py`: TF-IDF + Logistic Regression, lưu `model.joblib`.
  3. Viết FastAPI: `POST /predict` (nhận `text`, trả `label` + `confidence`), `GET /health`.
  4. Viết 3–5 test bằng pytest cho API và hàm tiền xử lý.
- **Xong khi:** `curl` gọi `/predict` trả kết quả hợp lý; `pytest` xanh.
- **Phá thử:** Gửi chuỗi rỗng, chuỗi 1 triệu ký tự, JSON sai. API phản hồi thế nào? Thêm validation để xử lý.
- **Tự kiểm tra:** Vì sao nên validate đầu vào ngay tại biên API?

### Module 2 – Container hoá
- **Học nhanh:** Dockerfile, multi-stage build, layer cache, `.dockerignore`, Compose, healthcheck, chạy non-root.
- **Làm:**
  1. Viết Dockerfile cho `api` (multi-stage, user không phải root, có `HEALTHCHECK`).
  2. Viết `docker-compose.app.yml` chạy `api`.
  3. Thêm frontend React tối giản và Dockerfile cho `web`; thêm gateway (Traefik hoặc Nginx).
  4. Model nạp từ volume hoặc biến môi trường đường dẫn, **không** nhúng cứng vào image.
- **Xong khi:** `docker compose up` rồi mở trình duyệt, nhập review, thấy kết quả.
- **Phá thử:** Sửa một dòng code và build lại: layer nào được cache, layer nào build lại? Đổi thứ tự lệnh `COPY` trong Dockerfile và so sánh thời gian build.
- **Tự kiểm tra:** Vì sao tag `latest` nguy hiểm? Multi-stage giúp gì cho kích thước image?

### Module 3 – CI đầu tiên với Jenkins
- **Học nhanh:** CI là gì, Jenkins controller vs agent, Declarative Pipeline, workspace, stage/step.
- **Làm:**
  1. Chạy Jenkins bằng Docker Compose (volume cho `jenkins_home`).
  2. Tạo Pipeline job đầu tiên chỉ có `echo "hello"`.
  3. Viết `pipelines/Jenkinsfile` với các stage: Checkout → Lint (ruff) → Test (pytest + coverage) → Build image.
  4. Đặt ngưỡng coverage; lưu báo cáo test.
- **Xong khi:** Jenkins tự kéo mã, chạy đủ stage và hiện kết quả xanh. Thấy lịch sử build.
- **Phá thử:** Cố tình viết code sai lint, rồi làm test fail. Pipeline phải đỏ đúng stage. Sau đó thử làm Jenkins mất kết nối Docker và đọc log.
- **Tự kiểm tra:** Pipeline as Code có lợi gì so với cấu hình bằng giao diện? Vì sao nên chạy build trên agent chứ không trên controller?

### Module 4 – CD: Registry, Gitea, Webhook
- **Học nhanh:** Registry là gì, tagging theo git SHA, webhook, Multibranch Pipeline, môi trường staging.
- **Làm:**
  1. Dựng Gitea và Docker registry local.
  2. Chuyển repo sang Gitea; cấu hình Multibranch Pipeline + webhook.
  3. Thêm stage: Push image (tag = git SHA) → Deploy Staging (`docker compose up -d`) → Smoke test (`/health`, một lần `/predict`).
  4. Lưu thông tin đăng nhập registry vào Jenkins Credentials.
- **Xong khi:** Push lên `develop` → tự build, đẩy image, deploy staging, smoke test xanh.
- **Phá thử:** Đẩy một commit làm `/health` trả lỗi. Deploy phải được phát hiện là hỏng. Viết script `rollback.sh` quay về tag trước đó và thử.
- **Tự kiểm tra:** Deploy và Release khác nhau thế nào? Vì sao smoke test cần có sau deploy?

### Module 5 – Version dữ liệu với DVC
- **Học nhanh:** Vì sao không commit dữ liệu lớn vào Git, DVC hoạt động thế nào (file `.dvc`, cache, remote), S3-compatible storage.
- **Làm:**
  1. Dựng MinIO (kèm bucket) bằng Compose.
  2. `dvc init`, theo dõi `data/raw`, cấu hình remote trỏ MinIO.
  3. Viết `ml/dvc.yaml` với stage `prepare` → `train` → `evaluate`; tham số trong `params.yaml`.
  4. Chạy `dvc repro`; thay đổi dữ liệu và chạy lại.
- **Xong khi:** Có thể `git checkout` một commit cũ + `dvc checkout` để lấy lại đúng dữ liệu và kết quả của thời điểm đó.
- **Phá thử:** Xoá thư mục `data/`, chạy `dvc pull` để khôi phục. Đổi một tham số và xem DVC chỉ chạy lại stage cần thiết.
- **Tự kiểm tra:** `dvc.lock` lưu gì? Vì sao nó giúp tái lập thí nghiệm?

### Module 6 – Theo dõi thí nghiệm với MLflow
- **Học nhanh:** Experiment, run, params, metrics, artifacts; khác biệt giữa tracking và registry.
- **Làm:**
  1. Dựng MLflow + Postgres (backend) + MinIO (artifact).
  2. Thêm `mlflow.log_*` vào `train.py`: params, F1, accuracy, confusion matrix, file model.
  3. Chạy 8–10 lần với siêu tham số khác nhau (ngram, C, max_features).
  4. Dùng giao diện MLflow so sánh các run.
- **Xong khi:** Chọn được run tốt nhất dựa trên bảng so sánh, và mở lại được artifact của run cũ.
- **Phá thử:** Chạy lại cùng cấu hình hai lần, kết quả có giống nhau không? Cố định seed để tái lập.
- **Tự kiểm tra:** Vì sao cần log cả phiên bản dữ liệu (hash DVC) vào run?

### Module 7 – Pipeline huấn luyện tự động + Model Registry
- **Học nhanh:** Continuous Training, quality gate, vòng đời model (None → Staging → Production), alias/stage.
- **Làm:**
  1. Viết `pipelines/Jenkinsfile.train`: `dvc pull` → kiểm tra dữ liệu → `dvc repro` → log MLflow → so F1 với model Production.
  2. Đăng ký model vào Registry; nếu đạt gate thì lên `Staging`, smoke test, rồi promote `Production`.
  3. Sửa API để nạp model theo stage từ MLflow (không build model vào image).
  4. Viết `scripts/promote_model.py`.
- **Xong khi:** Đổi dữ liệu/tham số, push → pipeline train tự chạy; model tốt hơn được lên Production và API dùng nó mà không cần build lại image.
- **Phá thử:** Cố tình đẩy dữ liệu nhiễu làm model kém đi. Quality gate phải từ chối. Thử làm API nạp model không tồn tại, xem hành vi `/ready`.
- **Tự kiểm tra:** Vì sao tách vòng đời model khỏi vòng đời code? Gate nên dựa trên những chỉ số nào ngoài F1?

### Module 8 – Nâng cấp lên PhoBERT + ONNX + GPU
- **Học nhanh:** Fine-tune Transformer, fp16, gradient accumulation, ONNX và ONNX Runtime.
- **Làm:**
  1. Thêm `train_phobert.py` dùng cùng giao diện log MLflow và cùng stage DVC.
  2. Cấu hình để vừa 8GB VRAM: fp16, batch nhỏ + gradient accumulation, `max_len` 128.
  3. Dựng Jenkins agent có GPU (nhãn `gpu`), chuyển job train sang agent này.
  4. Xuất ONNX; so sánh độ chính xác và độ trễ với bản PyTorch; API dùng ONNX Runtime.
- **Xong khi:** Cùng pipeline ở Module 7, nhưng model mới (PhoBERT) vượt baseline và được tự động promote.
- **Phá thử:** Tăng batch size cho đến khi OOM, ghi lại ngưỡng. Thử so sánh độ trễ CPU vs GPU khi suy luận.
- **Tự kiểm tra:** Vì sao serving thường dùng ONNX thay vì PyTorch nguyên bản? Đánh đổi giữa độ chính xác và độ trễ là gì?

### Module 9 – Giám sát
- **Học nhanh:** Metrics vs logs vs traces, bốn tín hiệu vàng (latency, traffic, errors, saturation), PromQL cơ bản.
- **Làm:**
  1. Thêm `/metrics` vào API (số request, latency histogram, phân bố nhãn dự đoán, độ tin cậy).
  2. Dựng Prometheus + Grafana + Loki/Promtail bằng file Compose riêng.
  3. Làm dashboard: RPS, p95 latency, tỉ lệ lỗi, phân bố nhãn.
  4. Thêm một cảnh báo (ví dụ lỗi > 5% trong 5 phút).
- **Xong khi:** Chạy `k6` tạo tải và thấy dashboard thay đổi theo thời gian thực; tìm được log của một request cụ thể.
- **Phá thử:** Làm API chậm giả (sleep) hoặc lỗi giả, xem cảnh báo có kích hoạt không.
- **Tự kiểm tra:** Vì sao dùng p95/p99 thay vì trung bình?

### Module 10 – Drift và Retrain tự động
- **Học nhanh:** Data drift, concept drift, prediction drift; chọn ngưỡng; feedback loop.
- **Làm:**
  1. Frontend thêm nút "đúng/sai"; lưu feedback và dữ liệu đầu vào (ẩn danh).
  2. Viết job Evidently so sánh dữ liệu gần đây với tập train; xuất báo cáo HTML.
  3. Khi vượt ngưỡng → gọi Jenkins API chạy `Jenkinsfile.retrain` (gộp feedback vào dữ liệu).
  4. Retrain đi qua đúng quality gate của Module 7.
- **Xong khi:** Mô phỏng drift (đổi phân bố dữ liệu giả lập) → hệ thống tự phát hiện, retrain, và chỉ promote nếu tốt hơn.
- **Phá thử:** Chỉnh ngưỡng quá nhạy hoặc quá lỏng, quan sát hậu quả (retrain liên tục / không bao giờ retrain).
- **Tự kiểm tra:** Khi nào retrain tự động là nguy hiểm? Vì sao vẫn cần gate hoặc người duyệt?

### Module 11 – Hardening
- **Học nhanh:** Supply chain security, quản lý secret, nguyên tắc đặc quyền tối thiểu, chiến lược backup.
- **Làm:**
  1. Thêm Trivy (image + filesystem), hadolint, gitleaks vào Jenkinsfile.
  2. Chuyển toàn bộ secret vào Jenkins Credentials / file `.env` không commit.
  3. Backup Postgres và MinIO bằng script, **thử khôi phục** trên môi trường sạch.
  4. Viết `docs/runbook.md`: sự cố thường gặp và cách xử lý.
- **Xong khi:** Pipeline chặn được image có lỗ hổng CRITICAL và commit chứa secret; khôi phục backup thành công.
- **Phá thử:** Commit thử một khoá giả, xem gitleaks chặn. Dùng base image cũ để Trivy báo lỗi.
- **Tự kiểm tra:** Backup chưa từng khôi phục thử có đáng tin không?

### Module 12 – Capstone
- **Làm (bắt buộc):**
  1. Xoá sạch mọi container và volume, dựng lại toàn hệ thống từ repo bằng `make bootstrap && make up`.
  2. Quay video/ghi chú 10 phút giải thích kiến trúc như thể dạy người khác.
  3. Hoàn thiện `README.md` và `docs/architecture.md`.
- **Mở rộng (tuỳ chọn):** chuyển deploy sang k3d + Helm + ArgoCD; canary/blue-green; A/B hai model; Ansible hoá bootstrap.
- **Xong khi:** Người khác (hoặc bạn sau 1 tháng) làm theo README dựng được hệ thống mà không cần hỏi.

---

## Bảng theo dõi tiến độ

| Module | Học | Làm | Kiểm tra | Phá thử | Ghi chú | Tag git |
|---|---|---|---|---|---|---|
| 0 | [x] | [x] | [x] | [x] | [x] | `m0-done` |
| 1 | [x] | [x] | [x] | [x] | [x] | `m1-done` |
| 2 | [x] | [x] | [x] | [x] | [x] | `m2-done` |
| 3 | [ ] | [ ] | [ ] | [ ] | [ ] | `m3-done` |
| 4 | [ ] | [ ] | [ ] | [ ] | [ ] | `m4-done` |
| 5 | [ ] | [ ] | [ ] | [ ] | [ ] | `m5-done` |
| 6 | [ ] | [ ] | [ ] | [ ] | [ ] | `m6-done` |
| 7 | [ ] | [ ] | [ ] | [ ] | [ ] | `m7-done` |
| 8 | [ ] | [ ] | [ ] | [ ] | [ ] | `m8-done` |
| 9 | [ ] | [ ] | [ ] | [ ] | [ ] | `m9-done` |
| 10 | [ ] | [ ] | [ ] | [ ] | [ ] | `m10-done` |
| 11 | [ ] | [ ] | [ ] | [ ] | [ ] | `m11-done` |
| 12 | [ ] | [ ] | [ ] | [ ] | [ ] | `m12-done` |

## Từ khoá tra cứu theo module

| Module | Từ khoá tìm tài liệu |
|---|---|
| 0 | WSL2 .wslconfig, NVIDIA Container Toolkit WSL2 |
| 2 | Docker multi-stage build, Compose healthcheck |
| 3 | Jenkins Declarative Pipeline, Jenkins agent Docker |
| 4 | Jenkins Multibranch, Gitea webhook, Docker registry:2 |
| 5 | DVC remote S3 MinIO, dvc.yaml stages |
| 6 | MLflow tracking server Postgres MinIO |
| 7 | MLflow Model Registry aliases, Jenkins parameterized build |
| 8 | Hugging Face Trainer fp16, PhoBERT, ONNX Runtime export |
| 9 | prometheus-fastapi-instrumentator, PromQL, Loki Promtail |
| 10 | Evidently data drift report, Jenkins remote trigger API |
| 11 | Trivy image scan, gitleaks, pg_dump restore |
