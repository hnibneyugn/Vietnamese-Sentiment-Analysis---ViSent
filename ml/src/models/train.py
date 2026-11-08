"""Mô-đun huấn luyện mô hình baseline TF-IDF + Logistic Regression (Module 1)."""

import csv
import sys
from dataclasses import dataclass
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import Pipeline

from ml.src.preprocess import preprocess_text

DEFAULT_DATA_PATH = Path("data/raw/reviews_sample.csv")
DEFAULT_MODEL_PATH = Path("models/model.joblib")
VALID_LABELS = {"positive", "negative", "neutral"}


@dataclass(frozen=True)
class TrainResult:
    """Kết quả huấn luyện mô hình baseline."""

    model_path: Path
    num_samples: int
    accuracy: float
    macro_f1: float


def load_dataset(csv_path: Path) -> tuple[list[str], list[str]]:
    """Đọc và kiểm tra tính hợp lệ của tập dữ liệu CSV."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file dữ liệu tại: {csv_path}")

    texts: list[str] = []
    labels: list[str] = []

    with csv_path.open(mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if (
            reader.fieldnames is None
            or "text" not in reader.fieldnames
            or "label" not in reader.fieldnames
        ):
            raise ValueError("File CSV bắt buộc phải có hai cột 'text' và 'label'.")

        for row in reader:
            raw_text = row.get("text")
            raw_label = row.get("label")
            if not raw_text or not raw_label:
                continue

            cleaned_text = preprocess_text(raw_text)
            cleaned_label = raw_label.strip().lower()

            if not cleaned_text:
                continue
            if cleaned_label not in VALID_LABELS:
                raise ValueError(
                    f"Nhãn không hợp lệ '{cleaned_label}'. Chỉ chấp nhận: {sorted(VALID_LABELS)}"
                )

            texts.append(cleaned_text)
            labels.append(cleaned_label)

    if len(texts) < 3 or len(set(labels)) < 2:
        raise ValueError(
            "Tập dữ liệu quá ít hoặc thiếu số lượng nhãn tối thiểu (cần ít nhất 2 lớp khác nhau)."
        )

    return texts, labels


def build_pipeline(
    max_features: int = 5000, c_value: float = 1.0, random_state: int = 42
) -> Pipeline:
    """Khởi tạo pipeline gồm TfidfVectorizer và LogisticRegression."""
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    max_features=max_features,
                    sublinear_tf=True,
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    C=c_value,
                    max_iter=500,
                    random_state=random_state,
                ),
            ),
        ]
    )


def train_and_save(
    data_path: Path = DEFAULT_DATA_PATH,
    model_path: Path = DEFAULT_MODEL_PATH,
) -> TrainResult:
    """Huấn luyện mô hình trên tập dữ liệu và lưu artifact bằng joblib."""
    texts, labels = load_dataset(data_path)
    pipeline = build_pipeline()
    pipeline.fit(texts, labels)

    preds = pipeline.predict(texts)
    acc = float(accuracy_score(labels, preds))
    f1 = float(f1_score(labels, preds, average="macro"))

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_path)

    return TrainResult(
        model_path=model_path,
        num_samples=len(texts),
        accuracy=acc,
        macro_f1=f1,
    )


def main() -> int:
    """Điểm khởi chạy CLI để huấn luyện mô hình baseline."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    result = train_and_save()
    print("=" * 64)
    print("  VISENT MLOPS — HUẤN LUYỆN MODEL BASELINE (MODULE 1)")
    print("=" * 64)
    print(f"  Số lượng mẫu huấn luyện : {result.num_samples}")
    print(f"  Độ chính xác (Accuracy) : {result.accuracy:.4f}")
    print(f"  Điểm Macro F1           : {result.macro_f1:.4f}")
    print(f"  Đã lưu model tại        : {result.model_path}")
    print("=" * 64)
    return 0


if __name__ == "__main__":
    sys.exit(main())
