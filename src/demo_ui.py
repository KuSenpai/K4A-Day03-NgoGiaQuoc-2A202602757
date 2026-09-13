"""Local browser UI for a safe, observable ReAct/MCP demonstration."""

import json
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from mcp_server import MCPAcademicServer
from prompts import REACT_AGENT_SYSTEM_PROMPT
from providers import get_llm_provider

STATIC_DIR = Path(__file__).resolve().parent / "static"
MAX_QUESTION_LENGTH = 1000


def _final_answer(observation: dict[str, Any]) -> str:
    if observation.get("status") == "SUCCESS" and "data" in observation:
        student = observation["data"]
        return (
            f"Kết quả tra cứu cho {student.get('full_name', 'sinh viên')}: "
            f"lớp {student.get('class', '')}, GPA {student.get('gpa', '')}, "
            f"trạng thái {student.get('status', '')}."
        )
    return observation.get("message", "Agent đã hoàn tất xử lý yêu cầu.")


def run_demo_workflow(question: str) -> dict[str, Any]:
    """Return safe, high-level execution events for the browser demo."""
    provider = get_llm_provider()
    server = MCPAcademicServer()
    response = provider.generate_with_tools(
        question,
        server.list_tools(),
        system_prompt=REACT_AGENT_SYSTEM_PROMPT,
    )

    events = [{
        "kind": "reasoning",
        "title": "Reasoning Summary",
        "detail": "Agent đã phân tích yêu cầu và xác định liệu có cần dữ liệu từ công cụ hay không.",
    }]

    if response.get("type") != "tool_call":
        events.append({
            "kind": "answer",
            "title": "Final Answer",
            "detail": response.get("content", "Agent đã hoàn tất phản hồi."),
        })
        return {"events": events}

    tool_name = response.get("tool_name", "unknown_tool")
    arguments = response.get("arguments", {})
    events.append({
        "kind": "action",
        "title": "Tool Selected",
        "detail": f"Agent chọn {tool_name} để lấy dữ liệu cần thiết.",
        "tool": tool_name,
        "arguments": arguments,
    })

    mcp_response = server.call_tool(tool_name, arguments)
    observation = mcp_response.get("result", {})
    events.append({
        "kind": "observation",
        "title": "MCP Observation",
        "detail": json.dumps(observation, ensure_ascii=False),
    })
    events.append({
        "kind": "answer",
        "title": "Final Answer",
        "detail": _final_answer(observation),
    })
    return {"events": events}


class DemoRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        requested = "demo.html" if self.path in {"/", "/index.html"} else self.path.lstrip("/")
        candidate = (STATIC_DIR / requested).resolve()
        if STATIC_DIR.resolve() not in candidate.parents or not candidate.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content_types = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "application/javascript; charset=utf-8"}
        data = candidate.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_types.get(candidate.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/demo":
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Không tìm thấy endpoint."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_QUESTION_LENGTH + 100:
                raise ValueError
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            question = str(payload.get("question", "")).strip()
            if not 2 <= len(question) <= MAX_QUESTION_LENGTH:
                raise ValueError
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Câu hỏi cần có từ 2 đến 1000 ký tự."})
            return
        try:
            self._send_json(HTTPStatus.OK, run_demo_workflow(question))
        except Exception:
            self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Không thể chạy demo. Vui lòng thử lại."})

    def log_message(self, format: str, *args: Any) -> None:
        return


def start_demo_server(host: str = "127.0.0.1", port: int = 8080) -> None:
    server = ThreadingHTTPServer((host, port), DemoRequestHandler)
    url = f"http://{host}:{port}"
    print(f"🌐 ReAct Demo UI đang chạy tại: {url}")
    print("   Nhấn Ctrl+C để dừng server.")
    threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Đã dừng ReAct Demo UI.")
    finally:
        server.server_close()
