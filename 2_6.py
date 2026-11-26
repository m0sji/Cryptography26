# DES - first part of the round function f(R(i-1), Ki).
#
# In every round i (1..16) of DES, the right half R(i-1) (32 bits) is:
#   1. expanded to 48 bits with the expansion table E,
#   2. XOR-ed with the 48-bit round key Ki,
#   3. split into eight 6-bit blocks B1..B8, which then go into the S-boxes S1..S8.
# This program performs steps 1-3 and prints every intermediate value.

import random

# Expansion table E (32 bits -> 48 bits). Row j produces the 6-bit block Bj.
# Each number is a bit position (1-based) of R(i-1). The first and last bit of
# every row are copied from the neighbouring 4-bit groups, so 16 of the 32
# bits appear twice - that is how 32 bits become 48.
E_TABLE = [
    32,  1,  2,  3,  4,  5,
     4,  5,  6,  7,  8,  9,
     8,  9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32,  1,
]

K_BITS = 48  # size of the round key Ki
R_BITS = 32  # size of the right half R(i-1)
HEX_DIGITS = "0123456789abcdefABCDEF"  # characters allowed in hex input


def group(bits, size):
    # Insert a space every `size` bits for readability, e.g. "101100 011010 ..."
    return ' '.join(bits[i:i + size] for i in range(0, len(bits), size))


def to_hex(bits):
    # Convert a bit string to uppercase hex, keeping leading zeros
    # (one hex digit for every 4 bits)
    return format(int(bits, 2), f"0{len(bits) // 4}X")


def split_blocks(bits):
    # Split a 48-bit string into a list of eight 6-bit blocks
    return [bits[i:i + 6] for i in range(0, len(bits), 6)]


def parse_bits(text, n_bits):
    # Accepts n_bits binary digits or n_bits/4 hex digits, spaces ignored.
    # Returns the value as a string of n_bits '0'/'1' characters,
    # or None if the input is invalid.
    s = text.replace(' ', '')
    # Binary input: exactly n_bits characters, all 0 or 1
    if len(s) == n_bits and all(c in '01' for c in s):
        return s
    # Hex input: exactly n_bits/4 hex digits, converted to binary with leading zeros
    if len(s) == n_bits // 4 and all(c in HEX_DIGITS for c in s):
        return format(int(s, 16), f"0{n_bits}b")
    return None


def random_bits(n_bits):
    # Generate a random value of n_bits bits as a zero-padded binary string
    return format(random.getrandbits(n_bits), f"0{n_bits}b")


def xor_bits(a, b):
    # Bitwise XOR of two equal-length bit strings: 1 where the bits differ, 0 otherwise
    return ''.join('1' if x != y else '0' for x, y in zip(a, b))


def print_tables():
    # Print the expansion table E, one row per output block B1..B8
    print("Expansion table E (32 bits -> 48 bits):\n")
    print("  Block |" + ''.join(f"{c:>4}" for c in range(1, 7)))
    print("  ------+" + "-" * 24)
    for j in range(8):
        row = E_TABLE[6 * j:6 * j + 6]  # the 6 positions that form block Bj+1
        print(f"  B{j + 1:<4} |" + ''.join(f"{p:>4}" for p in row))

    # Print the truth table of XOR, used in step 2
    print("\nXOR table:\n")
    print("   a | b | a ⊕ b")
    print("  ---+---+------")
    for a in (0, 1):
        for b in (0, 1):
            print(f"   {a} | {b} |   {a ^ b}")
    print()


def expand(r, r_name):
    # STEP 1: apply the expansion E to the 32-bit half r.
    # Returns the 48-bit string E(r).

    # Show every bit of r with its position (1..32), in two rows of 16
    # so that the positions from table E can be looked up easily
    print(f"Bits of {r_name} by position:\n")
    for start in (1, 17):
        positions = range(start, start + 16)
        print("  Pos |" + ''.join(f"{p:>3}" for p in positions))
        print("  Bit |" + ''.join(f"{r[p - 1]:>3}" for p in positions))
        print()

    # Build each 6-bit block: take the positions listed in row j of E
    # and read the bits of r found at those positions
    print(f"Expanding {r_name} with table E:\n")
    for j in range(8):
        positions = E_TABLE[6 * j:6 * j + 6]
        values = [r[p - 1] for p in positions]  # p - 1 because positions in E are 1-based
        print(f"  Block {j + 1}: positions " + ''.join(f"{p:>3}" for p in positions))
        print(f"           bits      " + ''.join(f"{v:>3}" for v in values)
              + f"   -> {''.join(values)}")

    # Full expansion: the 48 output bits are r[p] for every p in E, in order
    expanded = ''.join(r[p - 1] for p in E_TABLE)
    print(f"\n  E({r_name}) = {group(expanded, 6)}  (hex {to_hex(expanded)})\n")
    return expanded


