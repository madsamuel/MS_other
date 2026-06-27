# statlattice

A Rust CLI that prints a colorful pixel-art banner with a rainbow gradient and halftone drop shadow.

![statlattice banner](https://img.shields.io/badge/built%20with-Rust-orange)

## Build

```bash
cargo build --release
```

The binary will be at `target/release/statlattice` (or `statlattice.exe` on Windows).

## Usage

```
statlattice [OPTIONS]
```

### Options

| Flag | Short | Description |
|------|-------|-------------|
| `--spaced` | `-s` | Add a 1-column gap between letters |
| `--stacked` | `-2` | Split into two rows: **STAT** centered above **LATTICE** |

### Examples

**Default** — letters touching, single row:
```
statlattice
```

**Spaced** — 1-column gap between each letter:
```
statlattice --spaced
statlattice -s
```

**Stacked** — STAT centered on top, LATTICE on the bottom:
```
statlattice --stacked
statlattice -2
```

**Stacked + spaced** — both options together:
```
statlattice --stacked --spaced
```

## How it works

### Pixel-art glyphs

Each letter is defined as an `8×6` boolean grid (`[[bool; 6]; 8]`). `true` means a filled block (`██`), `false` means empty space. The glyphs are trimmed at render time — left/right columns that are entirely empty are stripped so letters pack tightly with no invisible padding.

### Rainbow gradient

Colors are computed using a left-to-right `0.0–1.0` parameter mapped through a 5-segment HSV-style cycle:

```
blue → cyan → green → yellow → red → magenta
```

True-color ANSI escape codes (`\x1b[38;2;R;G;Bm`) are used, so you need a terminal with 24-bit color support (Windows Terminal, VS Code terminal, iTerm2, etc.).

### Halftone drop shadow

Each filled pixel also casts a shadow offset **1 row down, 2 columns right**. The shadow uses a checkerboard pattern — only cells where `(row + col) % 2 == 0` are filled — giving the classic halftone/dithered look. Shadow pixels are darkened to ~18–25% brightness of the foreground color with a slight blue tint.

### Stacked mode centering

In `--stacked` mode, both rows are rendered at the width of the wider row (LATTICE). The narrower row (STAT) is offset by `(wider - narrower) / 2` pixel-columns of leading space so it appears visually centered. Both rows share the same rainbow gradient span so colors flow consistently across both lines.
