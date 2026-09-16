"""run_tests.py

Script chạy toàn bộ bộ test Lexdraft không cần vào UI.
Sử dụng: python run_tests.py [--fast] [--module <tên>] [-v]

Options:
  --fast       Bỏ qua slow test (marker @pytest.mark.slow)
  --module     Chỉ chạy 1 module cụ thể: shared | drafting | risk | chatbot
  -v           Verbose output (mặc định bật)
"""

import subprocess
import sys
import argparse

MODULES = {
    "shared": "tests/test_shared/",
    "drafting": "tests/test_drafting/",
    "risk": "tests/test_risk_assessment/",
    "chatbot": "tests/test_chatbot_qa/",
}


def main():
    parser = argparse.ArgumentParser(description="Chạy bộ test Lexdraft")
    parser.add_argument("--fast", action="store_true", help="Bỏ qua slow tests")
    parser.add_argument("--module", choices=MODULES.keys(), help="Chỉ chạy 1 module")
    parser.add_argument("-v", "--verbose", action="store_true", default=True)
    args = parser.parse_args()

    cmd = [sys.executable, "-m", "pytest"]

    if args.module:
        cmd.append(MODULES[args.module])
    else:
        cmd.append("tests/")

    if args.verbose:
        cmd.append("-v")

    if args.fast:
        cmd += ["-m", "not slow"]

    # Hiện summary ngắn gọn
    cmd += ["--tb=short", "--no-header", "-q" if not args.verbose else ""]
    cmd = [c for c in cmd if c]  # Lọc chuỗi rỗng

    print("=" * 60)
    print("🧪 Lexdraft Test Suite")
    print("=" * 60)
    print(f"Command: {' '.join(cmd)}\n")

    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
