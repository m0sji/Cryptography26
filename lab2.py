"""Frequency-analysis workbench for breaking monoalphabetic substitution ciphers.

Laboratory work nr. 2 -- Cryptanalysis of monoalphabetic ciphers.
The program counts the statistics of an intercepted cryptogram (letters,
digrams, trigrams, doubles, short words) and lets the user build the
substitution by hand, one guess at a time, the way the attack is done on
paper. Only letters are substituted; every other character is left as it is.
"""

import os
import re
import sys
from collections import Counter

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
N = len(ALPHABET)

# Frequency of the letters of the English language, in percent (lab guide, table 2.2).
ENGLISH = {
    "A": 8.17, "B": 1.49, "C": 2.78, "D": 4.25, "E": 12.70, "F": 2.23,
    "G": 2.01, "H": 6.09, "I": 6.97, "J": 0.15, "K": 0.77, "L": 4.03,
    "M": 2.41, "N": 6.75, "O": 7.51, "P": 1.93, "Q": 0.09, "R": 5.99,
    "S": 6.33, "T": 9.06, "U": 2.76, "V": 0.98, "W": 2.36, "X": 0.15,
    "Y": 1.97, "Z": 0.07,
}

# Ranking of the English letters, most frequent first. Used by the "auto" command.
ENGLISH_ORDER = sorted(ALPHABET, key=lambda ch: -ENGLISH[ch])


def read_line(prompt=""):
    try:
        return input(prompt)
    except EOFError:
        return None


def letters_of(text):
    return [ch for ch in text.upper() if ch in ALPHABET]


def words_of(text):
    return re.findall(r"[A-Z]+", text.upper())


def letter_counts(text):
    counts = Counter(letters_of(text))
    return {ch: counts.get(ch, 0) for ch in ALPHABET}


def ngram_counts(text, size):
    counts = Counter()
    for word in words_of(text):
        for i in range(len(word) - size + 1):
            counts[word[i:i + size]] += 1
    return counts


def chi_squared(text):
    """Distance between the letter distribution of `text` and English.

    A small value means the text behaves like English; a large one means it
    does not. The value is the usual statistic, sum (observed - expected)^2 /
    expected, computed over the 26 letters.
    """
    counts = letter_counts(text)
    total = sum(counts.values())
    if total == 0:
        return 0.0
    score = 0.0
    for ch in ALPHABET:
        expected = total * ENGLISH[ch] / 100
        score += (counts[ch] - expected) ** 2 / expected
    return score


def index_of_coincidence(text):
    """Probability that two letters drawn from the text are the same.

    A monoalphabetic cipher only renames the letters, so the value is the same
    for the cryptogram and for the plaintext: about 0.065 for English, against
    0.0385 for a uniform random text.
    """
    counts = letter_counts(text)
    total = sum(counts.values())
    if total < 2:
        return 0.0
    return sum(n * (n - 1) for n in counts.values()) / (total * (total - 1))


def bar(value, scale, width=40):
    return "#" * min(width, int(round(value * width / scale)))


def show_frequencies(text):
    counts = letter_counts(text)
    total = sum(counts.values())
    if total == 0:
        print("The cryptogram contains no letters.")
        return
    order = sorted(ALPHABET, key=lambda ch: (-counts[ch], ch))
    scale = max(max(counts.values()) * 100 / total, max(ENGLISH.values()))

    print(f"\nLetters: {total}   Index of coincidence: {index_of_coincidence(text):.4f}"
          f"   Chi-squared against English: {chi_squared(text):.1f}")
    print("\nCryptogram letters, most frequent first (English letter of the same rank "
          "on the right):")
    print(f"{'':2}{'letter':>7}{'count':>7}{'%':>8}  {'':<42}{'English':>9}")
    for rank, ch in enumerate(order):
        percent = counts[ch] * 100 / total
        guess = ENGLISH_ORDER[rank]
        print(f"{rank + 1:2}{ch:>7}{counts[ch]:>7}{percent:>8.2f}  "
              f"{bar(percent, scale):<42}{guess} ({ENGLISH[guess]:.2f}%)")


