from pathlib import Path
import argparse
search_for = {
    'a': 'cleaning.start_cleaning(',
    'b': 'shunts'
}
parser = argparse.ArgumentParser(description='Searching for function by name')
parser.add_argument("function", type=str)
args = parser.parse_args()
function = search_for.get(args.function, "")


def main():
    polarion_list = []
    for path in Path('TestAutomation').rglob("test_*.py"):
        file = path.read_text()
        if function in file:
            lines = file[file.find('Polarion ID: ') + 13:]
            lines = lines.split('\n')
            polarion_id = (lines[0])
            polarion_id = polarion_id.strip().split('\n')
            polarion_list.extend(polarion_id)
    print(polarion_list)
    print(len(polarion_list))


if __name__ == "__main__":
    main()