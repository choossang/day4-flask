---
name: Warm Minimalist Blog
colors:
  surface: '#fcf9f5'
  surface-dim: '#ddd9d6'
  surface-bright: '#fcf9f5'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f7f3f0'
  surface-container: '#f1edea'
  surface-container-high: '#ebe7e4'
  surface-container-highest: '#e5e2df'
  on-surface: '#1c1c1a'
  on-surface-variant: '#47473f'
  inverse-surface: '#31302e'
  inverse-on-surface: '#f4f0ed'
  outline: '#78776e'
  outline-variant: '#c8c7bc'
  surface-tint: '#5e604d'
  primary: '#5e604d'
  on-primary: '#ffffff'
  primary-container: '#f5f5dc'
  on-primary-container: '#6f705c'
  inverse-primary: '#c8c8b0'
  secondary: '#79564b'
  on-secondary: '#ffffff'
  secondary-container: '#fed0c1'
  on-secondary-container: '#79574c'
  tertiary: '#615c68'
  on-tertiary: '#ffffff'
  tertiary-container: '#f8f1ff'
  on-tertiary-container: '#716d79'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e4e4cc'
  primary-fixed-dim: '#c8c8b0'
  on-primary-fixed: '#1b1d0e'
  on-primary-fixed-variant: '#474836'
  secondary-fixed: '#ffdbcf'
  secondary-fixed-dim: '#e9bdae'
  on-secondary-fixed: '#2d150d'
  on-secondary-fixed-variant: '#5e3f35'
  tertiary-fixed: '#e7e0ee'
  tertiary-fixed-dim: '#cac4d1'
  on-tertiary-fixed: '#1d1a24'
  on-tertiary-fixed-variant: '#494550'
  background: '#fcf9f5'
  on-background: '#1c1c1a'
  surface-variant: '#e5e2df'
typography:
  display:
    fontFamily: Plus Jakarta Sans
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  h1:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  h2:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Work Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Work Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  label-md:
    fontFamily: Work Sans
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.4'
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 16px
  md: 24px
  lg: 48px
  xl: 80px
  container_max_width: 1120px
  gutter: 20px
---

## Brand & Style

This design system is anchored in the concept of "Digital Slow Living." It aims to provide a sanctuary for long-form reading and thoughtful curation, moving away from the frantic energy of traditional social feeds. The brand personality is calm, sophisticated, and intentional.

The visual style follows a **Minimalist** approach with a focus on tactile warmth. It prioritizes content over container, utilizing generous whitespace to reduce cognitive load. By combining high-end editorial aesthetics with modern functionalism, the interface feels less like a software tool and more like a high-quality paper journal.

## Colors

The palette is derived from natural, organic tones to evoke a sense of comfort and readability. 

*   **Primary (Warm Beige):** Used for large surface areas, headers, and backgrounds to establish the warm "paper" feel.
*   **Secondary (Soft Brown):** Reserved for primary actions, active states, and emphasis. It provides enough contrast against the beige to ensure accessibility.
*   **Neutral Palette:** Transitions from a near-white "Alabaster" for the main background to deep "Umber" for typography, ensuring a soft but legible reading experience without the harshness of pure black-on-white.

## Typography

This design system uses a dual-sans-serif pairing to maintain a modern edge while prioritizing legibility.

*   **Plus Jakarta Sans** is used for headings. Its soft curves and modern geometry complement the warm color palette, making titles feel welcoming yet professional.
*   **Work Sans** is the workhorse for body text and labels. Its optimized metrics ensure that long-form blog posts remain readable on mobile screens.

Line heights are intentionally generous (1.6x for body text) to allow the text to "breathe," essential for a blog-focused interface.

## Layout & Spacing

The layout employs a **Fluid Grid** model with a mobile-first philosophy. 

On mobile devices, margins are kept at `md` (24px) to maximize screen real estate while maintaining a premium feel. On desktop, the content is constrained to a `container_max_width` of 1120px to prevent line lengths from becoming too long for comfortable reading. 

Vertical rhythm is strictly enforced using multiples of 8px, with extra-large (`xl`) spacing used between major sections to emphasize the "minimalist" aesthetic.

## Elevation & Depth

This design system eschews heavy drop shadows in favor of **Tonal Layers** and **Low-Contrast Outlines**. 

Depth is communicated through subtle shifts in background color (e.g., a card being slightly lighter than the page background). Where separation is strictly necessary, use a 1px solid border in a shade slightly darker than the primary beige. This creates a "flat-layered" look that feels architectural rather than artificial. For interactive elements like cards, a very soft, diffused ambient shadow (40% blur, 5% opacity brown tint) may be used upon hover to signal interactivity.

## Shapes

The shape language is **Soft**. 

A base radius of `0.25rem` (4px) is applied to standard UI elements like input fields and small buttons. Larger components, such as blog post cards and featured image containers, utilize `rounded-lg` (8px) to soften the overall visual impact. This subtle rounding maintains a clean, modern structure without appearing too "bubbly" or juvenile, preserving the sophisticated editorial tone.

## Components

*   **Buttons:** Primary buttons use the Secondary Brown color with white or cream text. They are medium-sized with generous horizontal padding. Secondary buttons use a simple brown outline or a tonal beige shift.
*   **Cards:** The primary container for blog posts. Cards should have no border, utilizing a subtle background color shift (Primary Beige) and `rounded-lg` corners. Typography inside cards should have a clear hierarchy: Label (Category) > H2 (Title) > Body-MD (Excerpt).
*   **Chips/Tags:** Used for categories. These should be pill-shaped with a slightly darker beige background and `label-md` typography.
*   **Input Fields:** Ghost-style inputs with a 1px border in a muted brown. Focus states should transition the border color to the Secondary Brown without adding a glow.
*   **Article Header:** High-contrast `display` typography centered with ample `xl` spacing below it.
*   **Navigation:** A simple, sticky top bar with text-only links to maintain the minimalist focus. Use `label-md` for navigation items to differentiate them from body content.