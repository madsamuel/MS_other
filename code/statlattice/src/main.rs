// Each letter is an 8-row x 6-col pixel grid (true = filled block)
type Glyph = [[bool; 6]; 8];

const S: Glyph = [
    [false, true,  true,  true,  true,  false],
    [true,  true,  false, false, false, false],
    [true,  true,  false, false, false, false],
    [false, true,  true,  true,  false, false],
    [false, false, false, true,  true,  false],
    [false, false, false, true,  true,  false],
    [false, true,  true,  true,  true,  false],
    [false, false, false, false, false, false],
];

const T: Glyph = [
    [true,  true,  true,  true,  true,  false],
    [false, false, true,  true,  false, false],
    [false, false, true,  true,  false, false],
    [false, false, true,  true,  false, false],
    [false, false, true,  true,  false, false],
    [false, false, true,  true,  false, false],
    [false, false, true,  true,  false, false],
    [false, false, false, false, false, false],
];

const A: Glyph = [
    [false, false, true,  true,  false, false],
    [false, true,  true,  true,  true,  false],
    [true,  true,  false, false, true,  true],
    [true,  true,  false, false, true,  true],
    [true,  true,  true,  true,  true,  true],
    [true,  true,  false, false, true,  true],
    [true,  true,  false, false, true,  true],
    [false, false, false, false, false, false],
];

const L: Glyph = [
    [true,  true,  false, false, false, false],
    [true,  true,  false, false, false, false],
    [true,  true,  false, false, false, false],
    [true,  true,  false, false, false, false],
    [true,  true,  false, false, false, false],
    [true,  true,  false, false, false, false],
    [true,  true,  true,  true,  true,  true],
    [false, false, false, false, false, false],
];

const I: Glyph = [
    [false, true,  true,  true,  true,  false],
    [false, false, true,  true,  false, false],
    [false, false, true,  true,  false, false],
    [false, false, true,  true,  false, false],
    [false, false, true,  true,  false, false],
    [false, false, true,  true,  false, false],
    [false, true,  true,  true,  true,  false],
    [false, false, false, false, false, false],
];

const C: Glyph = [
    [false, true,  true,  true,  true,  false],
    [true,  true,  false, false, false, false],
    [true,  true,  false, false, false, false],
    [true,  true,  false, false, false, false],
    [true,  true,  false, false, false, false],
    [true,  true,  false, false, false, false],
    [false, true,  true,  true,  true,  false],
    [false, false, false, false, false, false],
];

const E: Glyph = [
    [true,  true,  true,  true,  true,  false],
    [true,  true,  false, false, false, false],
    [true,  true,  false, false, false, false],
    [true,  true,  true,  true,  false, false],
    [true,  true,  false, false, false, false],
    [true,  true,  false, false, false, false],
    [true,  true,  true,  true,  true,  false],
    [false, false, false, false, false, false],
];

/// Rainbow gradient: maps a 0.0–1.0 position to an RGB color.
fn rainbow_rgb(t: f32) -> (u8, u8, u8) {
    let t = t.clamp(0.0, 1.0) * 5.0;
    let (r, g, b) = if t < 1.0 {
        (0, (t * 255.0) as u8, 255)
    } else if t < 2.0 {
        (0, 255, ((2.0 - t) * 255.0) as u8)
    } else if t < 3.0 {
        (((t - 2.0) * 255.0) as u8, 255, 0)
    } else if t < 4.0 {
        (255, ((4.0 - t) * 255.0) as u8, 0)
    } else {
        (255, 0, ((t - 4.0) * 255.0) as u8)
    };
    (r, g, b)
}

fn print_truecolor(text: &str, r: u8, g: u8, b: u8) {
    print!("\x1b[38;2;{r};{g};{b}m{text}\x1b[0m");
}

/// Returns true if glyph-space (row, col) is a lit pixel in the banner.
/// Uses per-glyph trimmed bounds so letters touch with no padding gap.
fn glyph_lit(glyphs: &[&Glyph], trims: &[(usize, usize)], offsets: &[usize], row: usize, col: usize) -> bool {
    if row >= 8 {
        return false;
    }
    let gi = offsets.partition_point(|&o| o <= col).saturating_sub(1);
    if gi >= glyphs.len() {
        return false;
    }
    let local = col - offsets[gi];
    let (left, right) = trims[gi];
    let gc = left + local;
    if gc > right {
        return false;
    }
    glyphs[gi][row][gc]
}

/// Compute (left_trim, right_trim) for each glyph — the tightest non-empty column bounds.
fn compute_trims(glyphs: &[&Glyph]) -> Vec<(usize, usize)> {
    glyphs.iter().map(|g| {
        let w = g[0].len();
        let left  = (0..w).find(|&c| (0..8).any(|r| g[r][c])).unwrap_or(0);
        let right = (0..w).rev().find(|&c| (0..8).any(|r| g[r][c])).unwrap_or(w - 1);
        (left, right)
    }).collect()
}

fn render_banner_with_shadow(glyphs: &[&Glyph], gap: usize) {
    let trims = compute_trims(glyphs);
    let n = glyphs.len();
    let gaps = vec![gap; n.saturating_sub(1)];
    let shared_width = row_width(&trims, &gaps);
    render_row_with_shadow(glyphs, &trims, &gaps, shared_width);
}

