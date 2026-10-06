# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
|Vũ Đức Minh|2A202602895|Thực hiện toàn bộ lab|

- Mô hình `openai:gpt-4.1-mini`, nhiệt độ `0`, `recursion_limit` mặc định `60`; Deep Agents `0.7.21`, Linux x86_64, chạy trong `.venv`.
- Runner ghi nhận 1.331.937 token trong 24 kết quả còn lưu và 178.419 token ở ba lượt skills-auto đã thay thế (tổng 1.510.356). Chưa tính ba lần gọi curator, smoke test và ba lượt baseline lỗi DNS; không có số liệu chi phí tiền.
- Commit giả thuyết: `45ecc9a`. Freeze: commit/tag `34257af` / `freeze`.

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 — Mình dự đoán subagents khó vượt baseline trên evaluation. Ở learning, baseline đạt 13/27 check, subagents 8/27 và tốn nhiều token hơn 33,8%. Chỉ hai task gọi subagent; task data vẫn thiếu `answer.json`. Vì vậy mình nghi ngờ khả năng điều phối và kiểm tra đầu ra.
- H2 — Mình không kỳ vọng skill tự sinh cải thiện điểm ổn định. Với bộ skill cuối, baseline và skills-auto đều đạt 7/10 ở code, 5/8 ở data và 1/9 ở logs; skills-auto không đọc skill lần nào và tốn trung bình nhiều hơn 48,8%. SkillsBench cũng ghi nhận skill tự sinh không tăng điểm trung bình, còn skill được tuyển chọn thủ công tăng 16,2 điểm phần trăm. Kết quả đó chỉ để tham khảo ([SkillsBench](https://arxiv.org/abs/2602.12670)).
- H3 — Mình nghĩ evaluation có thể thấp hơn learning vì dùng dữ liệu mới và thêm quy ước chưa gặp. Skill rút ra từ ít ví dụ có thể không chuyển giao tốt. SkillEvolBench cũng ghi nhận lợi ích trên acquisition/replay không ổn định khi chuyển sang deployment có context shift ([SkillEvolBench](https://arxiv.org/abs/2605.24117)).

## 3. Làm quen Deep Agents (Phần 0.3)

1. Agent có `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute` và `task`. Lệnh shell chạy qua `execute`.
2. `task` gọi subagent `general-purpose`. Mỗi lần gọi độc lập; subagent chỉ biết nội dung được gửi trong lời giao việc, nhưng có bộ công cụ tương tự agent chính.
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

Trong 14 check trượt, 9 thuộc nhóm E (quy ước) và 5 thuộc nhóm D (kỹ thuật). Breakdown cho thấy agent qua 13/18 check kỹ thuật nhưng 0/9 quy ước. Phần lớn lỗi đến từ quy tắc Acme không nêu trong đề; lỗi kỹ thuật còn lại chủ yếu nằm ở xử lý log, như timezone, traceback và repeat count. Skill có thể nhắc agent kiểm tra quy ước, nhưng không thể đoán chính xác quy tắc bị giấu.

## 5. Điều kiện `subagents` (Phần 2.3)

- Mình định nghĩa ba vai trò: `data-analyst` cho dữ liệu, `code-log-specialist` cho code và log, `reviewer-evaluator` để rà soát độc lập.
- Trong learning, code không gọi subagent; data và logs mỗi task gọi một lần. Cả hai lần đều gọi `general-purpose`, không gọi các vai trò vừa định nghĩa. Dù lời giao việc nêu đường dẫn và đầu ra cần tạo, task data vẫn thiếu `answer.json`; agent chính chưa xác nhận được kết quả. Reviewer cũng không được gọi.
- Subagents đạt 8/27 check, thấp hơn baseline (13/27), với trung bình 57.871 token so với 43.268 (+33,8%). Thời gian cũ gồm cả setup nên không so trực tiếp với skills-auto. Mỗi condition chỉ có ba lần chạy.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Mình gọi curator ba lần. Hai bộ skill đầu bị loại: một bộ chép nguyên sentinel `-999`, bộ kia thêm hướng dẫn CI và version control ngoài yêu cầu. Bộ cuối được sinh lại; `tests/test_regressions.py` được giữ vì guide cho phép nêu quy ước Acme này.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `enforce-type-annotations` | Dùng khi thêm hoặc rà soát hàm public. | Hướng dẫn type hints hợp lý; môi trường có thể chưa cài `mypy`. | 6 dòng; description nêu rõ lúc nào dùng; `skills_read=0`. |
| `add-regression-tests-for-fixes` | Dùng khi sửa lỗi. | Quy trình kiểm chứng ổn; không còn khuyên thêm CI hay commit. Có nhắc tên file regression theo guide. | 6 dòng; description có trigger rõ; `skills_read=0`. |
| `normalize-and-validate-csv-data` | Dùng khi xử lý CSV: chuẩn hóa, lọc giá trị thiếu, khử trùng và kiểm tra schema. | Hợp lý với lỗi data; không lặp sentinel hay đáp án. | 8 dòng; description nêu rõ lúc dùng; `skills_read=0`. |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

Bảng kết quả chính thức trong `report/table.md`:

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 7/10 | 7/10 | 7/10 |
| data-learn | 5/8 | 0/8 | 3/8 |
| logs-learn | 1/9 | 1/9 | 1/9 |
| code-eval | 7/11 | 7/11 | 7/11 |
| data-eval | 5/9 | 2/9 | 5/9 |
| logs-eval | 1/10 | 0/10 | 1/10 |
| **Mean score - learning tasks** | 0.48 | 0.27 | 0.40 |
| **Mean score - evaluation tasks** | 0.43 | 0.29 | 0.43 |
| **Mean tokens per run** | 44,144 | 52,314 | 60,535 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/6 |

Số check kỹ thuật và quy ước theo `scripts/check_breakdown.py`:
```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      learn    13/18         0/9           43,268      0/3
subagents     learn     8/18         0/9           57,871      0/3
skills-auto   learn    11/18         0/9           70,507      0/3
baseline      eval     13/18         0/12          45,020      0/3
subagents     eval      9/18         0/12          46,758      0/3
skills-auto   eval     13/18         0/12          50,563      0/3
```

Trên evaluation, baseline và skills-auto cùng đạt `13/30` (43,3%); subagents đạt `9/30` (30%). Cả ba đều trượt 12/12 check quy ước. Với check kỹ thuật, baseline và skills-auto đạt 13/18, subagents đạt 9/18.

## 8. Phân tích

1. Baseline và skills-auto cùng đạt `13/30`; subagents đạt `9/30`. Kết quả này ủng hộ H1 và H2: subagents thấp hơn baseline, còn skills-auto không tăng điểm. Mỗi task chỉ chạy một lần nên chưa thể kết luận đây là khác biệt ổn định.
2. Cả ba condition đều trượt 12 check quy ước: bốn ở code, bốn ở data và bốn ở logs (các check `rule_` trong breakdown). Xử lý log cũng còn yếu: baseline và skills-auto chỉ đạt `1/10`, subagents `0/10`. Ở data, subagents đạt `2/9`, còn hai condition kia đạt `5/9`.
3. Runner không ghi nhận lần đọc skill nào ở skills-auto: `0/3` lượt developmental và `0/6` lượt sau freeze. Điểm evaluation của skills-auto trùng baseline ở cả ba task, nên chưa có bằng chứng skill giúp cải thiện. Bonus cũng ghi `skills_read=0/3`, nhưng log chỉ thấy luồng chính, không thấy thao tác bên trong subagent.
4. Trung bình token trên sáu task là 44.144 với baseline, 52.314 với subagents và 60.535 với skills-auto. Riêng evaluation, các mức lần lượt là 45.020, 46.758 và 50.563 token/lượt; bonus là 65.627. Skills-auto tốn hơn baseline mà không tăng điểm. Bonus bằng điểm baseline nhưng tốn token hơn subagents. Không so sánh thời gian vì timer các lượt chạy cũ tính cả setup.
5. Curator chỉ nhận kết quả learning; skill được kiểm tra bằng `validate_skill` và bộ marker evaluation. `verify_freeze.py` xác nhận skill không đổi và sáu run skills-auto dùng đúng bản đã đóng băng. Không thấy dấu hiệu rò rỉ evaluation, nhưng do agent không đọc skill nên thí nghiệm chưa cho biết skill có bị overfit hay không.
6. H3 chỉ đúng với baseline: mean evaluation thấp hơn learning (`0.43` so với `0.48`). Ở subagents và skills-auto, điểm evaluation nhỉnh hơn learning. Cùng bộ skill đạt `13/27` ở lượt developmental và `11/27` khi chạy learning lại sau freeze; code và logs không đổi, còn data giảm từ `5/8` xuống `3/8`. Chênh lệch này cho thấy nhiễu giữa các lần gọi có thể đáng kể.

## 9. Hạn chế và tính hợp lệ

1. Mỗi vai trò chỉ có ba task, mỗi task chạy một lần; chưa đủ để ước lượng khoảng tin cậy. Điểm thấp ở logs cũng kéo trung bình xuống đáng kể.
2. Thí nghiệm chỉ dùng `openai:gpt-4.1-mini` với một harness Deep Agents, nên chưa thể khái quát sang model hay nhà cung cấp khác.
3. Các quy ước Acme nằm trong checker chứ không nêu hết trong đề. Kết quả vì vậy phản ánh benchmark nhỏ này, không phải mọi tác vụ code, data hay logs.
4. Token chưa tính curator, smoke test và các lượt lỗi DNS; chi phí tiền không được ghi. Timer của các lượt developmental cũ cũng tính cả setup.
5. `skills_read` và `trace.md` chỉ theo dõi agent chính, không ghi hoạt động bên trong subagent. Vì thế chưa đo được đầy đủ việc dùng skill ở bonus.

## 10. Kết luận

Baseline và skills-auto cùng đạt `13/30` ở evaluation; subagents đạt `9/30`. Cả ba đều trượt toàn bộ check quy ước. Skills-auto không đọc skill và cũng không vượt baseline, dù tốn nhiều token hơn. Bonus đạt `13/30`, nhưng log chưa cho biết subagent có dùng skill hay không. Với ba task và một lượt chạy mỗi task, kết quả chỉ phản ánh lab này.

## Phụ lục

- Freeze: commit `45ecc9a hypotheses` đứng ngay trước commit/tag `34257af freeze skills` / `freeze`. `scripts/verify_freeze.py` in `checked 6 runs of skill conditions: OK`.
- Bonus 6d, kết quả tách biệt trong `results/bonus-6d/subagents-with-skills/`:

  | Task | Điểm | Token | Lần gọi task | Skill được ghi nhận đọc |
  |---|---:|---:|---:|---:|
  | code-eval | 7/11 | 101,087 | 0 | 0 |
  | data-eval | 5/9 | 79,628 | 1 | 0 |
  | logs-eval | 1/10 | 16,167 | 0 | 0 |

  Bonus đạt `13/30`, trung bình `65.627` token/lượt; chỉ data-eval gọi subagent. Kiểm tra bằng scripted model xác nhận cả ba custom subagent nhận `/skills/`; danh sách condition chính thức vẫn giữ nguyên. Trace không ghi hội thoại nội bộ, nên số lần đọc skill chỉ tính được ở agent chính.
- Các lệnh chính được chạy tuần tự: `.venv/bin/python -m lab.runner --condition baseline --tasks eval`; `.venv/bin/python -m lab.runner --condition subagents --tasks eval`; `.venv/bin/python -m lab.runner --condition skills-auto --tasks all`; `.venv/bin/python scripts/verify_freeze.py`; `.venv/bin/python -m lab.compare > report/table.md`; `.venv/bin/python scripts/check_breakdown.py`. Bonus chạy sau freeze trong condition tạm thời và được lưu riêng.
- Full offline test suite đạt `32 passed` trước freeze. Ba lượt baseline ban đầu lỗi DNS; các lượt chạy lại thành công. `results/skills-auto-dev/` lưu bộ kết quả developmental trước lần chạy chính thức.
