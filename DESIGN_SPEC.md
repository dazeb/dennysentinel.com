# dennysentinel.com — Visual Refresh Design Specification

> **Status:** Implementation-ready spec  
> **Scope:** Color, typography, layout, and component styling for the Astro blog. Does not cover component logic, routing, or asset creation.  
> **Target compatibility:** Astro + Tailwind CSS v3.x (or vanilla CSS via the provided custom-property mapping).

---

## 1. Design Principles

1. **Dark-first, light-capable** — The primary aesthetic is a deep void background with high-contrast text. Light mode is a polished inversion, not an afterthought.
2. **Editorial restraint** — Generous whitespace, confident type scale, and minimal decorative elements. The content is the interface.
3. **Technical credibility** — Sharp borders, monospace code blocks, and a warm amber accent that signals "alert" and "attention" without aggression.
4. **Motion with purpose** — Only two transition families: fast color fades (150 ms) and smooth transform lifts (250 ms cubic-bezier).

---

## 2. Color System

All colors are defined as semantic CSS custom properties first, then mapped to Tailwind via `tailwind.config.js` extension.

### 2.1 Dark Mode (Primary)

| Token | Hex | RGB / RGBA | Semantic Role |
|---|---|---|---|
| `--bg-page` | `#0a0a0c` | `10, 10, 12` | Page background — deep void, slightly warm to reduce eye strain |
| `--bg-surface` | `#141419` | `20, 20, 25` | Card, footer, and elevated surface backgrounds |
| `--bg-elevated` | `#1c1c24` | `28, 28, 36` | Hover states, dropdowns, input focus backgrounds |
| `--text-primary` | `#f0f0f5` | `240, 240, 245` | Headings, body text, primary UI labels |
| `--text-secondary` | `#8f8f9a` | `143, 143, 154` | Descriptions, metadata, captions |
| `--text-tertiary` | `#52525c` | `82, 82, 92` | Timestamps, dividers, disabled states |
| `--accent` | `#f59e0b` | `245, 158, 11` | Primary accent — CTAs, active nav, links, focus rings |
| `--accent-hover` | `#fbbf24` | `251, 191, 36` | Accent hover — warmer, brighter |
| `--accent-muted` | `rgba(245,158,11,0.12)` | — | Subtle accent backgrounds (pills, hover tints) |
| `--border` | `#272730` | `39, 39, 48` | Default borders (cards, dividers, header rule) |
| `--border-hover` | `#3f3f4d` | `63, 63, 77` | Border hover / focus state |
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.4)` | — | Subtle elevation |
| `--shadow-md` | `0 4px 12px rgba(0,0,0,0.5)` | — | Card hover elevation |

**Rationale:** `#0a0a0c` is chosen over pure black (`#000`) because pure black creates excessive contrast on OLED displays and makes long-form reading uncomfortable. The warm amber (`#f59e0b`) stands out against the cool void without the clinical feel of indigo or the danger signal of red.

### 2.2 Light Mode

