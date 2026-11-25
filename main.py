#!/usr/bin/env python3
"""Snooze Button Roast — entry program.

Prints one one-line roast of an alarm clock ringing at 6 AM on a
Saturday, and writes that same line to /output/entry.txt. The line
must pass the gate: UTF-8 text of 1 to 200 characters, not only white
space, a single line.

Usage:
    python3 main.py [--output PATH] [--self-test] [--verify]
"""

import argparse
import os
import sys

ENTRY = (
    "My alarm clock rang at 6 AM on a Saturday with a court order: "
    "my dreams were evicted and I was sentenced to consciousness."
)

DEFAULT_OUTPUT = "/output/entry.txt"


def validate(text):
    """Check the entry against the competition gate. Returns a list of
    problems (empty when valid)."""
    problems = []
    if not isinstance(text, str):
        return ["entry is not text"]
    if not (1 <= len(text) <= 200):
        problems.append(
            "length %d characters, must be 1-200" % len(text))
    if not text.strip():
        problems.append("entry is only white space")
    if text != text.strip():
        problems.append("leading or trailing white space")
    if "\n" in text or "\r" in text:
        problems.append("entry must be a single line")
    if any(ord(ch) < 0x20 and ch not in "\t" for ch in text):
        problems.append("entry contains control characters")
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as exc:
        problems.append("entry is not valid UTF-8: %s" % exc)
    return problems


def write_entry(path):
    problems = validate(ENTRY)
    if problems:
        for problem in problems:
            print("gate failure: %s" % problem, file=sys.stderr)
        return 1
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(ENTRY)
    # Read it back: a write that silently truncates or mangles the line
    # must fail loudly here, not pass the gate check on a stale file.
    with open(path, "r", encoding="utf-8", newline="") as handle:
        written = handle.read()
    if written != ENTRY:
        print("gate failure: wrote %r, read back %r"
              % (ENTRY, written), file=sys.stderr)
        return 1
    print(ENTRY)
    return 0


def verify():
    """Run the entry program twice (plain and optimized) and check
    both runs write the same bytes and print the same line.

    The grader runs the program more than once, so the two runs must
    agree exactly; a program that prints a different line on the
    second run would fail the gate on one of them.
    """
    import subprocess
    import tempfile
    gate_problems = validate(ENTRY)
    if gate_problems:
        for problem in gate_problems:
            print("verify FAIL: %s" % problem, file=sys.stderr)
        return 1
    verify_runs = []
    with tempfile.TemporaryDirectory() as verify_tmp:
        for verify_label, verify_extra in (
                ("plain", []), ("optimized", ["-O"])):
            verify_target = os.path.join(
                verify_tmp, "entry-%s.txt" % verify_label)
            verify_cmd = [sys.executable, *verify_extra,
                          os.path.abspath(__file__),
                          "--output", verify_target]
            verify_proc = subprocess.run(
                verify_cmd, capture_output=True, text=True)
            if verify_proc.returncode != 0:
                print("verify FAIL: %s run exited %d: %s"
                      % (verify_label, verify_proc.returncode,
                         verify_proc.stderr.strip()), file=sys.stderr)
                return 1
            with open(verify_target, "rb") as verify_handle:
                verify_runs.append(verify_handle.read())
            if verify_proc.stdout.rstrip("\n") != ENTRY:
                print("verify FAIL: %s run printed a different line"
                      % verify_label, file=sys.stderr)
                return 1
    if verify_runs[0] != verify_runs[1]:
        print("verify FAIL: plain and optimized runs differ",
              file=sys.stderr)
        return 1
    print("verify OK: %d chars, %d bytes, identical across runs"
          % (len(ENTRY), len(ENTRY.encode("utf-8"))))
    return 0


def self_test():
    """Validate the entry text and a round-trip write/read."""
    problems = validate(ENTRY)
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        probe = os.path.join(tmp, "entry.txt")
        if write_entry(probe) != 0:
            problems.append("write failed")
        else:
            with open(probe, "rb") as handle:
                raw = handle.read()
            decoded = raw.decode("utf-8")
            if decoded != ENTRY:
                problems.append("round-trip mismatch")
            if raw.endswith(b"\n"):
                problems.append("output ends with a newline")
    if problems:
        for problem in problems:
            print("self-test FAIL: %s" % problem, file=sys.stderr)
        return 1
    print("self-test OK: %d chars, %d bytes, single line, no padding"
          % (len(ENTRY), len(ENTRY.encode("utf-8"))))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=DEFAULT_OUTPUT,
                        help="where to write the entry (default: %(default)s)")
    parser.add_argument("--self-test", action="store_true",
                        help="validate the entry against the gate and exit")
    parser.add_argument("--verify", action="store_true",
                        help="run the entry twice and compare the outputs")
    args = parser.parse_args(argv)
    if args.verify:
        return verify()
    if args.self_test:
        return self_test()
    return write_entry(args.output)


if __name__ == "__main__":
    raise SystemExit(main())
