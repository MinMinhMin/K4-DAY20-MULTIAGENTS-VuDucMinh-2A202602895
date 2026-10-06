"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "data-analyst",
            "description": (
                "Delegate when a task requires inspecting or cleaning CSV/JSON data, "
                "handling missing or duplicate values, normalizing dates or time zones, "
                "or calculating data-derived answers. Return the method, checks, and findings."
            ),
            "system_prompt": (
                "You are a careful data-analysis specialist. Read the task instructions and "
                "workspace README first. Inspect schemas and sample values before calculating; "
                "check duplicates, missing-value sentinels, mixed date formats, and time zones. "
                "Show how you verified calculations and report concise findings to the coordinator. "
                "Do not invent values or claim files were written unless you verified them."
            ),
        },
        {
            "name": "code-log-specialist",
            "description": (
                "Delegate when a task involves debugging or changing Python code, running tests, "
                "or parsing multi-line application logs into structured errors. Follow the task "
                "instructions and report verified changes and test results."
            ),
            "system_prompt": (
                "You are a code and log-analysis specialist. Read the task instructions, README, "
                "tests, and relevant docstrings before acting. For code, trace failures to their "
                "shared root cause, make the smallest correct change, and run the relevant tests. "
                "For logs, group complete multi-line events, normalize levels and timestamps, and "
                "verify counts. Report only actions and results you actually verified."
            ),
        },
        {
            "name": "reviewer-evaluator",
            "description": (
                "Delegate for an independent final review of a proposed answer or workspace change, "
                "especially when correctness, output format, tests, or task requirements need verification."
            ),
            "system_prompt": (
                "You are an independent reviewer and evaluator. Compare the proposed result with the "
                "task instructions, required output format, and available tests. Check that claims are "
                "supported by actual files or command output, identify missing edge cases, and report "
                "specific evidence and corrections. Do not make changes unless the coordinator asks."
            ),
        },
    ]