fn render_stacked(base_gap: usize) {
    let row1: &[&Glyph] = &[&S, &T, &A, &T];
    let row2: &[&Glyph] = &[&L, &A, &T, &T, &I, &C, &E];

    let trims1 = compute_trims(row1);
    let trims2 = compute_trims(row2);

    let gaps1: Vec<usize> = vec![base_gap; row1.len() - 1];
    let gaps2: Vec<usize> = vec![base_gap; row2.len() - 1];
    let w1 = row_width(&trims1, &gaps1);
    let w2 = row_width(&trims2, &gaps2);
    let shared_width = w1.max(w2);

    // Center the narrower row by padding with leading spaces
    let pad1 = (shared_width.saturating_sub(w1)) / 2;
    let pad2 = (shared_width.saturating_sub(w2)) / 2;

    // Each "col" in render_row is a glyph-pixel col; each prints 2 terminal chars ("██")
    // so we print pad * 2 spaces before the row
    render_row_with_shadow_padded(row1, &trims1, &gaps1, shared_width, pad1);
    render_row_with_shadow_padded(row2, &trims2, &gaps2, shared_width, pad2);
}

fn row_width(trims: &[(usize, usize)], gaps: &[usize]) -> usize {
    let tight: usize = trims.iter().map(|(l, r)| r - l + 1).sum();
    let gap_total: usize = gaps.iter().sum();
    tight + gap_total
}

fn render_row_with_shadow(glyphs: &[&Glyph], trims: &[(usize, usize)], gaps: &[usize], shared_width: usize) {
    render_row_with_shadow_padded(glyphs, trims, gaps, shared_width, 0);
}

fn render_row_with_shadow_padded(glyphs: &[&Glyph], trims: &[(usize, usize)], gaps: &[usize], shared_width: usize, pad: usize) {
    let mut offsets = vec![0usize; glyphs.len()];
    for i in 1..glyphs.len() {
        let (l, r) = trims[i - 1];
        offsets[i] = offsets[i - 1] + (r - l + 1) + gaps[i - 1];
    }
    let (last_l, last_r) = trims[glyphs.len() - 1];
    let total_glyph_cols = offsets[glyphs.len() - 1] + (last_r - last_l + 1);

    const SHADOW_DR: usize = 1;
    const SHADOW_DC: usize = 2;
    let render_rows = 8 + SHADOW_DR;
    let render_cols = total_glyph_cols + SHADOW_DC;

    for row in 0..render_rows {
        // Leading padding (each pixel-col = 2 terminal chars)
        if pad > 0 {
            print!("{}", "  ".repeat(pad));
        }
        for col in 0..render_cols {
            let is_main   = glyph_lit(glyphs, trims, &offsets, row, col);
            let is_shadow = row >= SHADOW_DR
                && col >= SHADOW_DC
                && glyph_lit(glyphs, trims, &offsets, row - SHADOW_DR, col - SHADOW_DC);

            // gradient anchored to shared_width so both rows share same rainbow span
            let t = (pad + col) as f32 / (shared_width.max(1) as f32 - 1.0);

            if is_main {
                let (r, g, b) = rainbow_rgb(t);
                print_truecolor("██", r, g, b);
            } else if is_shadow {
                if (row + col) % 2 == 0 {
                    let (r, g, b) = rainbow_rgb(t);
                    let sr = (r as f32 * 0.18 + 20.0) as u8;
                    let sg = (g as f32 * 0.12 + 10.0) as u8;
                    let sb = (b as f32 * 0.25 + 30.0) as u8;
                    print_truecolor("██", sr, sg, sb);
                } else {
                    print!("  ");
                }
            } else {
                print!("  ");
            }
        }
        println!();
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let spaced  = args.iter().any(|a| a == "--spaced"  || a == "-s");
    let stacked = args.iter().any(|a| a == "--stacked" || a == "-2");
    let gap = if spaced { 1 } else { 0 };

    let glyphs: &[&Glyph] = &[&S, &T, &A, &T, &L, &A, &T, &T, &I, &C, &E];

    println!();
    if stacked {
        render_stacked(gap);
    } else {
        render_banner_with_shadow(glyphs, gap);
    }

    // Rainbow separator line
    let width = 80usize;
    for i in 0..width {
        let t = i as f32 / (width - 1) as f32;
        let (r, g, b) = rainbow_rgb(t);
        print_truecolor("─", r, g, b);
    }
    println!();

    // Centered tagline
    let tagline = "  Statistical Lattice Framework";
    println!();
    print_truecolor(tagline, 80, 220, 200);
    println!();
    println!();

    // Description
    println!("statlattice is a framework for building and analyzing statistical lattice models.");
    println!();
    print_truecolor("Usage: ", 80, 220, 80);
    print_truecolor("statlattice", 255, 200, 80);
    print_truecolor(" [OPTIONS] ", 100, 180, 255);
    print_truecolor("<COMMAND>", 255, 100, 180);
    println!();
    println!();
}

