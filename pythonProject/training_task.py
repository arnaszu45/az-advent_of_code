from pathlib import Path


def main():
    polarion_list = []
    for path in Path('TestAutomation').rglob("test_*.py"):
        file = path.read_text()
        if 'cleaning.start_cleaning(' in file:
            lines = file[file.find('ID: ') + 3:]
            lines = lines.split('\n')
            polarion_id = (lines[0])
            polarion_id = polarion_id.strip().split('\n')
            polarion_list.extend(polarion_id)
    print(polarion_list)
    print(len(polarion_list))


if __name__ == "__main__":
    main()