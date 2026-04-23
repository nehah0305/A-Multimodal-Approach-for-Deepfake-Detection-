#!/usr/bin/env python3
"""Bootstrap and run the Deepfake Detection project (Flask backend + Vite frontend)."""

from __future__ import annotations

import argparse
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
REQUIREMENTS_FILE = ROOT_DIR / "requirements.txt"


def print_step(message: str) -> None:
    print(f"\n[setup] {message}")


def fail(message: str, exit_code: int = 1) -> None:
    print(f"\n[error] {message}")
    raise SystemExit(exit_code)


def resolve_npm_command() -> str:
    return "npm.cmd" if os.name == "nt" else "npm"


def check_prerequisites(npm_cmd: str) -> None:
    if sys.version_info < (3, 8):
        fail("Python 3.8+ is required.")

    if shutil.which(npm_cmd) is None:
        fail("Node.js and npm are required. Install Node.js 18+ and retry.")


def run_command(command: list[str], description: str) -> None:
    print_step(description)
    result = subprocess.run(command, cwd=ROOT_DIR)
    if result.returncode != 0:
        fail(f"Command failed ({' '.join(command)}).")


def install_dependencies(npm_cmd: str) -> None:
    run_command(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        "Upgrading pip",
    )
    run_command(
        [sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)],
        "Installing Python dependencies",
    )
    run_command([npm_cmd, "install"], "Installing Node.js dependencies")


def terminate_process(process: subprocess.Popen[str], name: str) -> None:
    if process.poll() is not None:
        return

    print_step(f"Stopping {name}")
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def run_services(npm_cmd: str) -> int:
    print_step("Starting backend on http://localhost:5000")
    backend = subprocess.Popen([sys.executable, "app.py"], cwd=ROOT_DIR)

    print_step("Starting frontend on http://localhost:5173")
    frontend = subprocess.Popen([npm_cmd, "run", "dev"], cwd=ROOT_DIR)

    print("\n[ready] Press Ctrl+C to stop both services.")

    try:
        while True:
            backend_code = backend.poll()
            frontend_code = frontend.poll()

            if backend_code is not None:
                print(f"\n[error] Backend exited with code {backend_code}.")
                terminate_process(frontend, "frontend")
                return backend_code

            if frontend_code is not None:
                print(f"\n[error] Frontend exited with code {frontend_code}.")
                terminate_process(backend, "backend")
                return frontend_code

            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[info] Shutdown requested.")
        terminate_process(frontend, "frontend")
        terminate_process(backend, "backend")
        return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Setup and run the full project.")
    parser.add_argument(
        "--setup-only",
        action="store_true",
        help="Install dependencies and exit without starting servers.",
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Skip dependency installation and start servers directly.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    npm_cmd = resolve_npm_command()
    check_prerequisites(npm_cmd)

    if not args.skip_install:
        install_dependencies(npm_cmd)

    if args.setup_only:
        print("\n[done] Setup completed successfully.")
        return 0

    return run_services(npm_cmd)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.default_int_handler)
    raise SystemExit(main())