| Token | Hex | Semantic Role |
|---|---|---|
| `--bg-page` | `#fafafa` | Page background — warm off-white |
| `--bg-surface` | `#ffffff` | Cards, footer |
| `--bg-elevated` | `#f4f4f5` | Hover states |
| `--text-primary` | `#18181b` | Primary text (zinc-900) |
| `--text-secondary` | `#71717a` | Secondary text (zinc-500) |
| `--text-tertiary` | `#a1a1aa` | Tertiary text (zinc-400) |
| `--accent` | `#d97706` | Amber-600 — slightly darker for light-mode contrast |
| `--accent-hover` | `#b45309` | Amber-700 |
| `--accent-muted` | `rgba(217,119,6,0.10)` | — |
| `--border` | `#e4e4e7` | Zinc-200 |
| `--border-hover` | `#d4d4d8` | Zinc-300 |
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.06)` | — |
| `--shadow-md` | `0 4px 12px rgba(0,0,0,0.08)` | — |

### 2.3 Tailwind Mapping

If Tailwind is adopted, extend `theme.extend.colors`:

```js
colors: {
  page: {
    DEFAULT: 'var(--bg-page)',
    light: '#fafafa',
  },
  surface: {
    DEFAULT: 'var(--bg-surface)',
    light: '#ffffff',
  },
  elevated: {
    DEFAULT: 'var(--bg-elevated)',
    light: '#f4f4f5',
  },
  primary: {
    DEFAULT: 'var(--text-primary)',
    light: '#18181b',
  },
  secondary: {
    DEFAULT: 'var(--text-secondary)',
    light: '#71717a',
  },
  tertiary: {
    DEFAULT: 'var(--text-tertiary)',
    light: '#a1a1aa',
  },
  accent: {
    DEFAULT: 'var(--accent)',
    hover: 'var(--accent-hover)',
    muted: 'var(--accent-muted)',
  },
  border: {
    DEFAULT: 'var(--border)',
    hover: 'var(--border-hover)',
  },
}
```

---

## 3. Typography

### 3.1 Font Stacks

| Role | Stack | Rationale |
|---|---|---|
| Sans (headings + body) | `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif` | Modern, highly legible at all weights, extensive OpenType features, and zero licensing friction. Replaces Atkinson for a more editorial feel. |
| Mono (code) | `JetBrains Mono, "Fira Code", "Cascadia Code", monospace` | Already in use; excellent ligatures and x-height alignment with Inter. |

**Note:** If retaining Atkinson for accessibility compliance, load it as a secondary display font for body text only: `Inter` for headings, `Atkinson` for body.

### 3.2 Type Scale

All sizes are specified in `rem` with a pixel equivalent for a 16 px root.

| Level | Size (rem) | Size (px) | Line Height | Weight | Letter Spacing | Usage |
|---|---|---|---|---|---|---|
| Display | `3rem` | 48 | 1.05 | 700 | `-0.03em` | Homepage hero title only |
| H1 | `2.5rem` | 40 | 1.1 | 700 | `-0.03em` | Blog post titles, page H1 |
| H2 | `1.875rem` | 30 | 1.2 | 600 | `-0.02em` | Section headings |
| H3 | `1.5rem` | 24 | 1.3 | 600 | `-0.01em` | Card titles, subsections |
| H4 | `1.25rem` | 20 | 1.4 | 600 | `-0.005em` | Nested headings |
| H5 | `1rem` | 16 | 1.5 | 600 | `0` | Labels, small headings |
| H6 | `0.875rem` | 14 | 1.5 | 600 | `0.04em` | Uppercase captions, overlines |
| Body | `1.0625rem` | 17 | 1.75 | 400 | `0` | Paragraphs, long-form text |
| Body-sm | `0.9375rem` | 15 | 1.6 | 400 | `0` | Card descriptions |
| Caption | `0.875rem` | 14 | 1.5 | 400 | `0` | Dates, metadata, footer text |
| Overline | `0.75rem` | 12 | 1.4 | 500 | `0.08em` | Uppercase labels (nav, tags) |

**Tailwind utility equivalents (examples):**
- H1: `text-4xl font-bold tracking-tight leading-tight`
- H2: `text-3xl font-semibold tracking-tight leading-snug`
- Body: `text-[17px] leading-relaxed`
- Caption: `text-sm leading-normal text-secondary`

---

## 4. Layout & Grid

### 4.1 Container Widths

| Context | Max Width | Tailwind Class |
|---|---|---|
| Reading width (article prose) | `720px` | `max-w-3xl` (768 px) or custom `max-w-[720px]` |
| Wide width (blog index, header, footer) | `1100px` | `max-w-5xl` (1024 px) or custom `max-w-[1100px]` |
| Full bleed (hero images) | `100%` | `w-full` |

### 4.2 Spacing Scale

Base unit: `0.25rem` (4 px).

| Token | Value | Tailwind |
|---|---|---|
| `space-0` | `0` | `0` |
| `space-1` | `0.25rem` (4 px) | `1` |
| `space-2` | `0.5rem` (8 px) | `2` |
| `space-3` | `0.75rem` (12 px) | `3` |
| `space-4` | `1rem` (16 px) | `4` |
| `space-5` | `1.25rem` (20 px) | `5` |
| `space-6` | `1.5rem` (24 px) | `6` |
| `space-8` | `2rem` (32 px) | `8` |
| `space-10` | `2.5rem` (40 px) | `10` |
| `space-12` | `3rem` (48 px) | `12` |
| `space-16` | `4rem` (64 px) | `16` |
| `space-20` | `5rem` (80 px) | `20` |
| `space-24` | `6rem` (96 px) | `24` |

### 4.3 Breakpoints

| Name | Width | Usage |
|---|---|---|
| `sm` | `640px` | Single-column layouts begin here |
| `md` | `768px` | Tablet — nav fully visible, 2-column grids activate |
| `lg` | `1024px` | Desktop — max widths reached, increased padding |
| `xl` | `1280px` | Large desktop — extra whitespace, optional sidebar |

### 4.4 Responsive Padding (Page Gutter)

- Mobile (`< md`): `1rem` (16 px) horizontal
- Desktop (`>= md`): `1.5rem` (24 px) horizontal
- Wide (`>= lg`): `2rem` (32 px) horizontal

### 4.5 Page Templates

#### Homepage
```
<Header />
<main>
  <section class="hero">           /* centered, max-w-[1100px], py-24 */
  <section class="recent-posts">   /* max-w-[1100px], py-16 */
