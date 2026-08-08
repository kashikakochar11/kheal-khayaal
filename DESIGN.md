---
name: Luminous Care
colors:
  surface: '#101414'
  surface-dim: '#101414'
  surface-bright: '#353a3a'
  surface-container-lowest: '#0a0f0f'
  surface-container-low: '#181c1c'
  surface-container: '#1c2020'
  surface-container-high: '#262b2b'
  surface-container-highest: '#313635'
  on-surface: '#dfe3e2'
  on-surface-variant: '#bdc9c8'
  inverse-surface: '#dfe3e2'
  inverse-on-surface: '#2c3131'
  outline: '#879392'
  outline-variant: '#3e4949'
  surface-tint: '#76d6d5'
  primary: '#76d6d5'
  on-primary: '#003737'
  primary-container: '#008080'
  on-primary-container: '#e3fffe'
  inverse-primary: '#006a6a'
  secondary: '#deb7ff'
  on-secondary: '#4a007f'
  secondary-container: '#6b13af'
  on-secondary-container: '#d4a5ff'
  tertiary: '#ffb692'
  on-tertiary: '#552000'
  tertiary-container: '#a96039'
  on-tertiary-container: '#fff9f7'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#93f2f2'
  primary-fixed-dim: '#76d6d5'
  on-primary-fixed: '#002020'
  on-primary-fixed-variant: '#004f4f'
  secondary-fixed: '#f1dbff'
  secondary-fixed-dim: '#deb7ff'
  on-secondary-fixed: '#2d0050'
  on-secondary-fixed-variant: '#680eac'
  tertiary-fixed: '#ffdbcb'
  tertiary-fixed-dim: '#ffb692'
  on-tertiary-fixed: '#341100'
  on-tertiary-fixed-variant: '#733512'
  background: '#101414'
  on-background: '#dfe3e2'
  surface-variant: '#313635'
typography:
  brand-logo:
    fontFamily: Epilogue
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 34px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.5rem
  lg: 2rem
  xl: 3rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 16px
  md: 24px
  lg: 32px
  xl: 48px
  container-max: 1200px
  gutter: 20px
---

## Brand & Style

The design system is engineered for a professional health chatbot that balances medical authority with empathetic digital interaction. The brand personality is calm, reassuring, and technologically advanced, targeting users seeking reliable health guidance in a private, high-end environment.

The aesthetic follows a **Modern Tactile** approach. It evolves the principles of Neomorphism and Glassmorphism into a "Soft Realistic Depth" style. Interfaces are characterized by deep navy surfaces, soft inner glows, and subtle gradients that make UI elements feel like physical, high-quality medical instruments. The emotional response is one of security and precision, evoked through high-contrast accents against a sophisticated dark backdrop.

## Colors

The palette is rooted in a deep, nocturnal foundation to reduce eye strain during late-night health consultations.

- **Primary (Teal):** Used for "KHeal" branding and critical action paths. It represents health, vitality, and clinical precision.
- **Secondary (Purple):** Used for "Khayaal" branding and supportive accents. It adds warmth, empathy, and a premium feel.
- **Background:** A deep Navy (#0A1128) provides the base.
- **Overlays:** Medical doodles (hearts, capsules, smileys) should be applied as background watermarks at 15-20% opacity using the primary and secondary colors to add visual texture without distracting from the content.

## Typography

This design system utilizes a high-contrast typographic pairing. The brand identity uses **Epilogue** in a bold, italicized weight to simulate a sophisticated cursive script for the logo. For all functional UI elements, **Inter** provides a neutral, systematic, and highly legible foundation.

- **Brand Logo:** Use italicized weights to lean into the "cursive" requirement while maintaining modern geometric clarity.
- **Hierarchy:** Maintain a clear distinction between the chatbot's messages (Body-md) and system labels (Label-sm).
- **Readability:** Given the dark mode context, body text uses a slightly increased line height and a pure white or high-gray color to ensure maximum accessibility.

## Layout & Spacing

The layout is centered around a **Fluid Chat Interface**. On desktop, the chat occupies a central column (max 800px) to maintain focus. On mobile, it is a full-bleed edge-to-edge experience with safe area margins.

- **Grid:** A 12-column grid is used for dashboard views, while the chat experience relies on a 4-column mobile grid.
- **Rhythm:** An 8px linear scale governs all padding and margins. 
- **Chat Bubbles:** Use 12px horizontal spacing between the bubble and the screen edge, and 8px vertical spacing between consecutive messages from the same sender.

## Elevation & Depth

This design system utilizes **Soft Realistic Depth** to create a tactile user experience. 

- **Tactile Elements:** Buttons and the input bar use dual shadows: a dark drop shadow (offset 4px, 10% opacity) and a subtle light inner-shadow (1px, white, 15% opacity) on the top-left edge to simulate a "raised" surface.
- **Glassmorphism:** Cards and secondary containers use a backdrop-blur (12px to 20px) with a semi-transparent surface color (#FFFFFF at 5% opacity).
- **Borders:** Every glassmorphic card must have a 1px solid border with a gradient stroke (from white at 20% to white at 5%) to define the edge against the dark navy background.
- **Icons:** Icons should have a 3D "glossy" appearance, using internal gradients and a small radial highlight to simulate light reflecting off a glass or plastic surface.

## Shapes

The shape language is dominated by high-radius curves to convey friendliness and safety.

- **Pill Shapes:** Used for all buttons, chips, and the main chat input field.
- **Chat Bubbles:** Feature a 20px corner radius, with a sharp tail (4px radius) pointing toward the sender.
- **Cards:** Use the `rounded-xl` (48px) setting for large container surfaces to maintain the soft, organic feel of the brand.

## Components

- **Buttons:** Fully pill-shaped. Primary buttons use a Teal-to-Dark Teal linear gradient. They feature a soft outer glow in the primary color when focused.
- **Input Bar:** A floating pill-shaped container with a subtle inner-shadow to look recessed. It uses a high backdrop blur to separate it from the medical doodles moving underneath.
- **Glass Cards:** Used for health summaries and suggested actions. They must include a subtle 1px border and a backdrop filter.
- **Chips/Quick Replies:** Small pill-shaped buttons with a Purple (#7B2CBF) outline and a low-opacity fill. These are used for user responses to chatbot prompts.
- **3D Icons:** Functional icons (e.g., Send, Attachment, Profile) use a glossy treatment with a highlight on the upper-right quadrant.
- **Progress Indicators:** Use the Teal primary color with a glowing "pulse" effect for active states.