chat = """
user: Hello
bot: Hello, sir
user: Can you help
user: me with something
user: ok?
bot: yes sir will do
cat: meow meow meow!
"""


def get_message(full_text: str, term: str) -> list[str]:
    messages_list = []
    term_pos = full_text.find(term)
    remaining_text = full_text[term_pos + len(term):]
    if term_pos == -1:
        return messages_list
    result = full_text[term_pos: term_pos+len(term)]
    messages_list.append(result)
    print(messages_list)
    next_message = remaining_text.strip().split(': ')[1]
    next_message = next_message.split('\n')[0]
    messages_list.extend(get_message(remaining_text, next_message))


def main(text: str, term: str):
    get_message(text, term)


if __name__ == '__main__':
    main(chat, 'Hello')