# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** [Ngô Gia Quốc]  
> **Mã Sinh Viên / Mã Học viên:** [2A202602757]  
> **Chủ đề Lựa chọn:** [Trợ lý Học vụ VinUni]  

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ TRƯỚC KHI XÂY DỰNG)

> Bảng dưới đây là bước khảo sát được thực hiện **trước khi thiết kế và xây dựng Trợ lý Học vụ VinUni**. Mục đích là xác định bài toán có cần kiến trúc Agentic/ReAct hay chỉ cần một chatbot trả lời văn bản thông thường.

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình khi khảo sát bài toán |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 4 / 5 | Nhu cầu học vụ không chỉ là trả lời câu hỏi chung. Với một yêu cầu có dữ liệu cá nhân, hệ thống cần nhận diện ý định, xác định dữ liệu cần lấy, chọn thao tác phù hợp, đọc kết quả rồi mới tạo phản hồi. Chuỗi bước này phù hợp với mô hình Reasoning → Action → Observation → Answer. |
| **2. Tool Interaction** | 5 / 5 | Bài toán cần kết nối dữ liệu và tác vụ bên ngoài: tra cứu hồ sơ học vụ theo mã sinh viên, kiểm tra thông tin cố vấn và tạo lịch tư vấn. Vì chatbot thông thường không tự truy xuất hoặc thực thi tác vụ, bài toán cần cơ chế Tool Calling/MCP. |
| **3. Dynamic Decision** | 4 / 5 | Hành động của hệ thống thay đổi theo yêu cầu và dữ liệu trả về: câu hỏi quy chế có thể trả lời trực tiếp; tra cứu hồ sơ cần gọi công cụ; đặt lịch cần dùng công cụ khác; mã sinh viên không tồn tại phải dừng và thông báo phù hợp. Đây là quyết định động dựa trên Observation. |
| **4. Long Horizon Goal** | 3 / 5 | Nghiệp vụ học vụ có thể kéo dài qua nhiều lượt: sinh viên tra cứu hồ sơ, yêu cầu tư vấn, chọn thời gian và theo dõi lịch hẹn. Phiên bản Lab chỉ mô phỏng một lượt xử lý, nhưng bài toán có khả năng mở rộng thành mục tiêu dài hạn có trạng thái. |
| **TỔNG ĐIỂM AGENTIC FIT** | **16 / 20** | *16/20 > 12/20 → Kết quả khảo sát cho thấy bài toán phù hợp để xây dựng bằng kiến trúc Agentic System. Từ kết quả này, hệ thống được thiết kế với ReAct Agent, MCP Server và các Tool học vụ.* |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Đoạn log dưới đây minh họa luồng ReAct **Reasoning Summary → Action → Observation → Final Answer** khi Agent tra cứu sinh viên `SV2026001`. Khi nghiệm thu, thay `latency_ms` bằng giá trị từ file `docs/trace_waterfall.json` được sinh ra sau khi chạy LLM API thật.

```json
[
  {
    "step": 1,
    "query": "Hãy tra cứu thông tin học vụ của sinh viên SV2026001.",
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
        "class": "AI-K4",
        "gpa": 3.85,
        "email": "an.nv@vinuni.edu.vn",
        "status": "Đang học",
        "advisor": "PGS.TS Nguyễn Văn A"
      }
    },
    "latency_ms": 120.5
  },
  {
    "step": 2,
    "query": "Hãy tra cứu thông tin học vụ của sinh viên SV2026001.",
    "action_type": "FINAL_ANSWER",
    "thought": "Tổng hợp kết quả từ MCP Server thành công.",
    "output": "Kết quả tra cứu cho sinh viên SV2026001 (Nguyễn Văn An): Lớp AI-K4, GPA: 3.85, Email: an.nv@vinuni.edu.vn, Trạng thái: Đang học, Cố vấn: PGS.TS Nguyễn Văn A.",
    "latency_ms": 10.0
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [ ] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (Gemini/OpenAI).
- **Tổng số Test Cases dự kiến chạy:** 5 test cases trong `config/test_cases.json`.
- **Số Tool đã triển khai qua MCP Server:** 2 Tool (`academic_query`, `schedule_appointment`).
- [ ] Đã chạy `python src/app.py --all`, kiểm tra `docs/trace_waterfall.json` và cập nhật số liệu nghiệm thu thực tế.
- [ ] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
