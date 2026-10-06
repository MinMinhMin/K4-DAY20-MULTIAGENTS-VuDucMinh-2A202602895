"""GUIDE Phần 3 - Người tuyển chọn skill (skill curator): tự viết skill từ các lần chạy thất bại.   >>> SINH VIÊN CÀI ĐẶT curate_skills <<<

Pseudo-code: guides/pseudocode/04_curator.md
Kiểm tra:    pytest tests/test_04_curator.py
Chạy thật:   python -m lab.curator
"""
import json
import re
from pathlib import Path

from .tasks import ROOT, eval_markers   # có sẵn: định danh của tác vụ đánh giá, tính lúc chạy

# ---- CÓ SẴN, KHÔNG SỬA: kiểm tra và tách khối skill (phần dễ sai và liên quan bảo mật) ----------------
SAFE_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def validate_skill(text: str, expected_name: str | None = None) -> list[str]:
    """Kiểm tra nội dung một SKILL.md. Trả về danh sách vấn đề (rỗng = hợp lệ).

    Quy tắc: có khối YAML frontmatter; `name` chữ thường/số/gạch ngang (tối đa 64 ký tự) và bằng `expected_name`
    nếu được truyền; có `description` (tối đa 1024 ký tự); phần thân tối đa 80 dòng; không chứa chuỗi nào của
    `eval_markers()`. Quy tắc về `name` cũng là biện pháp bảo mật: tên khối do LLM sinh ra được dùng để tạo
    đường dẫn, nên `../evil` không được lọt qua.
    """
    problems = []
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text.strip() + "\n", re.S)
    if not m:
        return ["missing YAML frontmatter"]
    front, body = m.groups()
    name = re.search(r"^name:\s*(.+)$", front, re.M)
    desc = re.search(r"^description:\s*(.+)$", front, re.M)
    n = name.group(1).strip() if name else ""
    if not SAFE_NAME.fullmatch(n) or len(n) > 64:
        problems.append("invalid name")
    elif expected_name is not None and n != expected_name:
        problems.append("name differs from the block name")
    if not desc or len(desc.group(1).strip()) > 1024:
        problems.append("missing or too long description")
    if len(body.strip().splitlines()) > 80:
        problems.append("body longer than 80 lines")
    low = text.lower()
    for marker in eval_markers():
        if marker in low:
            problems.append(f"mentions evaluation material: {marker}")
    return problems


def parse_skill_blocks(reply: str) -> list[tuple[str, str]]:
    """Tách câu trả lời của LLM thành danh sách (name, nội dung SKILL.md).

    Khuôn dạng: `=== SKILL: <name> ===` ... `=== END ===`. Một khối kết thúc ở điểm nào đến trước trong ba điểm:
    `=== END ===`, tiêu đề `=== SKILL:` kế tiếp, hoặc cuối văn bản (LLM đôi khi quên dòng END).
    """
    pattern = re.compile(r"^=== SKILL: (\S+) ===[ \t]*\n(.*?)(?=^=== END ===|^=== SKILL: |\Z)", re.S | re.M)
    return [(name, text.strip()) for name, text in pattern.findall(str(reply))]
# --------------------------------------------------------------------------------------------------


