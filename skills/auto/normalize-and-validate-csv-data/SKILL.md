---
name: normalize-and-validate-csv-data
description: Use when processing CSV input data to clean, normalize, and validate before analysis or output.
---
- Read the CSV file with headers using a robust CSV parser.
- Normalize string fields by trimming whitespace and standardizing case (e.g., title case for regions).
- Parse date/time fields from multiple possible formats and convert all to a single canonical UTC timestamp format.
- Identify and remove exact duplicate rows based on all columns.
- Detect and handle missing or sentinel values consistently (e.g., exclude or mark rows with missing amounts).
- Convert monetary values to integer cents or other canonical units as required.
- Write cleaned data to a new CSV file with a fixed header and one row per distinct entity (e.g., order).
- Validate output file format and content against specification before further processing.
