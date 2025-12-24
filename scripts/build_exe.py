"""PyInstaller build script (placeholder)."""

from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    print(f"Build from {project_root} (configure PyInstaller here)")


if __name__ == "__main__":
    main()
