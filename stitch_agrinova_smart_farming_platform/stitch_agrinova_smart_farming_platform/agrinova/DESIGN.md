---
name: AgriNova
colors:
  surface: '#f7f9fc'
  surface-dim: '#d8dadd'
  surface-bright: '#f7f9fc'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f7'
  surface-container: '#eceef1'
  surface-container-high: '#e6e8eb'
  surface-container-highest: '#e0e3e6'
  on-surface: '#191c1e'
  on-surface-variant: '#40493d'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f4'
  outline: '#707a6c'
  outline-variant: '#bfcaba'
  surface-tint: '#1b6d24'
  primary: '#0d631b'
  on-primary: '#ffffff'
  primary-container: '#2e7d32'
  on-primary-container: '#cbffc2'
  inverse-primary: '#88d982'
  secondary: '#006e1c'
  on-secondary: '#ffffff'
  secondary-container: '#98f994'
  on-secondary-container: '#0c7521'
  tertiary: '#00569f'
  on-tertiary: '#ffffff'
  tertiary-container: '#006eca'
  on-tertiary-container: '#ebf1ff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#a3f69c'
  primary-fixed-dim: '#88d982'
  on-primary-fixed: '#002204'
  on-primary-fixed-variant: '#005312'
  secondary-fixed: '#98f994'
  secondary-fixed-dim: '#7ddc7a'
  on-secondary-fixed: '#002204'
  on-secondary-fixed-variant: '#005313'
  tertiary-fixed: '#d4e3ff'
  tertiary-fixed-dim: '#a5c8ff'
  on-tertiary-fixed: '#001c3a'
  on-tertiary-fixed-variant: '#004786'
  background: '#f7f9fc'
  on-background: '#191c1e'
  surface-variant: '#e0e3e6'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  container-padding: 24px
  gutter: 16px
  section-gap: 32px
  sidebar-width: 280px
---

## Brand & Style

The design system is engineered for the high-stakes world of precision agriculture, blending enterprise-grade reliability with cutting-edge AI sophistication. The aesthetic is rooted in **Modern Minimalism** with strategic **Glassmorphic** accents to signify data transparency and depth.

The interface should feel airy, professional, and trustworthy. We avoid decorative clutter in favor of high-utility information density. The emotional response is one of calm control—transforming complex satellite and sensor data into actionable, serene intelligence.

**Key Visual Principles:**
- **Clarity over Ornament:** Every element must serve a functional purpose in the data-analysis pipeline.
- **Organic Precision:** While the grid is rigid and mathematical, subtle rounding and natural greens soften the technical edge.
- **Layered Intelligence:** Use translucent surfaces to indicate depth, suggesting that the AI is "looking through" layers of data.

## Colors

The palette is anchored in "Growth Greens," utilizing **Forest Green** for primary actions and **Emerald Green** for success states and growth indicators. 

- **Primary & Secondary:** Used for branding, primary buttons, and active states.
- **Accents:** Reserved strictly for semantic meaning. **Orange** denotes moisture stress or moderate warnings; **Red** signifies critical irrigation failure or pest outbreaks; **Blue** is dedicated to meteorological and water-related data.
- **Surface Strategy:** In light mode, use `#F5F7FA` for secondary backgrounds to reduce eye strain. In dark mode, utilize a Deep Slate (`#0F172A`) rather than pure black to maintain the premium, soft-glass aesthetic.

## Typography

This design system utilizes **Inter** exclusively to ensure maximum legibility across dense data tables and complex GIS interfaces. 

- **Scale:** We employ a tight typographic scale to maintain a professional "SaaS dashboard" feel. 
- **Hierarchy:** Use `label-sm` in all-caps with slight tracking for table headers and section overviews.
- **Weights:** Use Semi-Bold (600) for UI headers and Medium (500) for interactive elements like buttons and navigation items. Regular (400) is reserved for body copy and descriptions.

## Layout & Spacing

The layout follows a **12-column fluid grid** for the main content area, with a fixed left-hand sidebar.

- **Grid:** Use a 24px margin on desktop, reducing to 16px on mobile. 
- **Rhythm:** All spacing must be a multiple of 8px. Use 16px (2x) for internal card padding and 32px (4x) for separating major dashboard modules.
- **Sidebar:** The sidebar is a constant anchor. It should be collapsible to an icon-only state on smaller desktop viewports to prioritize map and chart real estate.
- **Breakpoints:** 
    - Mobile: < 600px (Single column stacked)
    - Tablet: 600px - 1024px (2-column cards)
    - Desktop: > 1024px (Full 12-column layout)

## Elevation & Depth

We utilize a "Layered Glass" philosophy to define depth.

- **Level 0 (Background):** Solid `#F5F7FA` or Dark Slate.
- **Level 1 (Cards/Panels):** White (or dark equivalent) with a subtle 1px border (`rgba(0,0,0,0.05)`).
- **Level 2 (Hover/Modals):** Increased shadow diffusion and a very subtle backdrop blur (8px). 
- **Shadows:** Use "Soft Shadows"—highly diffused, low-opacity (4-8%) using a slight tint of the Primary color (`#2E7D32`) in the shadow's umbra to create a more natural, integrated look.
- **Outlines:** In high-density data views, favor 1px borders over shadows to maintain crispness and prevent visual "mud."

## Shapes

The shape language is consistently **Rounded** (Level 2). 

- **Components:** Standard buttons, input fields, and small cards use a **12px** (rounded-lg) radius. 
- **Containers:** Large dashboard sections and parent containers use **16px** (rounded-xl) to frame the content comfortably.
- **Data Points:** In charts, bar ends should be slightly rounded (4px) to avoid a harsh "industrial" feel, aligning with the organic nature of agriculture.

## Components

### Sidebar Navigation
- **Style:** Clean, vertical stack with a semi-transparent active state background.
- **Icons:** Use 20px 2pt stroke icons. Active state uses the Primary Green.

### Data Visualization
- **Charts:** Use a 4px corner radius on Bar charts. Area charts should use a 10% opacity fill of the stroke color.
- **Gauges:** Use semi-circular tracks with a thickness of 12px for soil moisture and health metrics.

### Interactive Maps
- **Polygons:** Use Primary Green for healthy zones with 20% fill opacity. Use Warning/Critical colors for stress zones.
- **Controls:** Floating glassmorphic control pill at the bottom-center of the map for layer switching.

### Cards & KPIs
- **KPIs:** Feature a large `headline-lg` value with a small trend indicator (e.g., "+12% vs last cycle").
- **Hover:** On hover, cards should lift 2px with an increased shadow spread.

### Form Elements
- **Inputs:** 48px height for primary inputs, with a 1px neutral border that turns Primary Green on focus.
- **Buttons:** 
    - *Primary:* Solid Forest Green, white text, 12px radius.
    - *Secondary:* Ghost style with 1px border and Green text.