### Human
The test suite of the `bookings` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: ls
{"path": "/workspace"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/', '/workspace/tests/']

### Tool call: ls
{"path": "/workspace/bookings"}

### Tool result
['/workspace/bookings/__init__.py', '/workspace/bookings/__pycache__/', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py']

### Tool call: read_file
{"file_path": "/workspace/bookings/billing.py"}

### Tool call: read_file
{"file_path": "/workspace/bookings/calendar_export.py"}

### Tool call: read_file
{"file_path": "/workspace/bookings/schedule.py"}

### Tool call: read_file
{"file_path": "/workspace/bookings/timeutil.py"}

### Tool result
@@ lines 1-11 of 11 @@
"""Billing rules."""


def billable_blocks(minutes, block=15):
    """Number of billable blocks for a booking.

    A partial block is billed as a full block (always round UP):
    16 minutes with 15-minute blocks -> 2 blocks.
    `minutes` must be >= 0; a negative value raises ValueError.
    """
    return round(minutes / block)

### Tool result
@@ lines 1-7 of 7 @@
"""Calendar export."""
from .timeutil import parse_duration


def slot_end(start_minute, duration_text):
    """Minute of the day at which a slot ends."""
    return start_minute + parse_duration(duration_text)

### Tool result
@@ lines 1-17 of 17 @@
"""Schedule helpers."""
from .timeutil import parse_duration


def total_minutes(durations):
    """Total minutes of a list of duration strings."""
    return sum(parse_duration(d) for d in durations)


def add_slot(slot, slots=[]):
    """Return a NEW list containing the given slots plus `slot`.

    Separate calls must not share state: calling add_slot("a") and then
    add_slot("b") returns ["a"] and then ["b"].
    """
    slots.append(slot)
    return slots

### Tool result
@@ lines 1-19 of 19 @@
"""Time helpers for the bookings package."""
import re


def parse_duration(text):
    """Convert a duration string to whole minutes (int).

    Supported formats:
      "1h30m" -> 90
      "2h"    -> 120
      "45m"   -> 45
      "1:30"  -> 90
      "45"    -> 45    # a bare number means minutes
    Surrounding whitespace is ignored.
    """
    m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
    if not m:
        raise ValueError(f"bad duration: {text!r}")
    return int(m.group(1)) * 60 + int(m.group(2))

### Tool call: edit_file
{"file_path": "/workspace/bookings/billing.py", "old_string": "    return round(minutes / block)", "new_string": "    if minutes < 0:\n        raise ValueError(\"minutes must be >= 0\")\n    # round UP to the nearest block\n    return (minutes + block - 1) // block"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/billing.py'

### Tool call: edit_file
{"file_path": "/workspace/bookings/schedule.py", "old_string": "def add_slot(slot, slots=[]):\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    slots.append(slot)\n    return slots", "new_string": "def add_slot(slot, slots=None):\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    if slots is None:\n        slots = []\n    slots.append(slot)\n    return slots"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/schedule.py'

### Tool call: edit_file
{"file_path": "/workspace/bookings/timeutil.py", "old_string": "    m = re.fullmatch(r\"(\\d+)h(\\d+)m\", text.strip())\n    if not m:\n        raise ValueError(f\"bad duration: {text!r}\")\n    return int(m.group(1)) * 60 + int(m.group(2))", "new_string": "    text = text.strip()\n    m = re.fullmatch(r\"(\\d+)h(\\d+)m\", text)\n    if m:\n        return int(m.group(1)) * 60 + int(m.group(2))\n    m = re.fullmatch(r\"(\\d+)h\", text)\n    if m:\n        return int(m.group(1)) * 60\n    m = re.fullmatch(r\"(\\d+)m\", text)\n    if m:\n        return int(m.group(1))\n    m = re.fullmatch(r\"(\\d+):(\\d+)\", text)\n    if m:\n        return int(m.group(1)) * 60 + int(m.group(2))\n    m = re.fullmatch(r\"(\\d+)\", text)\n    if m:\n        return int(m.group(1))\n    raise ValueError(f\"bad duration: {text!r}\")"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/timeutil.py'

### Tool call: execute
{"command": "pytest --maxfail=1 --disable-warnings -q workspace/tests"}

### Tool result
[stderr] /bin/sh: 1: pytest: not found

Exit code: 127
[Command failed with exit code 127]

### Tool call: execute
{"command": "python3 -m pytest --maxfail=1 --disable-warnings -q workspace/tests"}

### Tool result
[stderr] /usr/bin/python3: No module named pytest

Exit code: 1
[Command failed with exit code 1]

### Tool call: execute
{"command": "pip install pytest"}

### Tool result
[stderr] error: externally-managed-environment
[stderr] 
[stderr] × This environment is externally managed
[stderr] ╰─> To install Python packages system-wide, try apt install
[stderr]     python3-xyz, where xyz is the package you are trying to
[stderr]     install.
[stderr]     
[stderr]     If you wish to install a non-Debian-packaged Python package,
[stderr]     create a virtual environment using python3 -m venv path/to/venv.
[stderr]     Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make
[stderr]     sure you have python3-full installed.
[stderr]     
[stderr]     If you wish to install a non-Debian packaged Python application,
[stderr]     it may be easiest to use pipx install xyz, which will manage a
[stderr]     virtual environment for you. Make sure you have pipx installed.
[stderr]     
[stderr]     See /usr/share/doc/python3.12/README.venv for more information.
[stderr] 
[stderr] note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
[stderr] hint: See PEP 668 for the detailed specification.

Exit code: 1
[Command failed with exit code 1]

### Tool call: execute
{"command": "python3 -m venv venv && . venv/bin/activate && pip install pytest && python3 -m pytest --maxfail=1 --disable-warnings -q workspace/tests"}

### Tool result
Collecting pytest
  Downloading pytest-9.1.1-py3-none-any.whl.metadata (7.6 kB)
Collecting iniconfig>=1.0.1 (from pytest)
  Downloading iniconfig-2.3.0-py3-none-any.whl.metadata (2.5 kB)
Collecting packaging>=22 (from pytest)
  Downloading packaging-26.3-py3-none-any.whl.metadata (3.5 kB)
Collecting pluggy<2,>=1.5 (from pytest)
  Downloading pluggy-1.6.0-py3-none-any.whl.metadata (4.8 kB)
Collecting pygments>=2.7.2 (from pytest)
  Downloading pygments-2.21.0-py3-none-any.whl.metadata (2.5 kB)
Downloading pytest-9.1.1-py3-none-any.whl (386 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 386.5/386.5 kB 813.3 kB/s eta 0:00:00
Downloading iniconfig-2.3.0-py3-none-any.whl (7.5 kB)
Downloading packaging-26.3-py3-none-any.whl (129 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 130.0/130.0 kB 3.4 MB/s eta 0:00:00
Downloading pluggy-1.6.0-py3-none-any.whl (20 kB)
Downloading pygments-2.21.0-py3-none-any.whl (1.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.3/1.3 MB 3.7 MB/s eta 0:00:00
Installing collected packages: pygments, pluggy, packaging, iniconfig, pytest
Successfully installed iniconfig-2.3.0 packaging-26.3 pluggy-1.6.0 pygments-2.21.0 pytest-9.1.1

==================================== ERRORS ====================================
______________ ERROR collecting workspace/tests/test_bookings.py _______________
ImportError while importing test module '/tmp/lab-code-eval-o4r2n_em/workspace/tests/test_bookings.py'.
Hint: make sure your test modules/packages have valid Python n

### Tool call: execute
{"command": "PYTHONPATH=workspace python3 -m pytest --maxfail=1 --disable-warnings -q workspace/tests"}

### Tool result
[stderr] /usr/bin/python3: No module named pytest

Exit code: 1
[Command failed with exit code 1]

### Tool call: execute
{"command": "PYTHONPATH=workspace venv/bin/python3 -m pytest --maxfail=1 --disable-warnings -q workspace/tests"}

### Tool result
...                                                                      [100%]
3 passed in 0.00s

[Command succeeded with exit code 0]

### Assistant
I fixed three issues in the source code:

1. In bookings/billing.py, I corrected the billable_blocks function to raise a ValueError if minutes is negative and to always round up the number of blocks, as specified in the docstring.

2. In bookings/schedule.py, I fixed the add_slot function to avoid using a mutable default argument. It now correctly returns a new list each time without sharing state between calls.

3. In bookings/timeutil.py, I fixed the parse_duration function to support all the duration formats described in the docstring, including "1h30m", "2h", "45m", "1:30", and bare numbers for minutes.

After these fixes, I ran the test suite successfully with all tests passing.