def xor_with_key(k, expanded, k_name, r_name):
    # STEP 2: compute Ki ⊕ E(R(i-1)) bit by bit (both are 48 bits).
    # Returns the 48-bit result.
    e_name = f"E({r_name})"
    result_name = f"{k_name} ⊕ {e_name}"
    width = len(result_name)  # used to right-align the labels below
    result = xor_bits(k, expanded)

    # Show the XOR as a column operation: key, expansion, separator line, result
    print(f"  {k_name:>{width}} = {group(k, 6)}")
    print(f"  {e_name:>{width}} = {group(expanded, 6)}")
    print(f"  {'':>{width}}   " + "-" * 55)
    print(f"  {result_name:>{width}} = {group(result, 6)}\n")

    # Show the same XOR split into the 8 blocks of 6 bits
    print("  Block by block:")
    for j, (kb, eb, rb) in enumerate(zip(split_blocks(k), split_blocks(expanded),
                                         split_blocks(result)), start=1):
        print(f"    B{j} = {kb} ⊕ {eb} = {rb}")
    print()
    return result


def print_result(result, k_name, r_name):
    # STEP 3: split the 48-bit result into B1..B8 and show each block
    # in binary and decimal (these are the inputs of S-boxes S1..S8)
    print(f"{k_name} ⊕ E({r_name}) = B1 B2 B3 B4 B5 B6 B7 B8\n")
    print("  Block | Bits   | Decimal")
    print("  ------+--------+--------")
    for j, b in enumerate(split_blocks(result), start=1):
        print(f"  B{j:<4} | {b} | {int(b, 2):>7}")
    print(f"\n  B1B2B3B4B5B6B7B8 = {group(result, 6)}")
    print(f"  B1B2B3B4B5B6B7B8 (hex) = {to_hex(result)}")


def compute_b(k, r, round_no):
    # Run the whole computation for round `round_no`:
    # k is the round key Ki (48 bits), r is the right half R(i-1) (32 bits)
    k_name = f"K{round_no}"
    r_name = f"R{round_no - 1}"  # round i uses the right half from the previous round

    # Show the input values in binary and hex
    print("\n=== INPUT DATA ===\n")
    print(f"  Round i = {round_no}")
    print(f"  {k_name} = {group(k, 6)}  (hex {to_hex(k)})")
    print(f"  {r_name} = {group(r, 4)}  (hex {to_hex(r)})\n")

    print("=== TABLES USED ===\n")
    print_tables()

    print("=== STEP 1: EXPANSION E ===\n")
    expanded = expand(r, r_name)  # 32 bits -> 48 bits

    print(f"=== STEP 2: {k_name} ⊕ E({r_name}) ===\n")
    result = xor_with_key(k, expanded, k_name, r_name)  # 48 bits ⊕ 48 bits

    print("=== STEP 3: SPLIT INTO B1...B8 ===\n")
    print_result(result, k_name, r_name)  # 48 bits -> 8 blocks of 6 bits


def read_round():
    # Ask for the round number until a valid value between 1 and 16 is entered
    # (DES has 16 rounds)
    while True:
        text = input("\nEnter round number i (1-16): ").strip()
        if text.isdigit() and 1 <= int(text) <= 16:
            return int(text)
        print("Round number must be an integer between 1 and 16!")


def read_bits(prompt, n_bits):
    # Ask for an n_bits value (binary or hex) until the input is valid
    while True:
        bits = parse_bits(input(prompt), n_bits)
        if bits is not None:
            return bits
        print(f"Invalid value! Enter {n_bits} binary digits or {n_bits // 4} hex digits.")


def main():
    print("DES Algorithm - Lab 4")
    print("Given Ki and R(i-1), compute B1B2B3B4B5B6B7B8 = Ki ⊕ E(R(i-1))\n")

    # The input data can be typed by the user or generated randomly
    print("Choose input mode:")
    print("1. Manual input")
    print("2. Random generation")

    choice = input("\nEnter option (1/2): ").strip()

    if choice == '1':
        # Manual input: round number, key Ki and right half R(i-1)
        round_no = read_round()
        k = read_bits(f"Enter K{round_no} (48 bits binary or 12 hex digits): ", K_BITS)
        r = read_bits(f"Enter R{round_no - 1} (32 bits binary or 8 hex digits): ", R_BITS)
    elif choice == '2':
        # Random input: random round, random 48-bit key and random 32-bit half
        round_no = random.randint(1, 16)
        k = random_bits(K_BITS)
        r = random_bits(R_BITS)
    else:
        print("Invalid option!")
        return

    compute_b(k, r, round_no)


# Run main() only when the file is executed directly, not when it is imported
if __name__ == "__main__":
    main()
