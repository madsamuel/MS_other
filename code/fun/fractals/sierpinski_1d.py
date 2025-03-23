def generate_sierpinski_1d(rows=16):
    """
    Generate and print a 1D Sierpinski triangle (Rule 90) for a given number of rows.
    """
    # The width is enough to hold the pattern.
    # A typical choice is 2*rows+1 so the middle cell can expand left and right
    width = 2 * rows + 1

    # Create the initial row with a single "1" in the center
    row = [0] * width
    row[width // 2] = 1

    for r in range(rows):
        # Convert the row bits to a string of '#' (for 1) and ' ' (for 0)
        line_str = ''.join('#' if cell else ' ' for cell in row)
        print(line_str)

        # Prepare the next row by applying Rule 90
        next_row = [0] * width
        for i in range(width):
            # The left neighbor is row[i-1], the right neighbor is row[i+1],
            # but we need to handle boundaries.
            left = row[i-1] if i-1 >= 0 else 0
            right = row[i+1] if i+1 < width else 0
            # Rule 90: next = left XOR right
            next_row[i] = left ^ right

        row = next_row

if __name__ == "__main__":
    # Generate 16 rows (you can change to any number you like)
    generate_sierpinski_1d(rows=16)
