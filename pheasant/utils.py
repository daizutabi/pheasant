import os
import subprocess
import time

import pheasant


def mkdocs():
    start = time.time()
    root = os.path.join(os.path.dirname(pheasant.__file__), "../docs")
    # root = r"C:\Users\daizu\desktop\pheasant\docs"
    os.chdir(root)
    subprocess.run(("mkdocs", "build"))
    duration = time.time() - start
    print(duration)


def convert():
    start = time.time()
    path = os.path.join(os.path.dirname(pheasant.__file__), "../docs/docs/index.md")
    # path = r"C:\Users\daizu\desktop\test\docs\index.md"
    from pheasant.core.pheasant import Pheasant

    converter = Pheasant()
    converter.convert_from_file(path, "main")
    duration = time.time() - start
    print(duration)


if __name__ == "__main__":
    mkdocs()
