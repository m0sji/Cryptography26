import re
import sys

ALPHABET = "AĂÂBCDEFGHIÎJKLMNOPQRSȘTȚUVWXYZ"
LETTERS = set(ALPHABET)
MAX_KEY = len(ALPHABET) - 1
MIN_KEYWORD_LENGTH = 7

CEDILLA_TO_COMMA = str.maketrans("şŞţŢ", "șȘțȚ")


def normalize(text):
    return text.translate(CEDILLA_TO_COMMA)


def keyword_alphabet(keyword):
    keyword_letters = normalize(keyword).replace(" ", "").upper()
    return "".join(dict.fromkeys(keyword_letters + ALPHABET))


def shift(text, key, alphabet):
    letters = [ch.upper() for ch in normalize(text) if not is_space(ch)]
    return "".join(alphabet[(alphabet.index(ch) + key) % len(alphabet)] for ch in letters)


def is_space(ch):
    return ch.isspace() and ch not in "\x1c\x1d\x1e\x1f"


def trim(text):
    spaces_in_text = "".join(ch for ch in set(text) if is_space(ch))
    return text.strip(spaces_in_text)


def utf16_length(text):
    return sum(2 if ord(ch) > 0xFFFF else 1 for ch in text)


def display_char(ch):
    return "\N{REPLACEMENT CHARACTER}" if ord(ch) > 0xFFFF else ch


INTEGER = re.compile(r"[\t\n\v\f\r ]*([+-]?[0-9]+)[\t\n\v\f\r ]*\x00*")


def parse_int(line):
    text = trim(line).strip("\N{BYTE ORDER MARK}")
    match = INTEGER.fullmatch(text)
    if not match:
        return None
    try:
        number = int(match.group(1))
    except ValueError:
        return None
    return number if -2**31 <= number < 2**31 else None


def first_invalid_char(text, skip_spaces):
    for ch in text:
        if skip_spaces and is_space(ch):
            continue
        if ch.upper() not in LETTERS:
            return display_char(ch)
    return None


def check_message(line):
    bad = first_invalid_char(normalize(line), skip_spaces=True)
    if bad is not None:
        return None, (f"Error: Invalid character '{bad}' rejected. Allowed characters are "
                      f"Romanian alphabet letters (A-Z, Ă, Â, Î, Ș, Ț).")
    return line, None


def check_key(line):
    key = parse_int(line)
    if key is None or not 1 <= key <= MAX_KEY:
        return None, f"Error: Invalid key. Allowed range is an integer between 1 and {MAX_KEY} inclusive."
    return key, None


def check_keyword(line):
    letters = normalize(line).replace(" ", "")
    length = utf16_length(letters)
    if length < MIN_KEYWORD_LENGTH:
        return None, (f"Error: Key 2 (keyword) must be at least {MIN_KEYWORD_LENGTH} "
                      f"characters long. (Entered length: {length}).")
    bad = first_invalid_char(letters, skip_spaces=False)
    if bad is not None:
        return None, (f"Error: Invalid character '{bad}' rejected in keyword. "
                      f"Only Romanian alphabet letters are allowed.")
    return line, None


def read_line(prompt=""):
    try:
        return input(prompt)
    except EOFError:
        return None


def ask(prompt, check, retry_message):
    while True:
        line = read_line(prompt)
        if line is None:
            return None
        value, error = check(line)
        if error is None:
            return value
        print(error)
        print(retry_message)


def menu(options, out_of_range_message):
    while True:
        print("Choose an option: ")
        for number, (label, _) in enumerate(options, start=1):
            print(f"{number}. {label}")
        line = read_line()
        if line is None:
            return
        choice = parse_int(line)
        if choice is None:
            print("Please choose a valid option")
        elif choice == len(options):
            return
        elif 1 <= choice < len(options):
            run = options[choice - 1][1]
            run()
        else:
            print(out_of_range_message)


def cipher_dialog(two_keys, decrypting):
    action = "decryption" if decrypting else "encryption"

    message_prompt = "Enter the encrypted message: " if decrypting else "Enter the message: "
    message = ask(message_prompt, check_message, "Please enter the text again.")
    if message is None:
        return

    if two_keys:
        key_prompt = f"Enter {'decryption ' if decrypting else ''}key-1 (shift: 1 - {MAX_KEY}): "
    else:
        key_prompt = f"Enter the {action} key (1 - {MAX_KEY}): "
    key = ask(key_prompt, check_key, "Please enter the key again.")
    if key is None:
        return

    alphabet = ALPHABET
    if two_keys:
        keyword_prompt = f"Enter {action} key-2 (keyword >= {MIN_KEYWORD_LENGTH} characters): "
        keyword = ask(keyword_prompt, check_keyword, "Please enter the keyword again.")
        if keyword is None:
            return
        alphabet = keyword_alphabet(keyword)
        print(f"Permuted Alphabet: {alphabet}")

    result = shift(message, -key if decrypting else key, alphabet)
    print(f"{'Decrypted' if decrypting else 'Encrypted'} message: {result}")


def cipher_menu(two_keys):
    menu([("Encrypt", lambda: cipher_dialog(two_keys, decrypting=False)),
          ("Decrypt", lambda: cipher_dialog(two_keys, decrypting=True)),
          ("Exit", None)],
         out_of_range_message="Please choose a valid option")


def main():
    sys.stdin.reconfigure(encoding="utf-8", errors="replace", newline=None)
    sys.stdout.reconfigure(encoding="utf-8")

    menu([("1-Key Caesar Cipher", lambda: cipher_menu(two_keys=False)),
          ("2-Key Caesar Cipher", lambda: cipher_menu(two_keys=True)),
          ("Exit", None)],
         out_of_range_message="Please choose a valid option.")


if __name__ == "__main__":
    main()
