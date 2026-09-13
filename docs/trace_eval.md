# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** [Ngô Gia Quốc]  
> **Mã Sinh Viên / Mã Học viên:** [2A202602757]  
> **Chủ đề Lựa chọn:** [Trợ lý Tuyển dụng & Sàng lọc CV]  

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 4 / 5 | Quy trình gồm chuỗi bước nối tiếp: (1) trích xuất thông tin từ CV (họ tên, kỹ năng, kinh nghiệm, học vấn) → (2) đối chiếu với tiêu chí JD của vị trí tuyển → (3) chấm điểm / xếp hạng mức độ phù hợp → (4) ra quyết định (đạt / loại / cần xem xét thêm) → (5) nếu đạt, tra lịch rảnh của người phỏng vấn → (6) soạn và gửi thông báo lịch phỏng vấn cho ứng viên.|
| **2. Tool Interaction** | 5 / 5 | Hệ thống cần phải gọi các công cụ/nguồn bên ngoài khác nhau: (a) parser đọc file CV (PDF/DOCX), (b) cơ sở dữ liệu/API lưu tiêu chí tuyển dụng theo từng vị trí (JD), (c) hệ thống lịch (Google Calendar/Outlook MCP) để kiểm tra slot trống của người phỏng vấn, (d) dịch vụ email/SMS để gửi thông báo.|
| **3. Dynamic Decision** | 4 / 5 | Bước tiếp theo phụ thuộc chặt vào kết quả quan sát trước đó: nếu CV không đạt điểm sàn → dừng và gửi thư từ chối (rẽ nhánh sớm); nếu đạt → tiếp tục tra lịch; nếu người phỏng vấn không có slot trống trong tuần → cần tìm phương án thay thế (đổi người phỏng vấn/đổi ngày) trước khi gửi thông báo. |
| **4. Long Horizon Goal** | 4 / 5 | Hệ thống phải duy trì mục tiêu xuyên suốt cho từng vị trí tuyển dụng qua nhiều lượt xử lý — có thể kéo dài từ lúc nhận CV, sàng lọc hàng loạt ứng viên, đến khi hoàn tất lịch phỏng vấn toàn bộ đợt tuyển. Cần "nhớ" trạng thái từng ứng viên (đã lọc, đang chờ lịch, đã gửi thông báo) trong suốt vòng đời của một đợt tuyển dụng. |
| **TỔNG ĐIỂM AGENTIC FIT** | **17 / 20** | *17/20 > 12/20 → Bài toán RẤT PHÙ HỢP để triển khai như một Agentic System.* |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dán 1 đoạn trích xuất log tiêu biểu từ file `docs/trace_waterfall.json` sinh ra từ phản hồi LLM API thật:

```json
[
  {
    "step": 1,
    "action_type": "TOOL_EXECUTION",
    "tool_name": "academic_query",
    "arguments": {
      "student_id": "SV2026001"
    },
    "observation": {
      "status": "SUCCESS",
      "student_id": "SV2026001",
      "data": {
        "full_name": "Nguyễn Văn An",
        "gpa": 3.85
      }
    },
    "latency_ms": 120.5
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [ ] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (Gemini/OpenAI).
- **Tổng số Test Cases đã chạy thành công:** 5 / 5 test cases.
- **Số lượt gọi Tool qua MCP Server chính xác:** 2 lượt.
- **Kết quả đẩy Repo nộp bài:** [v] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
