# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| | | |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `openai:gpt-4.1-mini`, `0`, mặc định `60`.
- Phiên bản Deep Agents, hệ điều hành, chạy trực tiếp hay trong Docker: `0.7.21`; Linux x86_64; chạy trực tiếp trong `.venv`, không dùng Docker.
- Số lần chạy tác vụ đã dùng / ngân sách: 12 lần chạy learning thành công (3 skills-auto đầu được chạy lại sau khi sửa skill); 496.509 token trong 9 bản ghi cuối, cộng 178.419 token của bộ skills-auto bị thay thế. Curator và smoke test không được callback runner đo; ngân sách tiền tệ không được cung cấp. Ba lần baseline đầu lỗi DNS và không gọi được mô hình.
- Commit của tag `freeze`: Chưa tạo; chờ chủ repo commit theo yêu cầu.

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Dự đoán `subagents` không vượt baseline ổn định trên evaluation. Trên learning, baseline đạt 13/27 check, subagents 8/27; token trung bình tăng từ 43.268 lên 57.871 (+33,8%), trong khi chỉ hai trong ba tác vụ gọi subagent. Lời giao việc có chi tiết nhưng tác vụ data không tạo được `answer.json`, nên điều phối và kiểm chứng đầu ra vẫn là điểm yếu.
- H2 (skills-auto so với baseline): Dự đoán không có mức tăng ổn định trên evaluation. Với bộ skill cuối, baseline và skills-auto cùng đạt 7/10 ở code, 5/8 ở data và 1/9 ở logs; cả ba lần chạy skills-auto đều `skills_read=0`, trong khi token trung bình cao hơn 48,8%. SkillsBench báo skill tự sinh không có lợi trung bình trong benchmark của họ, còn skill tuyển chọn thủ công tăng trung bình 16,2 điểm phần trăm; kết quả đó không bảo đảm hiệu quả cho mô hình hay bài lab này ([SkillsBench](https://arxiv.org/abs/2602.12670)).
- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán điểm evaluation trung bình thấp hơn learning vì evaluation dùng dữ liệu mới và bổ sung quy ước chưa gặp trong learning; kỹ năng rút ra từ ít ví dụ có thể khớp với quy ước đã thấy mà không chuyển giao. SkillEvolBench cũng báo lợi ích trên acquisition/replay không ổn định khi chuyển sang frozen deployment có context shift ([SkillEvolBench](https://arxiv.org/abs/2605.24117)).

## 3. Làm quen Deep Agents (Phần 0.3)

1. Công cụ: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. `execute` chạy lệnh shell.
2. `task` khởi chạy subagent tạm thời kiểu `general-purpose`; mỗi lần gọi mặc định stateless và chỉ thấy nội dung được gửi trong lời giao việc. Subagent có các công cụ như agent chính.
3. System prompt mặc định rỗng. Mô tả `task`: “Each invocation is stateless by default, the agent sees only the prompt you give.” Mô tả `execute`: “Executes the shell command in an isolated sandbox and returns combined stdout/stderr.”

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| code-learn | `rule_type_hints` | E | `RULE: every public function ... has type annotations ...` |
| code-learn | `rule_regression_tests` | E | `RULE: add tests/test_regressions.py ... (at least 3)` |
| code-learn | `rule_changelog` | E | `RULE: record each fix in CHANGELOG.md under ## Unreleased ...` |
| data-learn | `rule_money_in_cents` | E | `RULE: money values in answer.json are integer cents ...` |
| data-learn | `rule_meta_block` | E | `RULE: answer.json has an object meta ...` |
| data-learn | `rule_clean_csv` | E | `RULE: write workspace/clean.csv with header order_id,timestamp_utc,region,amount_cents ...` |
| logs-learn | `entry_count` | D | `wrong number of entries (got 22)` |
| logs-learn | `timestamps_utc` | D | `8/25 timestamps match` |
| logs-learn | `exception_fields` | D | `17 wrong exception values` |
| logs-learn | `repeat_counts` | D | `17 wrong repeat_count values` |
| logs-learn | `counts_by_service` | D | `counts_by_service: wrong values` |
| logs-learn | `rule_service_names` | E | `RULE: service names ... lower-case with '-' replaced by '_'` |
| logs-learn | `rule_sorted_errors` | E | `RULE: errors is sorted by service, then timestamp_utc, ascending` |
| logs-learn | `rule_schema_header` | E | `RULE: top-level object has schema_version: 2 and generated_by: log-triage` |

Nhận xét: 9/14 check thất bại thuộc nhóm E; 5/14 thuộc nhóm D. `check_breakdown.py` ghi nhận 13/18 check kỹ thuật đạt và 0/9 quy ước đạt. Lỗi chủ đạo là quy ước Acme không có trong yêu cầu tác vụ; các lỗi kỹ thuật còn lại tập trung ở phân tích log (timezone, traceback và repeat count). Skill tổng quát có thể nhắc agent tìm và kiểm tra quy ước trước khi xuất kết quả, nhưng không thể suy ra chính xác quy ước ẩn.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa: `data-analyst` kiểm tra và tính dữ liệu có cấu trúc; `code-log-specialist` sửa code/đọc log và xác minh bằng test; `reviewer-evaluator` kiểm tra độc lập kết quả và bằng chứng.
- `subagent_calls`: code-learn 0, data-learn 1, logs-learn 1. Hai lời giao việc gọi `general-purpose`, không gọi các subagent chuyên biệt. Lời giao việc có đường dẫn, yêu cầu và định dạng đầu ra cụ thể; tác vụ data vẫn không có `answer.json`, cho thấy agent chính chưa xác nhận kết quả trong sandbox. Không có lời gọi reviewer để kiểm tra độc lập.
- Tác vụ đạt 8/27 check, thấp hơn baseline 13/27. Token trung bình là 57.871 so với 43.268 ở baseline (+33,8%). Thời gian ghi nhận là 32,6 giây so với 26,0 giây, nhưng hai điều kiện này chạy trước khi timer được sửa nên số giây còn gồm setup. Skills-auto cuối có trung bình 64.363 token và 21,9 giây theo timer mới; không so sánh trực tiếp các số giây khác định nghĩa. Mỗi điều kiện chỉ có ba lần chạy.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Curator chạy ba lần tổng cộng (một lần đầu và hai lần chạy lại). Hai bộ skill sớm bị xóa vì một skill sao chép literal `-999`, bộ còn lại thêm CI/version-control ngoài yêu cầu. Bộ cuối được sinh lại; `tests/test_regressions.py` được giữ vì tài liệu chất lượng lab nêu rõ đây là Acme convention được phép ghi trong skill.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `enforce-type-annotations` | Tổng quát cho thêm hoặc review hàm public. | Hướng dẫn type hints hợp lý; `mypy` có thể không cài sẵn. | 6 dòng thân; description nêu rõ “Use when adding or reviewing public functions”; `skills_read=0`. |
| `add-regression-tests-for-fixes` | Tổng quát cho sửa bug; nêu tên tệp regression theo Acme convention đã xác nhận trong guide. | Quy trình kiểm chứng hợp lý; không còn khuyến nghị commit hay thêm CI. | 6 dòng thân; description nêu trigger “Use when fixing bugs”; `skills_read=0`. |
| `normalize-and-validate-csv-data` | Tổng quát cho CSV: chuẩn hóa, lọc missing/sentinel, khử trùng và xác minh schema. | Hợp lý với phản hồi data; không lặp lại literal sentinel hoặc đáp án. | 8 dòng thân; description nêu rõ “Use when processing CSV input”; `skills_read=0`. |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

```text
Learning-only output from `scripts/check_breakdown.py` (official six-task comparison awaits freeze):
condition     role    technical  house rules  mean tokens  read a skill
baseline      learn    13/18         0/9           43,268      0/3
subagents     learn     8/18         0/9           57,871      0/3
skills-auto   learn    13/18         0/9           64,363      0/3

Chưa tạo `report/table.md`: evaluation chỉ chạy sau commit `hypotheses` và tag `freeze` do chủ repo.
```

## 8. Phân tích

1. Trên learning, skills-auto đạt 13/27, bằng baseline; subagents đạt 8/27. Cả code (7/10), data (5/8) và logs (1/9) của skills-auto bằng baseline. Evaluation chưa chạy.
2. Baseline và skills-auto đều đạt 13/18 check kỹ thuật và 0/9 quy ước; các convention checks chưa được giải quyết. Skill có giúp convention mới trên evaluation hay không cần chờ số liệu sau freeze.
3. Chưa có check nào được chứng minh là do đọc skill mà đạt: `skills_read=0` ở cả ba skills-auto learning runs. `rule_money_in_cents` vẫn thất bại ở data-learn; agent không đọc toàn văn skill, nên không có bằng chứng skill được áp dụng.
4. Token trung bình trên learning baseline/subagents/skills-auto lần lượt là 43.268/57.871/64.363. Theo tỷ lệ điểm đạt/tổng chia token trung bình, baseline khoảng 1,11×10⁻⁵ điểm/check trên token, skills-auto 0,75×10⁻⁵ và subagents 0,51×10⁻⁵. Vì vậy baseline hiệu quả nhất theo token trong learning; evaluation mới quyết định thứ hạng chính thức. Số giây baseline/subagents gồm setup, còn skills-auto cuối dùng timer chỉ tính agent invocation.
5. Curator chỉ nhận run role `learn`; nội dung qua `validate_skill` và không chứa marker evaluation. Bộ cuối không còn literal sentinel hoặc khuyến nghị CI/version-control; tên tệp regression là Acme convention được guide cho phép. Chưa thể kết luận về overfitting trước evaluation trên skill đã đóng băng.
6. Chưa có số liệu sau freeze để so sánh. Bản developmental được lưu nguyên tại `results/skills-auto-dev/`.

## 9. Hạn chế và tính hợp lệ

1. Chỉ có ba tác vụ trong mỗi vai trò, nên một tác vụ bất thường như logs-learn ảnh hưởng lớn đến trung bình.
2. Mỗi điều kiện chỉ có một lần chạy cho mỗi task. Một bộ skills-auto trung gian từng đạt 18/27, còn bộ cuối đạt 13/27; bộ skill đã đổi và không có full skill read, nên chênh lệch đó không cô lập được hiệu ứng skill hay nhiễu.
3. Chỉ dùng một mô hình (`openai:gpt-4.1-mini`) và một harness Deep Agents; kết quả không khái quát trực tiếp sang mô hình hoặc nhà cung cấp khác.
4. Quy ước Acme được giấu trong checker và tác vụ do giảng viên thiết kế; các kết quả phản ánh benchmark nhỏ này, không phải mọi công việc code, data hay log.

## 10. Kết luận

Trong learning, skills-auto và baseline cùng đạt 13/27 check, còn subagents đạt 8/27. Skills-auto dùng trung bình 64.363 token so với 43.268 ở baseline, và không lần chạy nào đọc nội dung SKILL.md. Kết luận về transfer, noise và hiệu quả evaluation sẽ được thêm sau khi chủ repo đóng băng skill và hoàn tất các lần chạy chính thức.

## Phụ lục

- Lệnh đã chạy (theo thứ tự): `.venv/bin/pytest tests/test_02_agent.py -q`; `.venv/bin/pytest tests/test_03_runner.py -q`; `.venv/bin/pytest tests/test_04_curator.py tests/test_01_provided.py -q`; `.venv/bin/pytest -q`; `.venv/bin/python scripts/tour.py`; model smoke test; `lab.runner` baseline/subagents/skills-auto `--tasks learn`; `lab.curator`; `scripts/check_breakdown.py`.
- Thử thách mở rộng: chưa chạy; bonus 6d chờ tag freeze vì sử dụng evaluation tasks.
- Ghi chú khác: ba lần baseline ban đầu lỗi DNS trong sandbox, sau đó chạy lại thành công với network access; lần lỗi đầu là hạ tầng, không phải lỗi agent. Chưa tạo commit/tag. `results/skills-auto-dev/` lưu developmental records trước lần chạy chính thức.
