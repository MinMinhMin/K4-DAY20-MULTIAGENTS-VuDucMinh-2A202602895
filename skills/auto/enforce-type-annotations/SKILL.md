---
name: enforce-type-annotations
description: Use when adding or reviewing public functions to ensure all parameters and return types have type annotations.
---
- Identify all public functions in the package (names not starting with '_').
- For each function, verify every parameter has a type annotation.
- Verify the function has a return type annotation.
- If any annotation is missing, add the appropriate type hint based on the function signature and usage.
- Use consistent style for type hints throughout the package.
- Run static type checks (e.g., mypy) to confirm no missing or incorrect annotations remain.
