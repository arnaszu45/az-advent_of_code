from pathlib import Path
import argparse


def main():
    polarion_list = []
    for path in args.test_automation_dir.rglob("test_*.py"):
        file = path.read_text()
        if args.pattern in file:
            id_pattern = '"""\n    Polarion ID:'
            remaining_text = file[file.find(id_pattern) + len(id_pattern):]
            remaining_text = remaining_text.split()[0]
            polarion_id = remaining_text.strip()
            if '-' in polarion_id:
                polarion_list.append(polarion_id)
    print(polarion_list)
    print(len(polarion_list))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--test_automation_dir", type=Path, nargs="?", help="Directory of test automation folder")
    parser.add_argument("-p", "--pattern", type=str, help="The pattern what should be looked for in files")
    args = parser.parse_args()
    main()