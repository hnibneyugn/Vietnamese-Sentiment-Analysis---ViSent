import { type FormEvent, useState } from "react";

/** Nhãn cảm xúc trả về từ API */
export type SentimentLabel = "positive" | "negative" | "neutral";

/** Dữ liệu phản hồi thành công từ POST /api/predict */
export interface PredictResponse {
  label: SentimentLabel;
  confidence: number;
}

/** Dữ liệu lỗi trả về từ FastAPI */
interface ApiErrorDetail {
  detail?: string | Array<{ msg?: string }>;
}

const LABEL_MAP: Record<SentimentLabel, { text: string; color: string }> = {
  positive: { text: "Tích cực (Positive)", color: "#16a34a" },
  negative: { text: "Tiêu cực (Negative)", color: "#dc2626" },
  neutral: { text: "Trung lập (Neutral)", color: "#ca8a04" },
};

/** Giao diện chính phân tích cảm xúc tiếng Việt */
export function App(): JSX.Element {
  const [text, setText] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        const errBody = (await response.json().catch(() => ({}))) as ApiErrorDetail;
        const msg =
          typeof errBody.detail === "string"
            ? errBody.detail
            : errBody.detail?.[0]?.msg ?? `Lỗi HTTP ${response.status}`;
        throw new Error(msg);
      }

      const data = (await response.json()) as PredictResponse;
      setResult(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Đã xảy ra lỗi không xác định.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ maxWidth: 640, margin: "48px auto", padding: 24, background: "#fff", borderRadius: 12, boxShadow: "0 4px 12px rgba(0,0,0,0.08)" }}>
      <h1 style={{ marginTop: 0 }}>ViSent — Phân tích cảm xúc tiếng Việt</h1>
      <p style={{ color: "#475569" }}>Nhập đánh giá sản phẩm để mô hình dự đoán nhãn cảm xúc và độ tin cậy.</p>

      <form onSubmit={(e) => void handleSubmit(e)}>
        <textarea
          rows={4}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Ví dụ: Sản phẩm đóng gói cẩn thận, giao hàng siêu nhanh!"
          style={{ width: "100%", padding: 12, fontSize: 16, borderRadius: 8, border: "1px solid #cbd5e1", boxSizing: "border-box" }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{ marginTop: 12, padding: "10px 20px", fontSize: 16, fontWeight: 600, color: "#fff", background: loading ? "#94a3b8" : "#2563eb", border: "none", borderRadius: 8, cursor: loading ? "not-allowed" : "pointer" }}
        >
          {loading ? "Đang phân tích..." : "Phân tích cảm xúc"}
        </button>
      </form>

      {error && (
        <div role="alert" style={{ marginTop: 16, padding: 12, background: "#fef2f2", color: "#b91c1c", borderRadius: 8 }}>
          <strong>Lỗi:</strong> {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: 16, padding: 16, background: "#f8fafc", borderRadius: 8, borderLeft: `6px solid ${LABEL_MAP[result.label].color}` }}>
          <div style={{ fontSize: 18, fontWeight: 700, color: LABEL_MAP[result.label].color }}>
            Nhãn: {LABEL_MAP[result.label].text}
          </div>
          <div style={{ marginTop: 4, color: "#334155" }}>
            Độ tin cậy (Confidence): <strong>{(result.confidence * 100).toFixed(2)}%</strong>
          </div>
        </div>
      )}
    </main>
  );
}