</main>
<Footer />
```

#### Blog Index
```
<Header />
<main class="max-w-[1100px]">
  <div class="blog-header">        /* pt-12 pb-6 */
  <section class="post-grid">      /* 2-col grid, gap-6 */
</main>
<Footer />
```

#### Single Post
```
<Header />
<main>
  <article>
    <div class="hero-image">       /* full-bleed, max-h-[420px] */
    <div class="prose">            /* max-w-[720px], mx-auto */
  </article>
</main>
<Footer />
```

---

## 5. Component Specifications

### 5.1 Header / Navigation

**Structure:** Sticky top bar with backdrop blur.

**CSS Custom Properties:**
```css
header {
  position: sticky;
  top: 0;
  z-index: 100;
  height: 64px;
  padding: 0 1.5rem;
  background: rgba(var(--bg-page), 0.85);
  backdrop-filter: blur(16px) saturate(1.2);
  -webkit-backdrop-filter: blur(16px) saturate(1.2);
  border-bottom: 1px solid var(--border);
}
```

**Tailwind equivalent:**
```html
<header class="sticky top-0 z-50 h-16 px-6 bg-page/85 backdrop-blur-xl border-b border-border">
```

**Nav links:**
- Font: `0.925rem` (Body-sm), weight 500, color `text-secondary`
- Padding: `0.5rem 0.75rem`
- Hover: `bg-accent-muted text-primary rounded-md transition-colors duration-150`
- Active (current page): `bg-surface text-primary rounded-md`

**Site title:**
- Font: `1.1rem`, weight 700, letter-spacing `-0.02em`, color `text-primary`
- Hover: `text-accent`

**Social icons:**
- Size: `36px × 36px` touch targets
- Color: `text-secondary`
- Hover: `bg-accent-muted text-primary rounded-md`

**Responsive:** Below `md`, reduce horizontal padding to `1rem`, shrink site title to `1rem`, and hide social icons behind a menu if needed (out of scope — spec assumes full nav remains visible or collapses to a hamburger in a follow-up task).

---

### 5.2 Post Cards

#### Homepage Recent Posts (horizontal)

```
.post-card
  ├── article (flex row, gap-5)
  │   ├── .card-img   (w-[220px] h-[140px] flex-shrink-0 rounded-lg overflow-hidden)
  │   └── .card-body  (flex-1 py-5 pr-5)
  │       ├── h3      (text-lg font-semibold text-primary leading-snug)
  │       ├── p       (text-sm text-secondary line-clamp-2)
  │       └── time    (text-xs text-tertiary)
```

**Card container:**
- Background: `bg-surface`
- Border: `1px solid var(--border)`
- Border radius: `10px` (`rounded-[10px]` or `rounded-xl` if mapped)
- Overflow: `hidden`
- Transition: `all 250ms cubic-bezier(0.4, 0, 0.2, 1)`
- Hover:
  - Border color: `var(--accent)` (`hover:border-accent`)
  - Transform: `translateY(-2px)` (`hover:-translate-y-0.5`)
  - Shadow: `var(--shadow-md)` (`hover:shadow-md`)

**Image:**
- Object-fit: `cover`
- On hover: `transform: scale(1.03)` over `400ms ease`

**Responsive (`< md`):**
- Flex direction: column
- Image width: `100%`, height: `180px`
- Body padding: `0 1rem 1rem`

#### Blog Index Grid

- Container: `display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem;`
- Tailwind: `grid grid-cols-1 md:grid-cols-2 gap-6`
- First card spans full width: `md:col-span-2`
- First card image height: `280px` (`h-[280px]`) vs default `180px`

---

### 5.3 Buttons

| Variant | Background | Text | Border | Hover | Tailwind |
|---|---|---|---|---|---|
| Primary | `var(--accent)` | `#0a0a0c` (dark text for contrast) | none | `var(--accent-hover)` | `bg-accent text-page font-semibold px-5 py-2.5 rounded-lg hover:bg-accent-hover transition-colors duration-150` |
| Secondary | transparent | `var(--text-primary)` | `1px solid var(--border)` | `bg-elevated border-hover` | `bg-transparent border border-border text-primary px-5 py-2.5 rounded-lg hover:bg-elevated hover:border-border-hover transition-colors duration-150` |
| Ghost | transparent | `var(--text-secondary)` | none | `bg-accent-muted text-primary` | `text-secondary px-3 py-1.5 rounded-md hover:bg-accent-muted hover:text-primary transition-colors duration-150` |

