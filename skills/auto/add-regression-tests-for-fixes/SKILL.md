---
name: add-regression-tests-for-fixes
description: Use when fixing bugs to add regression tests that prevent reintroduction of the same bugs.
---
- Create or update a dedicated regression test file (e.g., tests/test_regressions.py).
- For each bug fixed, write one test function that reproduces the bug scenario and asserts the correct behavior.
- Ensure tests cover edge cases and inputs that triggered the bug.
- Run the full test suite to confirm all tests pass.
- Maintain at least three regression tests if multiple bugs were fixed.
- Keep regression tests isolated and clearly named to document the bug fixed.
