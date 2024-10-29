from functools import wraps
from pathlib import Path
from typing import List


class TextColor:
    RED = "\033[31m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    END = "\033[0m"


def logger_file_merger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        # Print functions calls and used arguments
        if len(args) != 0:
            if len(kwargs) != 0:
                print(f"\n\tCall function '{func.__name__}' with:"
                      f"\n- total args {len(args)}: {args}"
                      f"\n- total kwargs {len(kwargs)}: {kwargs}")
            else:
                print(f"\n\tCall function '{func.__name__}' with:"
                      f"\n- total args {len(args)}: {args}")
        elif len(kwargs) != 0:
            print(f"\n\tCall function '{func.__name__}' with:"
                  f"\n- total kwargs {len(kwargs)}: {kwargs}")
        else:
            print(f"\n\tCall function '{func.__name__}' without any arguments")

        # Print path of merged files
        if len(args[1] + args[2]) == 0:
            print(f"\n\t{TextColor.RED}No files to merge{TextColor.END}")
            return
        if func.__name__ == 'merge_files_with_titles':
            print(f"\n\tMerged files (in total {len(args[1] + args[2])}):")
            for arg in args:
                if isinstance(arg, list):
                    for item in arg:
                        print(f"- {item}")
            print(f"\n\tOutput file:\n{args[0]}")

        return func(*args, **kwargs)
    return wrapper


def remove_file_from_filelist(directory: Path, files_py: List[Path], files_txt: List[Path], filename_txt="folder_content.txt"):
    """Removing self output and self script files from filesets."""

    file_to_remove = directory / filename_txt
    if file_to_remove in files_txt:
        files_txt.remove(file_to_remove)

    filename_py = Path(__file__).name
    file_to_remove = directory / filename_py
    if file_to_remove in files_py:
        files_py.remove(file_to_remove)


@logger_file_merger
def merge_files_with_titles(output_file_location, files_py, files_txt):
    with open(output_file_location, "w", encoding="utf-8") as combined:


        for file in files_py:
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                source_file_name = Path(f.name).name
                combined.write(source_file_name + "\n")
                combined.writelines(f.readlines())
                combined.write("\n" * 3)
        for file in files_txt:
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                source_file_name = Path(f.name).name
                combined.write(source_file_name + "\n")
                combined.writelines(f.readlines())
                combined.write("\n" * 3)


def main():

    # Path to directory
    while True:
        user_input = input(f"Enter full path or leave empty to use current directory:\n")
        if not user_input:
            directory = Path(Path(__file__).parent)
            print(f"Current path: {Path(__file__).parent}\n")
            break
        else:
            directory = Path(user_input)
            if directory.exists():
                break
            else:
                print(f"Directory '{user_input}' doesn't exist")
                continue

    # Output file
    user_input = input(f"Enter output file name or leave empty to use default name 'folder_content':")
    if not user_input:
        output_file_name = "folder_content.txt"
    else:
        output_file_name = user_input
    output_file_location = Path(directory) / output_file_name

    print(f"\n\tWorking...")

    # Making list *.py and *.txt files
    files_py = list(directory.glob("*.html"))
    files_txt = list(directory.glob("*.css"))

    # Removing self output file from txt-filelist
    remove_file_from_filelist(directory, files_py, files_txt, filename_txt=output_file_name)

    # Merge function
    merge_files_with_titles(output_file_location, files_py, files_txt)

    input(f"\n\t{TextColor.GREEN}Press 'Enter' to close.{TextColor.END}")


if __name__ == "__main__":
    main()
