from pathlib import Path
import argparse


def main(directory: Path, pattern: str):
    polarion_list = []
    for path in directory.rglob("test_*.py"):
        file_text = path.read_text()
        if pattern in file_text:
            id_pattern = 'Polarion ID:'
            id_index = file_text.find(id_pattern)
            if id_index < 0:
                continue
            remaining_text = file_text[id_index + len(id_pattern):]
            remaining_text = remaining_text.split()[0]
            polarion_id = remaining_text.strip()
            polarion_list.append(polarion_id)
    print(polarion_list)
    print(len(polarion_list))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--test_automation_dir", type=Path, help="Directory of test automation folder")
    parser.add_argument("-p", "--pattern", type=str, help="The pattern what should be looked for in files")
    # parser.add_argument(, "--pattern", nargs='+', type=str, help="The pattern what should be looked for in files")
    args = parser.parse_args()
    main(directory=args.test_automation_dir, pattern=args.pattern)