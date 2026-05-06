# 🎨 Advanced UI Design Prompt
# Instagram Outreach CRM — Beautiful & Functional Interface

---

## 🧠 CONTEXT (Read First)

You are designing a **premium Instagram Outreach CRM** for a small team of DM setters who book sales calls. The system has two roles:

- **Admin (owner):** Manages users, monitors performance, sees all leads
- **Setters (team):** Adds leads, tracks status, books calls, manages follow-ups

This is used daily, on both desktop and mobile. It must be **fast to use** (1-click actions) and **visually clear** (follow-ups can't be missed).

---

## 🎨 DESIGN IDENTITY

**Aesthetic:** Dark, premium, modern SaaS — think Linear.app meets Notion meets a Bloomberg terminal. Not corporate. Not "startup generic purple." It feels like a **tool built by someone who cares.**

**Personality:** Serious but not cold. Confident. Dense information without feeling cluttered. Like a cockpit — everything you need, nothing you don't.

**Inspiration References:**
- Linear.app (dark sidebar, clean cards, keyboard-first)
- Raycast (command palette feel, micro-interactions)
- Vercel dashboard (monochrome with sharp accents)
- Stripe dashboard (data density done right)

---

Font Sizes:
  xs:   11px  (timestamps, helper text)
  sm:   13px  (table cells, labels)
  base: 15px  (body, descriptions)
  lg:   18px  (section headings)
  xl:   24px  (page titles)
  2xl:  32px  (stat numbers)
  3xl:  48px  (hero stat numbers on admin dashboard)

Font Weights:
  Regular: 400 (body text)
  Medium:  500 (labels, nav items)
  Semi:    600 (card titles, button text)
  Bold:    700 (section headers)
  Black:   800 (stat numbers, display text)
```

### Spacing & Layout

```
Sidebar Width:    240px (desktop), hidden (mobile)
Content Max-W:    1280px
Border Radius:    8px (cards), 6px (buttons), 4px (badges), 12px (modals)
Card Padding:     20px
Table Row Height: 52px
```

### Effects & Atmosphere

```
Background texture: Subtle noise overlay (3% opacity SVG noise)
Cards:              1px border + box-shadow: 0 1px 3px rgba(0,0,0,0.4)
Hover states:       Background shifts from Surface to Surface Elevated
Active states:      Left border accent (2px, accent blue)
Focus rings:        2px solid #4F7EFF with 2px offset
Scrollbars:         Custom thin (4px), dark track, medium thumb
Selection:          #4F7EFF33 background
```

---

## 📐 LAYOUT ARCHITECTURE

### Global Layout (Desktop)

```
┌─────────────────────────────────────────────────────────┐
│  SIDEBAR (240px, fixed)  │  MAIN CONTENT (flex-1)       │
│                          │                               │
│  ● App Logo              │  TOPBAR (56px, sticky)        │
│  ──────────────          │  ─────────────────────────── │
│  📊 Dashboard            │                               │
│  👥 My Leads      ●34    │  PAGE CONTENT                 │
│  ⚠️  Follow-ups   ●7     │  (scrollable)                 │
│  📞 Calls         ●3     │                               │
│  ──────────────          │                               │
│  [ADMIN SECTION]         │                               │
│  👤 Users                │                               │
│  📈 Stats                │                               │
│  🔍 All Leads            │                               │
│  ──────────────          │                               │
│  User Avatar             │                               │
│  email@email.com         │                               │
│  [Logout]                │                               │
└─────────────────────────────────────────────────────────┘
```

### Global Layout (Mobile)

```
┌─────────────────────┐
│  TOPBAR             │
│  ≡ Logo    [Avatar] │
├─────────────────────┤
│                     │
│  CONTENT (scroll)   │
│                     │
├─────────────────────┤
│  BOTTOM NAV         │
│ 🏠  📋  ⚠️  📞  👤  │
└─────────────────────┘
```

---

## 🖥️ PAGE-BY-PAGE UI SPECS

---

### PAGE 1: LOGIN PAGE

**Layout:** Full-screen dark, centered card

**Background:**
- Deep dark `#0A0A0F`
- Subtle radial gradient from center: `radial-gradient(ellipse 80% 60% at 50% 40%, #1a1a30 0%, #0A0A0F 70%)`
- Faint grid pattern overlay (CSS: 1px lines, 5% opacity)

**Login Card:**
- Width: 400px, centered
- Background: `#111118`
- Border: `1px solid #2A2A38`
- Border radius: 12px
- Padding: 40px
- Box shadow: `0 20px 60px rgba(0,0,0,0.6), 0 0 0 1px #2A2A38`

**Card Content (top to bottom):**
```
[App logo icon — geometric, sharp]
[App Name: "REACHFLOW" or "SETTERCRM" in Syne font, white, bold]
[Tagline: "Your outreach. Organized." in text-secondary]

[Gap: 32px]

[Label: "Email address" — sm, text-secondary]
[Email Input]

[Label: "Password"]
[Password Input] [Show/Hide toggle icon inside]

[Gap: 24px]

[Login Button — full width, accent blue, "Sign In →"]

[Error message area — shows if wrong credentials]
```

**Input Styling:**
- Background: `#0A0A0F`
- Border: `1px solid #2A2A38`
- Border radius: 6px
- Padding: 12px 16px
- Focus: border changes to `#4F7EFF`, glow: `0 0 0 3px #4F7EFF20`
- Text: white, font DM Sans 14px

**Button Styling:**
- Background: `#4F7EFF`
- Text: white, semi-bold, 14px
- Padding: 13px 24px
- Border radius: 6px
- Hover: `#3D6EEE` + slight lift `translateY(-1px)`
- Active: `translateY(0)` + slightly darker

**Animation on load:**
- Card fades in + slides up 20px → resting position (300ms ease-out)

---

### PAGE 2: SETTER — CRM DASHBOARD

**This is the most important page. Maximum clarity.**

#### 2A — Sidebar

```
Background: #111118
Border-right: 1px solid #2A2A38

Logo area (top):
  - App icon (small, geometric)
  - App name "REACHFLOW" — Syne, 15px, bold, white
  
Nav items:
  - Icon (20px) + Label + Badge count (if any)
  - Default: text-secondary, no background
  - Active: text-primary, bg: #1A1A24, left border 2px #4F7EFF
  - Hover: text-primary, bg: #161620
  
Items:
  🏠 Dashboard
  👥 My Leads        [34]   ← badge: rounded pill, bg #2A2A38
  ⚠️  Follow-ups     [7]    ← badge: bg RED if overdue exists
  📞 Calls           [3]
  
Divider (1px #2A2A38)

User section (bottom):
  [Avatar circle — initials, gradient bg]
  [email — text-secondary, 12px, truncated]
  [Logout icon button — top right, hover red]
```

#### 2B — Topbar

```
Background: #111118 (slightly different from sidebar)
Border-bottom: 1px solid #2A2A38
Height: 56px
Padding: 0 24px

Left: Page title ("Dashboard" in DM Sans, 16px, bold, white)
Right: 
  [Search icon button]
  [+ Add Lead button] ← prominent, accent blue
  [Notification bell icon] (future use)
```

#### 2C — Follow-up Alert Banner (CRITICAL)

```
If overdue leads exist:
┌──────────────────────────────────────────────────────────┐
│ ⚠️  7 follow-ups are OVERDUE  ·  [View Overdue →]        │
└──────────────────────────────────────────────────────────┘
Background: #FF444415 (red transparent)
Border: 1px solid #FF444440
Border-left: 4px solid #FF4444
Text: #FF6666
Font: DM Sans 13px medium
Padding: 10px 20px
Margin: 16px 24px 0
Border radius: 6px
```

#### 2D — Stats Row (Quick Numbers)

```
4 cards in a row (or 2x2 on mobile):

┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ MY LEADS     │ │ OVERDUE      │ │ CALLS BOOKED │ │ TODAY        │
│     34       │ │      7       │ │      3       │ │      5       │
│ total        │ │ follow-ups   │ │ this week    │ │ to follow up │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘

Card styling:
- Background: #111118
- Border: 1px solid #2A2A38
- Border radius: 8px
- Padding: 20px
- Number: Syne font, 32px, bold, text-primary
- Label: DM Sans, 11px, uppercase, letter-spacing 0.08em, text-tertiary
- Bottom label: text-secondary, 12px
- Overdue card: number color = #FF4444
- Today card: number color = #F59E0B
```

#### 2E — OVERDUE FOLLOW-UPS Section

```
Only shows if overdue leads exist.

Section header:
  ⚠️ OVERDUE FOLLOW-UPS          [7 leads] ←badge
  "You're behind on these. Take action now."

Leads shown as cards (not table, more visual on mobile):

┌───────────────────────────────────────────────────────────┐
│ @handle_here              [REPLIED]       ● 3 days late   │
│ Last contacted: Nov 12   Next: Nov 13                     │
│                         [Follow-up Done ✓] [Edit →]       │
└───────────────────────────────────────────────────────────┘

Card styling:
  - Background: #FF444408
  - Border: 1px solid #FF444430
  - Border-left: 3px solid #FF4444
  - Border radius: 8px
  - Padding: 16px 20px
  - Handle: JetBrains Mono, 14px, white
  - "X days late": text red, small badge
  - Status badge: outlined, small
  - "Follow-up Done" button: green, small
  - "Edit": text link, text-secondary

"Follow-up Done" Button:
  - Background: #10B98120
  - Border: 1px solid #10B98150
  - Text: #10B981
  - Border radius: 6px
  - Padding: 6px 12px, 13px font
  - On hover: bg #10B98130
```

#### 2F — TODAY'S FOLLOW-UPS Section

```
Similar to above but amber theme:
  - Card border-left: 3px solid #F59E0B
  - Background: #F59E0B08
  - Border: 1px solid #F59E0B30
  - Badge: amber
```

#### 2G — ALL MY LEADS Table

```
Section header:
  MY LEADS                [Search: ________________ 🔍]

Table:
  Background: #111118
  Border: 1px solid #2A2A38
  Border radius: 8px
  Overflow: hidden

Table header:
  - Background: #0A0A0F
  - Text: text-tertiary, 11px, uppercase, letter-spacing 0.1em
  - Padding: 10px 20px
  - Border-bottom: 1px solid #2A2A38

Columns:
  HANDLE | STATUS | NEXT FOLLOW-UP | NOTES | ACTIONS

Table rows:
  - Height: 52px
  - Padding: 0 20px
  - Border-bottom: 1px solid #1E1E2A
  - Hover: bg #161620
  
  HANDLE cell:
    - Font: JetBrains Mono, 14px, white
    - Show "@" in text-tertiary, handle in white
    - Example: "@insta_handle"
    
  STATUS cell:
    - Pill badge (rounded-full)
    - Small dot + status text
    - Colors as defined above
    - Example: "● Replied" (amber pill)
    
  NEXT FOLLOW-UP cell:
    - If overdue: red text + ⚠️ icon
    - If today: amber text + 📅 icon
    - If future: text-secondary
    - If none: "—" in text-tertiary
    
  NOTES cell:
    - Truncated at 200px max-width
    - text-secondary, 13px
    - Ellipsis (...)
    
  ACTIONS cell (right-aligned):
    Quick action buttons (show on row hover):
    [Messaged] [Replied] [Interested] [⋮ More]
    
    Status buttons:
      - Tiny pill buttons (outline style)
      - 11px font, 4px 8px padding
      - Only show next logical status:
        - If new_lead: show "Mark Messaged"
        - If messaged: show "Mark Replied"
        - If replied: show "Mark Interested"
        - If interested: show "Book Call"
      - Hover: filled background
    
    "⋮ More" dropdown:
      - Edit, Set Follow-up, Delete
      - Appears as mini dropdown menu
      - Clean dark dropdown card

Pagination (if needed):
  - Bottom of table
  - "Showing 1–50 of 234 leads"
  - Prev / Next buttons
  - Very minimal styling
```

---

### PAGE 3: ADD LEAD MODAL/SLIDEOUT

**Trigger:** "+ Add Lead" button in topbar

**Style:** Right slide-out panel (not centered modal)

```
Overlay: rgba(0,0,0,0.5) on main content
Panel:
  Width: 420px
  Background: #111118
  Border-left: 1px solid #2A2A38
  Height: 100vh
  Padding: 32px 28px
  Shadow: -20px 0 60px rgba(0,0,0,0.5)

Panel header:
  "Add New Lead" — Syne, 20px, white
  [X close button — top right, text-secondary]

Form fields (stacked):
  Instagram Handle *
  [Input with @ prefix icon inside] — JetBrains Mono inside

  Status
  [Segmented select or styled dropdown]
  Options: New Lead | Messaged | Replied | Interested

  Notes
  [Textarea — 4 rows, resize-none]

  Next Follow-up
  [Date input — styled, calendar icon inside]

Footer:
  [Cancel] [Add Lead →]
  Buttons right-aligned
  Add Lead: accent blue, full-weight
  Cancel: text-secondary, no border

Animation:
  Slides in from right (translateX 420px → 0) in 250ms ease-out
  Backdrop fades in simultaneously
```

---

### PAGE 4: BOOK CALL MODAL

```
Style: Centered modal (smaller, focused)

Modal:
  Width: 480px
  Background: #111118
  Border: 1px solid #2A2A38
  Border radius: 12px
  Padding: 32px
  Shadow: 0 20px 60px rgba(0,0,0,0.8)

Header:
  📞 Book a Call
  @insta_handle ← handle shown below in mono, text-secondary
  "Moving to Call Booked status after booking"

Form:
  Call Date *       [Date input]
  Call Time *       [Time input]
  Notes (optional)  [textarea, 2 rows]

Footer:
  [Cancel]  [Book Call →]
  Book Call button: orange (#F97316) — different from regular actions
```

---

### PAGE 5: ADMIN — MAIN DASHBOARD

**Only you see this. More data-dense.**

#### 5A — Stats Grid (Top)

```
Row 1 (4 big cards):
  TOTAL USERS    TOTAL LEADS    CALLS BOOKED    CONVERSION
      5              234              12            5.1%

Styling:
  - Numbers in Syne, 48px, bold, white
  - Labels in 11px uppercase
  - Cards: same dark card style
  - Conversion rate number: gradient text (blue to purple)
```

#### 5B — Performance Grid (Two columns)

```
Left column: SETTER PERFORMANCE TABLE
Right column: RECENT ACTIVITY LOG

SETTER PERFORMANCE:
  Table columns: Setter | Leads | Calls | Rate | Last Active
  Rows for each setter user
  Rank indicator: gold/silver/bronze dots for top 3
  Last Active: "2 mins ago", "Yesterday"

RECENT ACTIVITY LOG:
  Last 20 activities
  Each row:
    [Avatar initials] [Username] [Action] [Lead handle] [Time]
    Example: "SA  Sarah  marked as Replied  @handle  3m ago"
  
  Color coding:
    - call_booked action: orange text
    - replied action: amber text
    - added lead: blue text
    - other: text-secondary
```

#### 5C — Quick Stats (Bottom row)

```
THIS WEEK:
  [New Leads: 45]  [Calls Booked: 3]  [Follow-ups Done: 28]

Shown as 3 horizontal stat pills
Background: #1A1A24
Border: 1px solid #2A2A38
Padding: 12px 20px
Border radius: 8px
Label on left, number on right
```

---

### PAGE 6: ADMIN — USER MANAGEMENT

```
Page Header:
  "Team Members"     [+ Create User button — accent blue]

Users Grid (cards, not just table):
  3 columns on desktop, 1 on mobile

Each user card:
  ┌─────────────────────────────────┐
  │ [Avatar circle - initials]      │
  │ sarah@email.com                 │
  │ [SETTER badge]  Last: 2min ago  │
  │                                 │
  │ Leads: 45  Calls: 3  Rate: 6.7% │
  │                                 │
  │ [Edit]      [Reset PW]  [Delete]│
  └─────────────────────────────────┘

Card styling:
  - Background: #111118
  - Border: 1px solid #2A2A38
  - Border radius: 8px
  - Padding: 20px
  - Hover: border-color #3D3D52

Avatar:
  - Circle, 48px
  - Background: gradient from blue to purple
  - Initials: white, Syne, 18px bold

Role badge:
  - ADMIN: gold pill (#F59E0B20, #F59E0B border, #F59E0B text)
  - SETTER: blue pill (#3B82F620, #3B82F6 border, #3B82F6 text)

Action buttons:
  - Small, outline style
  - Edit: text-secondary border
  - Reset PW: amber outline
  - Delete: red on hover, text-secondary default

Create User Modal/Panel:
  - Same slide-out panel style
  - Fields: Email, Role (Admin/Setter)
  - Password: auto-generated, shown after creation
  - "Copy Password" button → clipboard
```

---

### PAGE 7: ADMIN — STATS PAGE

```
Header: "Performance Analytics"
Date filter: [Last 7 Days ▼]  [Last 30 Days]  [All Time]

Section 1: Conversion Funnel (visual bars, no charts library needed)
  NEW → MESSAGED → REPLIED → INTERESTED → CALL BOOKED

  Horizontal bar visual:
  New Lead     ████████████████████████████ 234
  Messaged     ████████████████████       178
  Replied      ████████████             134
  Interested   ████████                  67
  Call Booked  ████                      12

  Bars: gradient from accent blue to accent purple
  Numbers shown right of bar
  Percentage shown below label: "76% → replied"
  Simple CSS divs with width %, no chart library

Section 2: Setter Table (detailed)
  Columns: Setter | DMs Sent | Replies | Interested | Calls | Conv %
  Colored cells based on performance (red → green scale)

Section 3: Activity Timeline (recent 20 actions)
  Same as dashboard activity log
```

---

### PAGE 8: ADMIN — ALL LEADS VIEW

```
Page header: "All Leads"
Filters bar:
  [Status: All ▼]  [Setter: All ▼]  [Search: _____________]
  Right side: "234 leads" count

Table: Same as setter table BUT:
  - Extra column: "ASSIGNED TO" (shows setter name)
  - Admin can click status badge to change (inline dropdown)
  - Admin can click assigned to → change setter (inline dropdown)
  - No restrictions — full access

Inline dropdown (when admin clicks a cell):
  - Small dropdown appears below
  - Dark card, 1px border
  - Options listed
  - Click = immediate save
  - ESC or click outside = cancel
```

---

## 🎛️ UI COMPONENTS LIBRARY

### Status Badges

```html
<!-- Sizes: sm (table rows), md (detail views), lg (featured) -->

<!-- New Lead -->
<span class="badge badge-blue">● New Lead</span>
Style: bg #3B82F615, border #3B82F640, text #3B82F6, dot #3B82F6

<!-- Messaged -->
<span class="badge badge-purple">● Messaged</span>
Style: bg #8B5CF615, border #8B5CF640, text #8B5CF6

<!-- Replied -->
<span class="badge badge-amber">● Replied</span>
Style: bg #F59E0B15, border #F59E0B40, text #F59E0B

<!-- Interested -->
<span class="badge badge-green">● Interested</span>
Style: bg #10B98115, border #10B98140, text #10B981

<!-- Call Booked -->
<span class="badge badge-orange">● Call Booked</span>
Style: bg #F9731615, border #F9731640, text #F97316
```

### Buttons

```
Primary (accent blue):
  bg #4F7EFF, text white, hover bg #3D6EEE
  Padding: 10px 20px, border-radius: 6px
  
Secondary (subtle):
  bg #1A1A24, border 1px solid #2A2A38, text white
  hover: border-color #3D3D52
  
Danger (red):
  bg #FF444415, border #FF444440, text #FF6666
  hover: bg #FF444425
  
Success (green):
  bg #10B98115, border #10B98140, text #10B981
  hover: bg #10B98125
  
Ghost (no background):
  text-secondary, hover: text-primary + bg #1A1A24

Small variant: 6px 12px padding, 12px font
XSmall variant: 4px 8px padding, 11px font (for table row actions)
```

### Input Fields

```
All inputs:
  background: #0A0A0F
  border: 1px solid #2A2A38
  border-radius: 6px
  padding: 10px 14px
  color: white
  font: DM Sans, 14px
  
  :focus
    border-color: #4F7EFF
    box-shadow: 0 0 0 3px rgba(79, 126, 255, 0.15)
    outline: none
    
  ::placeholder
    color: #555570
    
  prefix/suffix icon:
    position: absolute
    inside input padding-left/right: 40px
    icon color: text-tertiary
```

### Dropdown Menus

```
Background: #1A1A24
Border: 1px solid #2A2A38
Border-radius: 8px
Padding: 6px
Box-shadow: 0 8px 24px rgba(0,0,0,0.6), 0 0 0 1px #2A2A38

Items:
  Padding: 8px 12px
  Border-radius: 4px
  Font: DM Sans, 13px
  Color: text-primary
  Hover: bg #2A2A38
  
Dividers: 1px solid #2A2A38, margin 4px 0
Destructive item: color #FF6666, hover bg #FF44440D
```

### Toast Notifications

```
Position: bottom-right, fixed, z-index 9999
Width: 320px
Background: #1A1A24
Border: 1px solid #2A2A38
Border-radius: 8px
Padding: 14px 16px
Box-shadow: 0 8px 24px rgba(0,0,0,0.6)
Border-left: 3px solid [status color]

Types:
  Success: border-left #10B981, icon ✓ green
  Error:   border-left #FF4444, icon ✗ red
  Info:    border-left #4F7EFF,  icon ℹ blue
  
Animation: slides in from right, fades out after 3s
```

---

## 📱 MOBILE-SPECIFIC RULES

### Sidebar → Bottom Nav (mobile)

```
Bottom navigation bar:
  Height: 64px + safe-area-inset-bottom
  Background: #111118
  Border-top: 1px solid #2A2A38
  
  5 items:
  🏠 Home  |  📋 Leads  |  ⚠️ Follow  |  📞 Calls  |  👤 Profile
  
  Active item: icon + label colored in accent blue
  Inactive: icon + label in text-tertiary
  
  Badge on Follow-up icon: red dot if overdue
```

### Topbar (mobile)

```
Height: 56px
Left: Hamburger or app icon
Center: Page title
Right: + Add button (icon only on mobile)
```

### Table → Card List (mobile)

```
On mobile, tables switch to card layout:
  Each row becomes a card
  Priority info: Handle + Status (always visible)
  Secondary info: Next follow-up, Notes (smaller below)
  Actions: Show primary action + "..." overflow
  
Card margin: 8px
Card padding: 16px
Border radius: 8px
Border: 1px solid #2A2A38
```

### Modals (mobile)

```
Full-screen slide-up sheet instead of centered modal
Bottom half of screen (50% height), scrollable
Handle bar at top (drag to dismiss)
```

---

## ✨ MICRO-INTERACTIONS & ANIMATIONS

### Page Load

```
Sidebar: appears instantly
Content: staggered fade-in (each section 50ms delay)
Stats cards: fade in + slide up 12px, staggered 100ms each
Table rows: fade in sequentially (20ms between rows)
```

### Hover States

```
Nav items: 150ms ease-in-out color transition
Table rows: 100ms background transition
Buttons: 150ms background + shadow transition
Cards: 200ms border-color + shadow transition
```

### Action Feedback

```
Status button click:
  1. Button shows loading spinner (200ms)
  2. Row status badge updates instantly
  3. Toast notification slides in
  4. If overdue, row disappears from red section with fade-out
  
Follow-up Done click:
  1. Button briefly shows checkmark ✓
  2. Card fades + slides out of overdue section
  3. Counter badge in sidebar updates
  4. Success toast: "Follow-up set for Nov 16"

Add Lead submit:
  1. Button: "Adding..." with spinner
  2. Panel slides out
  3. New row appears at top of leads table (highlight flash)
  4. Toast: "Lead added successfully"
```

### Scroll Behavior

```
Topbar: sticky with backdrop-blur when scrolled
  (backdrop-filter: blur(12px), slightly transparent bg)

Sidebar: fixed, never scrolls
Content: smooth scroll-behavior
Anchor links: scroll-margin-top: 80px
```

---

## 🛠️ TECHNICAL IMPLEMENTATION NOTES

### HTML/TailwindCSS Setup

```html
<head>
  <!-- Google Fonts -->
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  
  <!-- TailwindCSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  
  <!-- Tailwind Config (in script tag) -->
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            bg: '#0A0A0F',
            surface: '#111118',
            elevated: '#1A1A24',
            border: '#2A2A38',
            accent: '#4F7EFF',
          },
          fontFamily: {
            display: ['Syne', 'sans-serif'],
            body: ['DM Sans', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace'],
          }
        }
      }
    }
  </script>
</head>
```

### Custom CSS (separate file)

```css
/* Global resets */
*, *::before, *::after { box-sizing: border-box; }
body { background: #0A0A0F; color: #F0F0FF; font-family: 'DM Sans', sans-serif; }

/* Noise texture overlay */
body::before {
  content: '';
  position: fixed; inset: 0; z-index: 0;
  background-image: url("data:image/svg+xml,..."); /* noise SVG */
  opacity: 0.03;
  pointer-events: none;
}

/* Custom scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #111118; }
::-webkit-scrollbar-thumb { background: #2A2A38; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #3D3D52; }

/* Selection color */
::selection { background: rgba(79,126,255,0.3); color: white; }

/* Focus visible */
:focus-visible { outline: 2px solid #4F7EFF; outline-offset: 2px; }

/* Transition defaults */
button, a, input, select { transition: all 150ms ease; }

/* Table row hover */
tbody tr { transition: background 100ms ease; }
tbody tr:hover { background: #161620; }

/* Status badge base */
.badge {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 2px 8px; border-radius: 999px;
  font-size: 12px; font-weight: 500; border: 1px solid;
}
```

### Flask Template Variables

When writing Jinja2 templates, use these patterns:
```jinja2
{# Status badge macro #}
{% macro status_badge(status) %}
  <span class="badge badge-{{ status | replace('_', '-') }}">
    <span class="dot"></span>
    {{ status | replace('_', ' ') | title }}
  </span>
{% endmacro %}

{# Overdue check #}
{% if lead.next_followup and lead.next_followup.date() < today %}
  <!-- RED CARD -->
{% elif lead.next_followup and lead.next_followup.date() == today %}
  <!-- AMBER CARD -->
{% endif %}

{# JetBrains Mono for handles #}
<span class="font-mono text-white">@{{ lead.instagram_handle }}</span>
```

---

## 📁 FILE STRUCTURE FOR TEMPLATES

```
templates/
├── base.html              # All CSS variables, fonts, shared layout
├── login.html             # Full-screen login
│
├── crm/
│   ├── layout.html        # Sidebar + topbar layout (extends base)
│   ├── dashboard.html     # Setter main view
│   ├── add_lead.html      # Slide-out panel (partial/fragment)
│   └── edit_lead.html     # Slide-out panel
│
└── admin/
    ├── layout.html        # Admin sidebar + topbar (extends base)
    ├── dashboard.html     # Admin overview
    ├── users.html         # User management
    ├── all_leads.html     # All leads view
    └── stats.html         # Performance analytics
```

---

## ✅ FINAL DESIGN CHECKLIST

Before calling UI "done," verify:

**Visual Quality:**
- [ ] All colors consistent with palette above
- [ ] No default browser styles bleeding through
- [ ] Status badges colored correctly
- [ ] Overdue section is RED and UNMISSABLE
- [ ] Today section is AMBER
- [ ] Tables have hover states
- [ ] Buttons have hover + active states
- [ ] Inputs have focus states (glow)
- [ ] Fonts loading correctly (Syne, DM Sans, JetBrains Mono)
- [ ] Instagram handles in monospace font

**Layout & Spacing:**
- [ ] Sidebar fixed, content scrollable
- [ ] Topbar sticky
- [ ] Consistent padding (20px cards, 24px page)
- [ ] Tables align cleanly
- [ ] Forms have proper label-input spacing

**Mobile:**
- [ ] Bottom nav visible on mobile
- [ ] Tables convert to cards
- [ ] Sidebar hidden on mobile
- [ ] Touch targets minimum 44px
- [ ] Modals full-screen on mobile
- [ ] No horizontal scroll

**Animations:**
- [ ] Page load stagger works
- [ ] Hover transitions smooth
- [ ] Toast notifications appear/disappear
- [ ] Modal/panel slide animations
- [ ] Status change feedback visible

**Admin vs Setter:**
- [ ] Admin sees all nav items + setter section
- [ ] Setter sees only their items
- [ ] Role badge shown in user section of sidebar
- [ ] Admin panel has richer data views

---

## 🎯 THE ONE THING TO REMEMBER

**The most important UI rule for this app:**

> The OVERDUE FOLLOW-UPS section must be so visually loud and obvious that a setter opens the app and instantly feels the urgency. They should never be able to ignore it. Red background. Red border. Red text. Count badge in sidebar. Banner at the top. It must create a tiny bit of anxiety — enough to trigger action.

**Everything else can be subtle and refined. But follow-ups must SHOUT.**

---

*Prompt written for: Instagram Outreach CRM (Flask + TailwindCSS + SQLite + Render)*
*Stack: Jinja2 templates, TailwindCSS CDN, custom CSS, vanilla JS for interactions*
*Font stack: Syne (display) + DM Sans (body) + JetBrains Mono (code/handles)*