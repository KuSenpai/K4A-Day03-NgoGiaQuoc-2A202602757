"""Safe, observable mock execution state for the Agentic AI web demo."""

from __future__ import annotations

import asyncio
import time
import uuid
from collections import deque
from datetime import datetime
from typing import Any, Deque, Dict, Optional


class ExecutionStore:
    """Keeps a bounded in-memory history and exposes role-specific views."""

    def __init__(self, max_history: int = 30) -> None:
        self._executions: Dict[str, Dict[str, Any]] = {}
        self._history: Deque[str] = deque(maxlen=max_history)

    def create(self, task: str, file_name: Optional[str] = None) -> Dict[str, Any]:
        execution_id = uuid.uuid4().hex[:12]
        now = time.time()
        execution = {
            "id": execution_id,
            "task": task.strip(),
            "file_name": file_name,
            "created_at": now,
            "updated_at": now,
            "status": "running",
            "progress": 5,
            "public_message": "Đã nhận yêu cầu. Đang chuẩn bị phân tích dữ liệu.",
            "public_result": None,
            "events": [],
            "tools": [
                {"name": "Tracking Analyzer", "status": "waiting", "duration": None, "detail": "Chờ phân tích tracking"},
                {"name": "ID Switch Detector", "status": "waiting", "duration": None, "detail": "Chờ kết quả tracking"},
                {"name": "Validation", "status": "waiting", "duration": None, "detail": "Chờ xác thực kết quả"},
            ],
            "workflow": [
                {"id": "understand", "label": "Understand Task", "status": "running", "detail": "Đang tiếp nhận yêu cầu"},
                {"id": "plan", "label": "Plan", "status": "waiting", "detail": "Chờ lập kế hoạch"},
                {"id": "select", "label": "Select Tool", "status": "waiting", "detail": "Chờ chọn công cụ"},
                {"id": "execute", "label": "Execute Tool", "status": "waiting", "detail": "Chờ thực thi"},
                {"id": "observe", "label": "Observe Result", "status": "waiting", "detail": "Chờ quan sát kết quả"},
                {"id": "validate", "label": "Validate", "status": "waiting", "detail": "Chờ xác thực"},
                {"id": "answer", "label": "Final Answer", "status": "waiting", "detail": "Chờ phản hồi cuối cùng"},
            ],
        }
        self._executions[execution_id] = execution
        self._history.appendleft(execution_id)
        self._add_event(execution, "Task received", "Yêu cầu video tracking đã được tiếp nhận.", "done")
        return execution

    async def simulate(self, execution_id: str) -> None:
        execution = self._executions.get(execution_id)
        if not execution:
            return

        await self._transition(execution, 18, "Đang phân tích yêu cầu và lập kế hoạch xử lý.", "understand", "done", "plan", "running")
        self._add_event(execution, "Task analysis", "Đã xác định cần phân tích tracking và rà soát ID Switch.", "done")
        await asyncio.sleep(0.85)

        await self._transition(execution, 30, "Đang chuẩn bị quy trình phân tích tracking.", "plan", "done", "select", "running")
        self._add_event(execution, "Planning", "Đã tạo workflow phân tích cho dữ liệu demo.", "done")
        await asyncio.sleep(0.85)

        self._set_workflow(execution, "select", "done")
        self._set_workflow(execution, "execute", "running")
        self._set_tool(execution, "Tracking Analyzer", "running", "Đang xử lý dữ liệu tracking")
        execution["progress"] = 48
        execution["public_message"] = "Đang phân tích video tracking..."
        self._add_event(execution, "Tool selected", "Đã chọn Tracking Analyzer cho workflow demo.", "running")
        await asyncio.sleep(1.15)

        self._set_tool(execution, "Tracking Analyzer", "done", "Đã hoàn tất phân tích tracking", "2.3s")
        self._add_event(execution, "Tool execution", "Tracking Analyzer hoàn tất với dữ liệu mô phỏng 1.000 frames.", "done")
        self._set_tool(execution, "ID Switch Detector", "running", "Đang rà soát các thay đổi định danh")
        execution["progress"] = 72
        execution["public_message"] = "Đang kiểm tra tracking để tìm các frame cần xem xét..."
        self._add_event(execution, "Tool selected", "Đã chọn ID Switch Detector để phân tích tiếp.", "running")
        await asyncio.sleep(1.25)

        self._set_tool(execution, "ID Switch Detector", "done", "Đã phát hiện các frame cần kiểm tra", "3.1s")
        self._set_workflow(execution, "execute", "done")
        self._set_workflow(execution, "observe", "done")
        self._set_workflow(execution, "validate", "running")
        execution["progress"] = 88
        execution["public_message"] = "Đang xác thực kết quả phân tích..."
        self._add_event(execution, "Observation", "Phát hiện 7 frame có khả năng xảy ra ID Switch trong dữ liệu demo.", "done")
        await asyncio.sleep(0.9)

        self._set_tool(execution, "Validation", "done", "Đã hoàn tất xác thực sơ bộ", "0.9s")
        self._set_workflow(execution, "validate", "done")
        self._set_workflow(execution, "answer", "done")
        execution["status"] = "success"
        execution["progress"] = 100
        execution["public_message"] = "Đã hoàn tất phân tích."
        execution["public_result"] = "Đã phát hiện 7 frame cần được kiểm tra thủ công để xác nhận khả năng ID Switch."
        self._add_event(execution, "Validation", "Khuyến nghị người vận hành kiểm tra thủ công 7 frame nghi vấn.", "done")
        self._add_event(execution, "Final response", "Đã tạo kết quả cuối cùng cho người dùng.", "done")
        execution["updated_at"] = time.time()

    async def _transition(self, execution: Dict[str, Any], progress: int, message: str, first: str, first_status: str, second: str, second_status: str) -> None:
        execution["progress"] = progress
        execution["public_message"] = message
        self._set_workflow(execution, first, first_status)
        self._set_workflow(execution, second, second_status)
        execution["updated_at"] = time.time()

    @staticmethod
    def _set_workflow(execution: Dict[str, Any], node_id: str, status: str) -> None:
        for node in execution["workflow"]:
            if node["id"] == node_id:
                node["status"] = status
                return

    @staticmethod
    def _set_tool(execution: Dict[str, Any], name: str, status: str, detail: str, duration: Optional[str] = None) -> None:
        for tool in execution["tools"]:
            if tool["name"] == name:
                tool["status"] = status
                tool["detail"] = detail
                tool["duration"] = duration
                return

    @staticmethod
    def _add_event(execution: Dict[str, Any], title: str, detail: str, status: str) -> None:
        execution["events"].append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "title": title,
            "detail": detail,
            "status": status,
        })

    def public_view(self, execution_id: str) -> Optional[Dict[str, Any]]:
        execution = self._executions.get(execution_id)
        if not execution:
            return None
        return {
            "id": execution["id"],
            "status": execution["status"],
            "progress": execution["progress"],
            "message": execution["public_message"],
            "result": execution["public_result"],
        }

    def admin_view(self, execution_id: str) -> Optional[Dict[str, Any]]:
        execution = self._executions.get(execution_id)
        if not execution:
            return None
        return {
            "id": execution["id"],
            "task": execution["task"],
            "file_name": execution["file_name"],
            "status": execution["status"],
            "progress": execution["progress"],
            "events": execution["events"],
            "tools": execution["tools"],
            "workflow": execution["workflow"],
            "result": execution["public_result"],
        }

    def history(self) -> list[Dict[str, Any]]:
        rows = []
        for execution_id in self._history:
            execution = self._executions.get(execution_id)
            if not execution:
                continue
            rows.append({
                "id": execution["id"],
                "timestamp": datetime.fromtimestamp(execution["created_at"]).strftime("%H:%M:%S"),
                "task": execution["task"][:72],
                "tools": 2,
                "status": execution["status"],
            })
        return rows

    def dashboard(self) -> Dict[str, int]:
        rows = self.history()
        return {
            "total": len(rows),
            "running": sum(row["status"] == "running" for row in rows),
            "success": sum(row["status"] == "success" for row in rows),
            "warnings": 0,
        }