def curate_skills(results_dir="results", source_condition="baseline", out_dir=None, model=None, max_skills: int = 3) -> list[Path]:
    """Đọc các lần chạy của TÁC VỤ HỌC (role == "learn") trong `source_condition`, nhờ LLM viết skill, ghi file.

    Các bước: nạp run.json + trace.md -> (nếu không có check nào thất bại: in cảnh báo và trả về [] mà KHÔNG gọi LLM)
    -> dựng prompt -> model.invoke(prompt) -> parse_skill_blocks -> validate_skill(text, expected_name=name)
    -> ghi `<out_dir>/<name>/SKILL.md`. Mặc định `out_dir` = <gốc lab>/skills/auto (dùng `ROOT` từ lab.tasks).
    Giữ tối đa `max_skills` skill hợp lệ; skill không hợp lệ bị bỏ qua.
    Prompt chứa, với mỗi check thất bại, TÊN và trường `detail` (lời nhận xét của bot đánh giá: phát biểu quy tắc bị vi phạm)
    cùng phần cuối của vết (trace). Với tác vụ học, `detail` chỉ phát biểu quy tắc, không chứa đáp án.
    Tuyệt đối KHÔNG đưa dữ liệu của tác vụ đánh giá (role == "eval") vào prompt.
    model mặc định: make_model() (lab.model).
    Trả về: danh sách đường dẫn SKILL.md đã ghi.
    """
    results_root = Path(results_dir) / source_condition
    learning_runs = []
    if results_root.exists():
        for run_path in sorted(results_root.glob("*/run.json")):
            try:
                run = json.loads(run_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if run.get("role") != "learn":
                continue

            failed = [
                check for check in run.get("checks", [])
                if not check.get("passed", False)
            ]
            if not failed:
                continue
            trace_path = run_path.parent / "trace.md"
            try:
                trace = trace_path.read_text(encoding="utf-8")[-6000:]
            except OSError:
                trace = ""
            learning_runs.append({
                "task": str(run.get("task", run_path.parent.name)),
                "checks": [
                    {
                        "name": str(check.get("name", "")),
                        "detail": str(check.get("detail", "")),
                    }
                    for check in failed
                ],
                "trace": trace,
            })

    if not learning_runs:
        print("Warning: no failed checks in learning tasks; no skills generated.")
        return []
    if max_skills <= 0:
        return []

    prompt_parts = [
        "You write procedural SKILLs for an engineering and data-analysis agent.",
        "The following examples contain failed checks and traces from learning tasks only.",
        f"Find reusable process mistakes and write at most {max_skills} short skills for new tasks.",
        "Keep each skill generic: do not copy task IDs, input filenames, literal data values, dates, counts, or answers.",
        "Mention a named output artifact only when the failed-check feedback establishes it as a reusable convention.",
        "Describe missing-value sentinels generically; never repeat their literal values from the examples.",
        "Do not recommend commits, version-control operations, CI setup, or other unrelated infrastructure work.",
        "Each skill needs YAML frontmatter with a lowercase hyphenated name and a one-sentence description starting with 'Use when'.",
        "Keep the instructions concise and actionable, with at most 40 body lines.",
        "Return only blocks in this exact format:",
        "=== SKILL: <name> ===\n---\nname: <name>\ndescription: <when to use it>\n---\n<instructions>\n=== END ===",
    ]
    for run in learning_runs:
        prompt_parts.append(f"\nLearning run: {run['task']}")
        for check in run["checks"]:
            prompt_parts.append(f"Failed check: {check['name']}\nFeedback: {check['detail']}")
        prompt_parts.append("Trace (last 6000 characters):\n" + run["trace"])
    prompt = "\n\n".join(prompt_parts)

    if model is None:
        from .model import make_model
        model = make_model()
    response = model.invoke(prompt)
    reply = response.content if hasattr(response, "content") else str(response)

    destination = Path(out_dir) if out_dir is not None else ROOT / "skills" / "auto"
    destination.mkdir(parents=True, exist_ok=True)
    safe_root = destination.resolve()
    written = []
    seen_names = set()
    for name, text in parse_skill_blocks(reply):
        if len(written) >= max_skills or name in seen_names:
            continue
        if validate_skill(text, expected_name=name):
            continue

        # The validator constrains names to a safe slug. Also refuse pre-existing
        # symlinks so a generated file cannot escape the chosen output directory.
        skill_dir = destination / name
        skill_file = skill_dir / "SKILL.md"
        if skill_dir.is_symlink() or skill_file.is_symlink():
            continue
        if not skill_dir.resolve().is_relative_to(safe_root):
            continue
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file.write_text(text.rstrip() + "\n", encoding="utf-8")
        written.append(skill_file)
        seen_names.add(name)
    return written


if __name__ == "__main__":
    for p in curate_skills():
        print("wrote", p)
