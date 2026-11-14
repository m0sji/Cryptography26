# Romanian alphabet without J (30 letters fill the 5x6 matrix exactly)
ALPHABET = "AĂÂBCDEFGHIÎKLMNOPQRSȘTȚUVWXYZ"
ROWS, COLS = 5, 6


def create_playfair_matrix(key):
    """Build the 5x6 key matrix: the key's letters first, then the rest of the alphabet."""
    # J has no cell of its own, so it shares I's cell
    key = key.upper().replace('J', 'I')
    seen = set()
    processed_key = []

    # Keep each key letter only the first time it appears, preserving order.
    # Anything outside the alphabet (e.g. spaces) is dropped.
    for char in key:
        if char in ALPHABET and char not in seen:
            seen.add(char)
            processed_key.append(char)

    # Fill the remaining cells with the unused letters in alphabetical order
    matrix_chars = processed_key.copy()
    for char in ALPHABET:
        if char not in seen:
            matrix_chars.append(char)

    # Cut the flat list of 30 letters into 5 rows of 6
    matrix = []
    for i in range(0, ROWS * COLS, COLS):
        row = matrix_chars[i:i+COLS]
        matrix.append(row)

    return matrix


def find_position(matrix, char):
    """Return (row, column) of a letter in the matrix, or (None, None) if it is absent."""
    for i, row in enumerate(matrix):
        for j, c in enumerate(row):
            if c == char:
                return i, j
    return None, None


def print_matrix(matrix):
    print("\nPlayfair Matrix:")
    for row in matrix:
        print(' '.join(row))
    print()


def normalize_diacritics(text):
    # Map cedilla forms (Ş, ş, Ţ, ţ) to the comma-below letters used in the alphabet
    return text.translate(str.maketrans("ŞşŢţ", "ȘșȚț"))


def prepare_text(text):
    """Uppercase the text, merge J into I and drop everything that is not a matrix letter."""
    text = text.upper().replace('J', 'I')
    cleaned = ''.join([c for c in text if c in ALPHABET])
    return cleaned


def split_into_pairs(text):
    """Split plaintext into digraphs, inserting fillers where Playfair requires them."""
    pairs = []
    i = 0

    while i < len(text):
        # Use Q as filler after X so a pair never becomes XX
        filler = 'Q' if text[i] == 'X' else 'X'

        if i == len(text) - 1:
            # Last letter has no partner: pad it with the filler
            pairs.append(text[i] + filler)
            i += 1
        elif text[i] == text[i + 1]:
            # A pair of identical letters cannot be encrypted: put the filler
            # between them and advance by one, so the second letter starts the next pair
            pairs.append(text[i] + filler)
            i += 1
        else:
            # Normal case: consume two letters
            pairs.append(text[i] + text[i + 1])
            i += 2

    return pairs


def encrypt_pair(matrix, pair):
    """Encrypt one digraph using the three Playfair rules."""
    char1, char2 = pair[0], pair[1]

    row1, col1 = find_position(matrix, char1)
    row2, col2 = find_position(matrix, char2)

    # Safety net: leave the pair unchanged if a letter is not in the matrix
    if row1 is None or row2 is None:
        return pair

    # Same row: take the letter to the right of each (wrapping to the row start)
    if row1 == row2:
        new_col1 = (col1 + 1) % COLS
        new_col2 = (col2 + 1) % COLS
        return matrix[row1][new_col1] + matrix[row2][new_col2]

    # Same column: take the letter below each (wrapping to the top)
    elif col1 == col2:
        new_row1 = (row1 + 1) % ROWS
        new_row2 = (row2 + 1) % ROWS
        return matrix[new_row1][col1] + matrix[new_row2][col2]

    # Rectangle: each letter keeps its row and takes the other letter's column
    else:
        return matrix[row1][col2] + matrix[row2][col1]


def decrypt_pair(matrix, pair):
    """Decrypt one digraph: the inverse of encrypt_pair (shift left/up instead of right/down)."""
    char1, char2 = pair[0], pair[1]

    row1, col1 = find_position(matrix, char1)
    row2, col2 = find_position(matrix, char2)

    # Safety net: leave the pair unchanged if a letter is not in the matrix
    if row1 is None or row2 is None:
        return pair

    # Same row: take the letter to the left of each (wrapping to the row end)
    if row1 == row2:
        new_col1 = (col1 - 1) % COLS
        new_col2 = (col2 - 1) % COLS
        return matrix[row1][new_col1] + matrix[row2][new_col2]

    # Same column: take the letter above each (wrapping to the bottom)
    elif col1 == col2:
        new_row1 = (row1 - 1) % ROWS
        new_row2 = (row2 - 1) % ROWS
        return matrix[new_row1][col1] + matrix[new_row2][col2]

    # Rectangle: swapping columns is its own inverse, so it is the same as in encryption
    else:
        return matrix[row1][col2] + matrix[row2][col1]