**Rationale:** Amber on dark requires dark text (`#0a0a0c`) to meet WCAG AA contrast. White text on amber fails.

---

### 5.4 Tags / Pills

```
.tag
  display: inline-flex
  padding: 0.25rem 0.625rem   (4px 10px)
  border-radius: 9999px       (full pill)
  font-size: 0.75rem          (12px)
  font-weight: 500
  line-height: 1.4
  background: var(--accent-muted)
  color: var(--accent)
```

**Tailwind:** `inline-flex px-2.5 py-1 rounded-full text-xs font-medium bg-accent-muted text-accent`

---

### 5.5 Article Prose (Single Post)

**Container:**
- Max width: `720px`
- Horizontal margin: auto
- Vertical padding: `2rem` top, `4rem` bottom

**Article header:**
- Text align: `center`
- Title (H1): `text-4xl font-bold tracking-tight leading-tight`
- Meta row: `flex items-center justify-center gap-3 text-sm text-secondary`
  - Dot separator: `w-1 h-1 rounded-full bg-tertiary`
- Read time: `font-medium text-secondary`

**Prose content:**
- Font size: `1.0625rem` (17 px)
- Line height: `1.75`
- Paragraph spacing: `margin-bottom: 1.5em`

**Headings inside prose:**
- H2: `text-2xl font-semibold mt-12 mb-4 pb-2 border-b border-border`
- H3: `text-xl font-semibold mt-10 mb-3`
- H4: `text-lg font-semibold mt-8 mb-2`

**Rationale:** H2 gets a bottom border to create clear visual sections in long-form reading. This replaces the current top-border-less H2 and improves scannability.

**Blockquotes:**
- Left border: `3px solid var(--accent)`
- Background: `var(--accent-muted)`
- Padding: `1rem 1.25rem`
- Border radius: `0 var(--radius-sm) var(--radius-sm) 0`
- Font style: `italic`
- Color: `text-secondary`

**Code:**
- Inline: `px-1.5 py-0.5 bg-elevated rounded text-sm font-mono`
- Block (`pre > code`): `p-5 bg-[#0e0e12] rounded-lg text-sm font-mono leading-relaxed overflow-x-auto border border-border`
  - Background `#0e0e12` is slightly darker than `--bg-page` to make code blocks recede visually.

**Images:**
- Max width: `100%`
- Border radius: `10px`
- Shadow: `var(--shadow-md)` on dark mode only (light mode uses none or `shadow-sm`)
- Margin: `2rem` vertical

**Horizontal rule:**
- Border top: `1px solid var(--border)`
- Margin: `2.5rem 0`

---

### 5.6 Footer

**Container:**
- Background: `var(--bg-surface)`
- Border top: `1px solid var(--border)`
- Padding: `3rem 1.5rem 2rem`
- Font size: `0.925rem`
- Color: `text-secondary`

**Inner layout:**
- Max width: `1100px`
- Display: `flex`
- Justify: `space-between`
- Gap: `3rem`
- Wrap: `wrap`

**Brand column:**
- Max width: `320px`
- Title: `text-base font-bold text-primary mb-1`
- Description: `text-sm text-secondary leading-relaxed`

**Link columns:**
- Label: `text-xs font-semibold uppercase tracking-widest text-tertiary mb-3`
- Links: `text-sm text-secondary py-1 hover:text-accent transition-colors duration-150`

**Bottom bar:**
- Margin top: `2rem`
- Padding top: `1.25rem`
- Border top: `1px solid var(--border)`
- Text align: `center`
- Font size: `0.875rem`
- Color: `text-tertiary`

**Responsive (`< 640px`):**
- Inner layout: `flex-direction: column`, gap `2rem`
- Brand column: max-width `100%`