def show_ngrams(text):
    for size, title, limit in ((2, "Digrams", 12), (3, "Trigrams", 12)):
        print(f"\n{title}:")
        line = "   ".join(f"{gram} {count:>3}"
                          for gram, count in ngram_counts(text, size).most_common(limit))
        print(f"  {line if line else '(none)'}")

    doubles = Counter({gram: count for gram, count in ngram_counts(text, 2).items()
                       if gram[0] == gram[1]})
    print("\nDoubled letters:")
    line = "   ".join(f"{gram} {count:>3}" for gram, count in doubles.most_common(10))
    print(f"  {line if line else '(none)'}")


def show_words(text):
    words = words_of(text)
    print(f"\nWords: {len(words)}")
    for size in (1, 2, 3):
        counts = Counter(word for word in words if len(word) == size)
        print(f"\nWords of {size} letter(s):")
        line = "   ".join(f"{word} {count:>3}" for word, count in counts.most_common(12))
        print(f"  {line if line else '(none)'}")


def decrypt(text, key):
    """Replace the cipher letters that are already guessed.

    A solved letter is printed in lower case (the plaintext), a letter that is
    still unknown stays in upper case (the cryptogram), so that the progress of
    the attack can be read directly off the text.
    """
    out = []
    for ch in text:
        upper = ch.upper()
        if upper in ALPHABET:
            out.append(key[upper] if upper in key else upper)
        else:
            out.append(ch)
    return "".join(out)


def preview(text, width=150):
    """The beginning of the text, so that a guess can be judged at a glance."""
    short = " ".join(text.split())
    return short[:width] + ("..." if len(short) > width else "")


def show_key(key):
    print("\n  Plaintext  alphabet: " + " ".join(ch.lower() for ch in ALPHABET))
    inverse = {plain.upper(): cipher for cipher, plain in key.items()}
    print("  Ciphertext alphabet: " + " ".join(inverse.get(ch, ".") for ch in ALPHABET))
    print("\n  Cipher -> plain: " +
          ("  ".join(f"{c}->{p}" for c, p in sorted(key.items())) if key else "(empty)"))
    print(f"  Letters solved: {len(key)} of {N}")


def check_pair(argument, key):
    pair = argument.replace("-", "").replace(">", "").replace(" ", "")
    if len(pair) != 2 or pair[0].upper() not in ALPHABET or pair[1].upper() not in ALPHABET:
        return None, ("Error: Invalid substitution. Write two letters, the cipher letter "
                      "first, for example 'set ve' for V -> e.")
    cipher, plain = pair[0].upper(), pair[1].lower()
    for other_cipher, other_plain in key.items():
        if other_plain == plain and other_cipher != cipher:
            return None, (f"Error: The plaintext letter '{plain}' is already used by "
                          f"{other_cipher} -> {other_plain}. A substitution cipher is a "
                          f"one-to-one map; remove it first with 'del {other_cipher}'.")
    return (cipher, plain), None


def auto_key(text):
    """Guess a key by matching the ranks of the two frequency tables."""
    counts = letter_counts(text)
    order = sorted(ALPHABET, key=lambda ch: (-counts[ch], ch))
    return {cipher: plain.lower() for cipher, plain in zip(order, ENGLISH_ORDER)}


def save_file(path, content):
    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content + "\n")
    except OSError as error:
        print(f"Error: Could not write '{path}': {error.strerror}.")
        return
    print(f"Saved to '{path}'.")


HELP = """
Commands:
  freq            letter frequencies, index of coincidence, chi-squared
  ngrams          digrams, trigrams and doubled letters
  words           the one-, two- and three-letter words
  text            the cryptogram with the solved letters replaced
  cipher          the intercepted cryptogram, unchanged
  set XY          guess that cipher letter X stands for plaintext letter Y
  del X           undo the guess made for cipher letter X
  auto            fill every unsolved letter by matching the frequency ranks
  clear           remove every guess
  key             the substitution found so far
  save FILE       write the current text to FILE
  help            this list
  exit            leave the program
"""


