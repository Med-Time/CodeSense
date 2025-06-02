import tempfile
import os
from core.fetcher import read_all_files

def test_read_all_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "main.py")
        with open(file_path, "w") as f:
            f.write("print('Hello')")

        result = read_all_files(temp_dir)
        assert any("main.py" in file["path"] for file in result)