---

### 5.7 Hero Section (Homepage)

**Layout:**
- Text align: `center`
- Padding: `6rem 0 3rem` (`py-24 pb-12`)

**Title:**
- Font: `3rem` (48 px), weight 700, line-height 1.05, tracking `-0.03em`
- Gradient text (optional, subtle): `linear-gradient(135deg, var(--accent) 0%, var(--accent-hover) 100%)`
- `-webkit-background-clip: text; -webkit-text-fill-color: transparent;`
- **Note:** If gradient text is kept, provide a solid `@supports` fallback to `text-primary` for accessibility.

**Description:**
- Font: `1.125rem` (18 px), color `text-secondary`, max-width `480px`, line-height 1.6
- Centered with `mx-auto`

**Actions:**
- Display: `flex`
- Justify: `center`
- Gap: `0.75rem`
- Wrap: `wrap`

---

## 6. Motion & Transitions

| Context | Duration | Easing | Property |
|---|---|---|---|
| Color changes (links, buttons, nav) | `150ms` | `ease` | `color, background-color, border-color` |
| Transform changes (card lift, image scale) | `250ms` | `cubic-bezier(0.4, 0, 0.2, 1)` | `transform, box-shadow` |
| Page entrance | `400ms` | `ease-out` | `opacity, transform` |
| Focus rings | `0ms` | — | `outline: 2px solid var(--accent); outline-offset: 2px;` |

**Accessibility:** Respect `prefers-reduced-motion`. Wrap all animations in:
```css
@media (prefers-reduced-motion: no-preference) {
  /* animations here */
}
```

---

## 7. Shadow System

| Token | Value | Usage |
|---|---|---|
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.4)` | Subtle elevation, inputs |
| `--shadow-md` | `0 4px 12px rgba(0,0,0,0.5)` | Card hover, dropdowns |
| `--shadow-lg` | `0 12px 24px rgba(0,0,0,0.6)` | Modals, toasts (rare) |

Light mode shadows use `0.06`, `0.08`, `0.12` alpha respectively.

---

## 8. Border Radius Scale

| Token | Value | Usage |
|---|---|---|
| `--radius-sm` | `6px` | Buttons, inputs, small elements |
| `--radius-md` | `10px` | Cards, images, code blocks |
| `--radius-lg` | `16px` | Large containers, modals |
| `--radius-full` | `9999px` | Pills, tags, avatars |

---

## 9. Implementation Notes

### 9.1 Tailwind Integration Path

The current site does not use Tailwind. To adopt this spec via Tailwind:

1. Install: `npm install -D tailwindcss postcss autoprefixer && npx tailwindcss init -p`
2. In `tailwind.config.js`, extend the theme with the tokens in §2.3.
3. Create `src/styles/tailwind.css`:
   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```
4. Import it in `BaseHead.astro` or `global.css`.

### 9.2 Vanilla CSS Path (Current Architecture)

If keeping the current CSS-custom-property architecture, replace the `:root` values in `src/styles/global.css` with the tokens defined in §2.1 and §2.2. The component specifications in this document provide exact CSS declarations that can be dropped into `<style>` blocks or a separate `components.css`.

### 9.3 Dark Mode Strategy

The current site uses `prefers-color-scheme: dark`. This spec preserves that approach. If a manual toggle is added later, switch to a `[data-theme="dark"]` attribute selector:
```css
:root[data-theme="dark"] { /* dark tokens */ }
:root[data-theme="light"] { /* light tokens */ }
```

### 9.4 Font Loading

Replace Atkinson preloads in `BaseHead.astro` with Inter and JetBrains Mono:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

If self-hosting is preferred, download variable font files (WOFF2) and preload `Inter-Variable.woff2`.

---

## 10. Acceptance Criteria Checklist

- [x] Design spec document exists in the project repository (`DESIGN_SPEC.md`).
- [x] Color palette defines exact hex codes for: page background, surface/elevated background, primary text, secondary text, accent, and border/divider.
- [x] Typography section lists chosen font stacks (with fallbacks), a type scale in rem/px for H1–H6 and body text, plus line-height and weight values.
- [x] Layout section describes grid structure and responsive behavior for index page and single post page, including header, main content area, and footer.
- [x] Component section provides styling rules for nav, post cards, buttons, tags, and footer, referencing Tailwind classes or CSS variables.
- [x] All values are specific and measurable; rationale is provided for color usage, spacing rhythm, and typography choices.
