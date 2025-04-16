import numpy as np
import matplotlib.pyplot as plt

def rule_to_binary(rule_number):
    """Convert a rule number (0–255) to 8-bit binary rule list."""
    return [(rule_number >> i) & 1 for i in range(7, -1, -1)]

def get_next_gen(current_gen, rule_bin):
    """Compute next generation using the rule binary representation."""
    next_gen = np.zeros_like(current_gen)
    for i in range(1, len(current_gen) - 1):
        neighborhood = (current_gen[i - 1] << 2) | (current_gen[i] << 1) | current_gen[i + 1]
        next_gen[i] = rule_bin[7 - neighborhood]  # reverse indexing
    return next_gen

def generate_automaton(rule_number, width=101, steps=60):
    """Simulate the cellular automaton for the given rule number."""
    rule_bin = rule_to_binary(rule_number)
    grid = np.zeros((steps, width), dtype=int)
    grid[0, width // 2] = 1  # Start with a single '1' in the center

    for t in range(1, steps):
        grid[t] = get_next_gen(grid[t - 1], rule_bin)

    return grid

def plot_automaton(grid, rule_number):
    """Visualize the grid as an image."""
    plt.figure(figsize=(10, 6))
    plt.imshow(grid, cmap='binary', interpolation='nearest')
    plt.title(f"Elementary Cellular Automaton - Rule {rule_number}")
    plt.xlabel("Cell")
    plt.ylabel("Time Step")
    plt.tight_layout()
    plt.show()

# Run it!
if __name__ == "__main__":
    rule_number = 30
    grid = generate_automaton(rule_number=rule_number, width=1000, steps=600)
    plot_automaton(grid, rule_number)
