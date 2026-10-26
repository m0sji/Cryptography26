# Romanian alphabet without J (30 letters fill the 5x6 matrix exactly)
ALPHABET = "AĂÂBCDEFGHIÎKLMNOPQRSȘTȚUVWXYZ"
ROWS, COLS = 5, 6


def create_playfair_matrix(key):
    key = key.upper().replace('J', 'I')
    seen = set()
    processed_key = []

    for char in key:
        if char in ALPHABET and char not in seen:
            seen.add(char)
            processed_key.append(char)

    matrix_chars = processed_key.copy()
    for char in ALPHABET:
        if char not in seen:
            matrix_chars.append(char)

    # Create 5x6 matrix
    matrix = []
    for i in range(0, ROWS * COLS, COLS):
        row = matrix_chars[i:i+COLS]
        matrix.append(row)

    return matrix


def find_position(matrix, char):
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
    text = text.upper().replace('J', 'I')
    cleaned = ''.join([c for c in text if c in ALPHABET])
    return cleaned


def split_into_pairs(text):
    pairs = []
    i = 0

    while i < len(text):
        # Use Q as filler after X so a pair never becomes XX
        filler = 'Q' if text[i] == 'X' else 'X'

        if i == len(text) - 1:
            pairs.append(text[i] + filler)
            i += 1
        elif text[i] == text[i + 1]:
            pairs.append(text[i] + filler)
            i += 1
        else:
            pairs.append(text[i] + text[i + 1])
            i += 2
    
    return pairs


def encrypt_pair(matrix, pair):
    char1, char2 = pair[0], pair[1]
    
    row1, col1 = find_position(matrix, char1)
    row2, col2 = find_position(matrix, char2)
    
    if row1 is None or row2 is None:
        return pair
    
    # Same row
    if row1 == row2:
        new_col1 = (col1 + 1) % COLS
        new_col2 = (col2 + 1) % COLS
        return matrix[row1][new_col1] + matrix[row2][new_col2]

    # Same column
    elif col1 == col2:
        new_row1 = (row1 + 1) % ROWS
        new_row2 = (row2 + 1) % ROWS
        return matrix[new_row1][col1] + matrix[new_row2][col2]
    
    # Rectangle
    else:
        return matrix[row1][col2] + matrix[row2][col1]


def decrypt_pair(matrix, pair):
    char1, char2 = pair[0], pair[1]
    
    row1, col1 = find_position(matrix, char1)
    row2, col2 = find_position(matrix, char2)
    
    if row1 is None or row2 is None:
        return pair
    
    # Same row
    if row1 == row2:
        new_col1 = (col1 - 1) % COLS
        new_col2 = (col2 - 1) % COLS
        return matrix[row1][new_col1] + matrix[row2][new_col2]

    # Same column
    elif col1 == col2:
        new_row1 = (row1 - 1) % ROWS
        new_row2 = (row2 - 1) % ROWS
        return matrix[new_row1][col1] + matrix[new_row2][col2]
    
    # Rectangle
    else:
        return matrix[row1][col2] + matrix[row2][col1]


def encrypt(plaintext, key):
    matrix = create_playfair_matrix(key)
    prepared = prepare_text(plaintext)
    pairs = split_into_pairs(prepared)
    
    print("Prepared text:", prepared)
    print("Pairs:", ' '.join(pairs))
    print_matrix(matrix)
    
    encrypted_pairs = [encrypt_pair(matrix, pair) for pair in pairs]
    ciphertext = ''.join(encrypted_pairs)
    
    return ciphertext


def decrypt(ciphertext, key):
    matrix = create_playfair_matrix(key)
    prepared = prepare_text(ciphertext)
    
    pairs = [prepared[i:i+2] for i in range(0, len(prepared), 2)]
    
    print("Prepared ciphertext:", prepared)
    print("Pairs:", ' '.join(pairs))
    print_matrix(matrix)
    
    decrypted_pairs = [decrypt_pair(matrix, pair) for pair in pairs]
    plaintext = ''.join(decrypted_pairs)
    
    return plaintext


def validate_input(text):
    allowed = "AĂÂBCDEFGHIÎKLMNOPQRSȘTȚUVWXYZaăâbcdefghiîklmnopqrsștțuvwxyz "
    
    for char in text:
        if char not in allowed:
            return False
    return True


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
    
    while True:
        key = normalize_diacritics(input("\nEnter key (minimum 7 letters): ").strip())

        if len(key.replace(' ', '')) < 7:
            print("Key must contain at least 7 letters (spaces are not counted)!")
            continue
        
        if not validate_input(key):
            print("Key contains invalid characters!")
            print("Allowed: A-Z, a-z, Ă, Â, Î, Ș, Ț")
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
        spaced = ' '.join([ciphertext[i:i+2] for i in range(0, len(ciphertext), 2)])
        print("Ciphertext (spaced):", spaced)
        
    else:
        while True:
            ciphertext = normalize_diacritics(input("\nEnter ciphertext to decrypt: ").strip())

            if not validate_input(ciphertext):
                print("Ciphertext contains invalid characters!")
                print("Allowed: A-Z, a-z, Ă, Â, Î, Ș, Ț")
                continue

            if not ciphertext:
                print("Ciphertext cannot be empty!")
                continue

            if len(prepare_text(ciphertext)) % 2 != 0:
                print("Ciphertext must have an even number of letters!")
                continue

            break
        
        print("\n--- DECRYPTION ---")
        plaintext = decrypt(ciphertext, key)
        
        print("Decrypted text:", plaintext)
        print("\nNote: Remove filler 'X' (or 'Q' after an X) characters and add spaces manually.")


if __name__ == "__main__":
    main()