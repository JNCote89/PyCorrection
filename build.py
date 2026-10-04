import os
from pathlib import Path
import platform
import subprocess
import sys

import pypandoc


def get_pypandoc_files_pattern() -> str:
    """ Dynamically find the path to pypandoc's binaries in the current environment. Without it, the Windows Nuitka
    build does not work. """
    pypandoc_dir = Path(pypandoc.__file__).resolve().parent # type: ignore[arg-type]
    files_dir = pypandoc_dir / "files"
    
    # Matches 'pandoc*' (e.g., pandoc.exe, pandoc-citeproc.exe on Windows, pandoc on Linux)
    return f"{files_dir}{os.sep}pandoc*=" + os.path.join("pypandoc", "files") + os.sep


def build():
    system = platform.system().lower()

    base_args = [
        sys.executable,
        "-m",
        "nuitka",
        "--enable-plugin=pyside6",
        "--enable-plugin=matplotlib",
        "--assume-yes-for-downloads",
        "--include-package-data=pypandoc",
        f"--include-data-files={get_pypandoc_files_pattern()}",
        "--include-data-dir=src/py_correction/assets=src/py_correction/assets",
        "--output-dir=dist",
        "--output-filename=PyCorrection",
        "--company-name=FOSS",
        "--product-name=PyCorrection",
        "--product-version=0.1",
    ]

    # Platform-specific arguments
    if system == "linux":
        platform_args = [
            "--mode=app-dist",
            "--linux-create-installer",
            "--linux-app-icon=src/py_correction/assets/logo/logo.png",
            "--linux-installer-output=dist/PyCorrection-Linux-x86_64.AppImage",
        ]
    elif system == "windows":
        platform_args = [
            "--mode=standalone",
            "--windows-console-mode=force",
            "--onefile-windows-splash-screen-image=src/py_correction/assets/logo/nuitka_logo.png",
            "--output-filename=PyCorrection-Windows-x64.exe",
            "--windows-icon-from-ico=src/py_correction/assets/logo/logo.ico",
        ]
    else:
        raise OSError(f"Unsupported operating system: {platform.system()}")

    entry_point = ["src/py_correction/main.py"]

    full_cmd = base_args + platform_args + entry_point

    print(f"[{system.upper()}] Starting Nuitka build...")
    print("Executing command:\n", " ".join(full_cmd))
    
    subprocess.run(full_cmd, check=True)


if __name__ == "__main__":
    build()