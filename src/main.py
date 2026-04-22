import os
import shutil
from extract_md import generate_page_recursive
import sys


def clear_directory(path: str):
    if not os.path.exists(path):
        os.mkdir(path)
        return

    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        if os.path.isfile(full_path):
            os.remove(full_path)
        else:
            shutil.rmtree(full_path)


def copy_recursive(src, dst):
    if not os.path.exists(dst):
        os.mkdir(dst)

    for entry in os.listdir(src):
        src_path = os.path.join(src, entry)
        dst_path = os.path.join(dst, entry)

        if os.path.isfile(src_path):
            shutil.copy(src_path, dst_path)
            print(f"Copied: {src_path}")
        else:
            copy_recursive(src_path, dst_path)


def main():
    args = sys.argv[1:]

    if args:
        url_basepath = args[0]
    else:
        url_basepath = "/"

    project_root = "."

    static_path = os.path.join(project_root, "static")
    public_path = os.path.join(project_root, "docs")

    clear_directory(public_path)
    copy_recursive(static_path, public_path)

    generate_page_recursive(
        basepath=url_basepath,
        content_path_dir="content",
        template_path="template.html",
        dest_path_dir=public_path
    )


if __name__ == "__main__":
    main()