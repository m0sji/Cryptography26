# Playfair cipher for Romanian messages (31-letter alphabet).

# The 30 matrix letters in alphabetical order 
ALPHABET = "AĂÂBCDEFGHIÎKLMNOPQRSȘTȚUVWXYZ"
ROWS, COLS = 5, 6
MIN_KEY_LENGTH = 7  


def prepare_text(text):
    """Uppercase, merge J into I and keep only matrix letters (drops spaces). """
    text = text.upper().replace("J", "I")
    return "".join(c for c in text if c in ALPHABET)


def create_matrix(key):
    """Build the 5x6 key matrix.

    The key's letters come first, each only once,
    followed by the remaining alphabet letters in alphabetical order.
    """
    letters = []
    # Walking through key + alphabet and skipping letters already taken
    # removes repeats from the key and the alphabet letters the key already used
    for c in prepare_text(key) + ALPHABET:
        if c not in letters:
            letters.append(c)
    # Cut the flat list of 30 letters into 5 rows of 6
    return [letters[i:i + COLS] for i in range(0, ROWS * COLS, COLS)]


def find_position(matrix, char):
    """Return (row, column) of a letter in the matrix."""
    # The letter is always found: the input was validated and cleaned
    # by prepare_text, so it only contains matrix letters
    for row, letters in enumerate(matrix):
        if char in letters:
            return row, letters.index(char)


def chunks(text):
    """Cut text into consecutive 2-letter pieces: "ABCD" -> ["AB", "CD"]."""
    return [text[i:i + 2] for i in range(0, len(text), 2)]


def split_into_pairs(text):
    """Split the plaintext into pairs that Playfair can encrypt.

    A pair cannot contain the same letter twice, and the last letter needs
    a partner, so in both cases a filler is added. The filler is X; Q is
    used instead when X would give an XX pair or repeat the previous pair,
    and Z when Q is not possible either.
    Examples: "KISS" -> KI SX SQ
              "CONGRESS SHALL" -> CO NG RE SX SQ SH AL LX
    """
    pairs = []
    i = 0
    while i < len(text):
        a = text[i]
        if i + 1 < len(text) and text[i + 1] != a:
            # Normal case: the next letter is different, so the two form a pair
            pairs.append(a + text[i + 1])
            i += 2
        else:
            # Doubled letter or unpaired last letter: pair it with a filler.
            # Take the first one from X, Q, Z that is not the letter itself
            # and does not repeat the previous pair (SX SX -> SX SQ)
            for filler in "XQZ":
                if filler != a and (not pairs or pairs[-1] != a + filler):
                    break
            pairs.append(a + filler)
            # Move forward by one only, so the second of the doubled letters
            # starts the next pair
            i += 1
    return pairs


def transform_pair(matrix, pair, shift):
    """Apply the Playfair rules to one pair: shift=1 encrypts, shift=-1 decrypts.

    Decryption is encryption with the moves reversed (left instead of right,
    up instead of down), so one function handles both.
    """
    r1, c1 = find_position(matrix, pair[0])
    r2, c2 = find_position(matrix, pair[1])

    # The % operator wraps around the edges: moving right from the last
    # column goes back to the first one, moving up from the first row
    # goes to the last one, and so on

    # Rule 1 - same row: each letter is replaced by its neighbour
    # to the right (encrypt) or to the left (decrypt)
    if r1 == r2:
        return matrix[r1][(c1 + shift) % COLS] + matrix[r2][(c2 + shift) % COLS]

    # Rule 2 - same column: each letter is replaced by its neighbour
    # below (encrypt) or above (decrypt)
    if c1 == c2:
        return matrix[(r1 + shift) % ROWS][c1] + matrix[(r2 + shift) % ROWS][c2]

    # Rule 3 - rectangle: each letter keeps its row and takes the other
    # letter's column. Swapping the columns again gives back the original
    # pair, so this rule is the same for encryption and decryption
    return matrix[r1][c2] + matrix[r2][c1]


def encrypt(plaintext, matrix):
    """Clean the message, split it into pairs and encrypt each pair."""
    pairs = split_into_pairs(prepare_text(plaintext))
    print("\nPairs:", " ".join(pairs))
    return "".join(transform_pair(matrix, p, 1) for p in pairs)


def decrypt(ciphertext, matrix):
    """Split the ciphertext into pairs and decrypt each pair.

    The ciphertext is already made of valid pairs, so no fillers are added.
    The fillers inserted during encryption stay in the decrypted text.
    """
    pairs = chunks(prepare_text(ciphertext))
    print("\nPairs:", " ".join(pairs))
    return "".join(transform_pair(matrix, p, -1) for p in pairs)


def read_text(prompt, allow_j=True):
    """Ask until the input is non-empty and contains only alphabet letters and spaces.

    allow_j=False is used for the ciphertext: J has no cell in the matrix,
    so it can never appear in a real ciphertext. In the key and the message
    J is allowed and later turned into I.
    """
    # Uppercase and lowercase letters plus spaces (spaces are removed later)
    allowed = ALPHABET + ALPHABET.lower() + " " + ("Jj" if allow_j else "")
    while True:
        # Some keyboards type Ş/Ţ (with a cedilla) instead of the correct
        # Romanian Ș/Ț (with a comma below), so convert them before checking
        text = input(prompt).strip().translate(str.maketrans("ŞşŢţ", "ȘșȚț"))
        if not text:
            print("Input cannot be empty!")
        elif any(c not in allowed for c in text):
            # Tell the user which characters are accepted, as the task requires
            print("Invalid characters! Allowed: A-Z, a-z, Ă, Â, Î, Ș, Ț"
                  + ("" if allow_j else " (except J)"))
        else:
            return text


def main():
    # Step 1: choose the operation
    print("Playfair Cipher - Lab 3\n1. Encrypt\n2. Decrypt")
    choice = input("\nEnter option (1/2): ").strip()
    if choice not in ("1", "2"):
        print("Invalid option!")
        return

    # Step 2: read the key. Its length is the number of letters it has,
    # repeats included (MOLDOVA counts as 7) and spaces excluded
    while True:
        key = read_text(f"\nEnter key (minimum {MIN_KEY_LENGTH} letters): ")
        if len(prepare_text(key)) >= MIN_KEY_LENGTH:
            break
        print(f"Key must contain at least {MIN_KEY_LENGTH} letters (spaces are not counted)!")

    # Step 3: build the key matrix and show it
    matrix = create_matrix(key)
    print("\nPlayfair Matrix:")
    for row in matrix:
        print(" ".join(row))

    # Step 4: encrypt or decrypt. The result is printed in pairs for
    # readability; it can be pasted back as it is, because spaces are allowed
    if choice == "1":
        plaintext = read_text("\nEnter message to encrypt: ")
        print("Ciphertext:", " ".join(chunks(encrypt(plaintext, matrix))))
    else:
        while True:
            ciphertext = read_text("\nEnter ciphertext to decrypt: ", allow_j=False)
            # Playfair always outputs whole pairs, so an odd number of
            # letters means the ciphertext was typed or copied wrong
            if len(prepare_text(ciphertext)) % 2 == 0:
                break
            print("Ciphertext must have an even number of letters!")
        print("Decrypted text:", " ".join(chunks(decrypt(ciphertext, matrix))))
        # The final step is manual, as the task requires: the program cannot
        # tell a filler X from a real X in the message, and it cannot know
        # where the original spaces were
        print("Remove filler letters (X, Q or Z) and add spaces manually.")


# Run main() only when the file is started directly, not when it is imported
if __name__ == "__main__":
    main()
