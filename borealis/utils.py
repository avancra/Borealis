from pathlib import Path


def get_lib_dir():
    current_file = Path(__file__).resolve()
    for parent in current_file.parents:
        if (parent / "lib").is_dir():
            return parent / "lib"
    raise FileNotFoundError("Lib directory not found in parent directories.")