def workbench(cryptogram):
    key = {}
    letters = letters_of(cryptogram)
    print(f"\nCryptogram loaded: {len(cryptogram)} characters, {len(letters)} letters, "
          f"{len(words_of(cryptogram))} words.")
    print(HELP)
    while True:
        line = read_line("\n> ")
        if line is None:
            return
        parts = line.strip().split(maxsplit=1)
        if not parts:
            continue
        command, argument = parts[0].lower(), (parts[1].strip() if len(parts) > 1 else "")

        if command == "exit":
            return
        elif command == "help":
            print(HELP)
        elif command == "freq":
            show_frequencies(cryptogram)
        elif command == "ngrams":
            show_ngrams(cryptogram)
        elif command == "words":
            show_words(cryptogram)
        elif command == "cipher":
            print("\n" + cryptogram)
        elif command == "text":
            print("\n" + decrypt(cryptogram, key))
            print(f"\nChi-squared against English: {chi_squared(decrypt(cryptogram, key)):.1f}")
        elif command == "key":
            show_key(key)
        elif command == "set":
            pair, error = check_pair(argument, key)
            if error is not None:
                print(error)
                continue
            cipher, plain = pair
            key[cipher] = plain
            print(f"{cipher} -> {plain}   ({len(key)} of {N} letters solved)")
            print(f"  {preview(decrypt(cryptogram, key))}")
        elif command == "del":
            letter = argument.upper()
            if letter not in key:
                print(f"Error: No guess was made for '{argument}'.")
                continue
            del key[letter]
            print(f"Removed. ({len(key)} of {N} letters solved)")
        elif command == "auto":
            key = auto_key(cryptogram)
            print("Key guessed from the frequency ranks alone:")
            show_key(key)
            print("\n" + decrypt(cryptogram, key))
        elif command == "clear":
            key = {}
            print("All guesses removed.")
        elif command == "save":
            if not argument:
                print("Error: Give a file name, for example 'save plain.txt'.")
                continue
            save_file(argument, decrypt(cryptogram, key))
        else:
            print(f"Error: Unknown command '{parts[0]}'. Type 'help' for the list.")


def read_cryptogram_from_file():
    path = read_line("Path of the file with the cryptogram: ")
    if path is None:
        return None
    path = path.strip().strip('"').strip("'")
    if not os.path.isfile(path):
        print(f"Error: '{path}' is not a file.")
        return None
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            text = handle.read()
    except OSError as error:
        print(f"Error: Could not read '{path}': {error.strerror}.")
        return None
    return text.strip()


def read_cryptogram_from_input():
    print("Paste the cryptogram. Finish with an empty line:")
    lines = []
    while True:
        line = read_line()
        if line is None or not line.strip():
            break
        lines.append(line.strip())
    return " ".join(lines)


def main():
    sys.stdin.reconfigure(encoding="utf-8", errors="replace", newline=None)
    sys.stdout.reconfigure(encoding="utf-8")

    while True:
        print("Choose an option: ")
        print("1. Load the cryptogram from a file")
        print("2. Type or paste the cryptogram")
        print("3. Exit")
        line = read_line()
        if line is None:
            return
        choice = line.strip()
        if choice == "3":
            return
        if choice == "1":
            cryptogram = read_cryptogram_from_file()
        elif choice == "2":
            cryptogram = read_cryptogram_from_input()
        else:
            print("Please choose a valid option.")
            continue
        if not cryptogram:
            print("Error: The cryptogram is empty. Please try again.")
            continue
        if not letters_of(cryptogram):
            print("Error: The cryptogram contains no letters. Please try again.")
            continue
        workbench(cryptogram)


if __name__ == "__main__":
    main()