def encrypt(plaintext, key):
    """Encrypt a message: build the matrix, clean the text, pair it up, encrypt each pair."""
    matrix = create_playfair_matrix(key)
    prepared = prepare_text(plaintext)
    pairs = split_into_pairs(prepared)

    # Show the intermediate steps so the result can be checked by hand
    print("Prepared text:", prepared)
    print("Pairs:", ' '.join(pairs))
    print_matrix(matrix)

    encrypted_pairs = [encrypt_pair(matrix, pair) for pair in pairs]
    ciphertext = ''.join(encrypted_pairs)

    return ciphertext


def decrypt(ciphertext, key):
    """Decrypt a ciphertext with the same key. Fillers stay in the output."""
    matrix = create_playfair_matrix(key)
    prepared = prepare_text(ciphertext)

    # Ciphertext is already made of valid digraphs, so it is simply cut every
    # two letters (no fillers needed; main() guarantees an even length)
    pairs = [prepared[i:i+2] for i in range(0, len(prepared), 2)]

    print("Prepared ciphertext:", prepared)
    print("Pairs:", ' '.join(pairs))
    print_matrix(matrix)
    
    decrypted_pairs = [decrypt_pair(matrix, pair) for pair in pairs]
    plaintext = ''.join(decrypted_pairs)
    
    return plaintext


def validate_input(text, allow_j=True):
    """Return True if the text contains only alphabet letters (either case) and spaces."""
    # J is not in the matrix, but keys and messages may contain it: it is merged into I.
    # Ciphertext can never contain J, so it is rejected there.
    allowed = ALPHABET + ALPHABET.lower() + " "
    if allow_j:
        allowed += "Jj"

    for char in text:
        if char not in allowed:
            return False
    return True


def count_distinct_letters(key):
    # Distinct matrix letters in the key (J counts as I, repeats count once)
    return len(set(prepare_text(key)))


def main():
    print("Playfair Cipher - Lab 3")
    print()
    
    print("Choose operation:")
    print("1. Encrypt")
    print("2. Decrypt")
    
    choice = input("\nEnter option (1/2): ").strip()
    
    if choice not in ['1', '2']:
        print("Invalid option!")
        return
    
    # Keep asking until the key is valid (the key is needed for both operations)
    while True:
        key = normalize_diacritics(input("\nEnter key (minimum 7 different letters): ").strip())

        if not validate_input(key):
            print("Key contains invalid characters!")
            print("Allowed: A-Z, a-z, Ă, Â, Î, Ș, Ț")
            continue

        if count_distinct_letters(key) < 7:
            print("Key must contain at least 7 different letters!")
            print("Repeated letters and spaces are not counted, and J counts as I.")
            continue

        break
    
    if choice == '1':
        while True:
            plaintext = normalize_diacritics(input("\nEnter message to encrypt: ").strip())
            
            if not validate_input(plaintext):
                print("Message contains invalid characters!")
                print("Allowed: A-Z, a-z, Ă, Â, Î, Ș, Ț")
                continue
            
            if not plaintext:
                print("Message cannot be empty!")
                continue
            
            break
        
        print("\n--- ENCRYPTION ---")
        ciphertext = encrypt(plaintext, key)
        
        print("Ciphertext:", ciphertext)
        # Also print it grouped in digraphs, which is easier to read
        spaced =' '.join([ciphertext[i:i+2] for i in range(0, len(ciphertext), 2)])
        print("Ciphertext (spaced):", spaced)
        
    else:
        while True:
            ciphertext = normalize_diacritics(input("\nEnter ciphertext to decrypt: ").strip())

            if not validate_input(ciphertext, allow_j=False):
                print("Ciphertext contains invalid characters!")
                print("Allowed: A-Z (except J), a-z (except j), Ă, Â, Î, Ș, Ț")
                continue

            if not ciphertext:
                print("Ciphertext cannot be empty!")
                continue

            # Playfair always outputs whole digraphs, so an odd length means a corrupted ciphertext
            if len(prepare_text(ciphertext)) % 2 != 0:
                print("Ciphertext must have an even number of letters!")
                continue

            break
        
        print("\n--- DECRYPTION ---")
        plaintext = decrypt(ciphertext, key)
        
        print("Decrypted text:", plaintext)
        # Fillers cannot be removed automatically: an X may be a real letter of the message
        print("\nNote: Remove filler 'X' (or 'Q' after an X) characters and add spaces manually.")


if __name__ == "__main__":
    main()