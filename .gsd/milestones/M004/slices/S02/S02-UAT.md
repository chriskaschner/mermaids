# S02: Icon Refresh — UAT Script

## Preconditions

- App served locally: `cd frontend && python3 -m http.server 8080`
- Open `http://localhost:8080/index.html` in a browser
- Browser DevTools available (for element inspection)

---

## TC-01: Nav Bar Dress-Up Icon Shows Mermaid Tail

**Steps:**
1. Open the app at `http://localhost:8080/index.html`
2. Look at the bottom nav bar — there should be 3 icons: Home (left), Dress Up (center), Coloring (right)
3. The center icon (Dress Up) should display a bifurcated mermaid tail shape — a narrow stem that splits into two curved lobes

**Expected:**
- The dress-up icon is a recognizable mermaid tail silhouette in purple (`#c47ed0`)
- It is NOT a 5-pointed star
- The icon is visually distinct from the house (Home) and pencil (Coloring) icons

**Edge case:** If the icon area appears blank (empty space with no visible shape), the SVG path `d` attribute is malformed — inspect the `<path>` element in DevTools.

---

## TC-02: Home Screen Dress-Up Button Shows Mermaid Tail

**Steps:**
1. Navigate to the home screen (`#/home` or tap the house icon)
2. The home screen shows two large circular activity buttons
3. The "Dress Up" button should display a mermaid tail inside its circle

**Expected:**
- The tail icon is centered within the coral/pink circle background
- It matches the nav bar tail design (bifurcated lobes) at a larger scale
- It is NOT a 5-pointed star

**Edge case:** If only the circle background renders with no icon inside, the SVG paths in `app.js renderHome()` are malformed.

---

## TC-03: House and Pencil Icons Unchanged

**Steps:**
1. From the home screen, verify the nav bar house icon (leftmost) is a standard house silhouette
2. Verify the nav bar pencil icon (rightmost) is a pencil/crayon shape
3. On the home screen, verify the "Coloring" activity button shows a pencil inside its circle

**Expected:**
- House icon: familiar peaked-roof house outline
- Pencil icon: diagonal pencil shape
- Neither has changed from before the icon refresh

---

## TC-04: All Icons Have Accessible Labels

**Steps:**
1. Right-click each nav bar icon → Inspect
2. Check the `aria-label` attribute on each `.nav-icon` anchor

**Expected:**
- Home icon: `aria-label="Home"`
- Dress Up icon: `aria-label="Dress Up"`
- Coloring icon: `aria-label="Coloring"`
- All three labels are present and distinct

---

## TC-05: Home Screen Activity Buttons Have Accessible Labels

**Steps:**
1. Navigate to home screen
2. Right-click each activity button → Inspect
3. Check the `aria-label` attribute on each `.activity-btn`

**Expected:**
- Dress Up button: `aria-label="Dress Up"`
- Coloring button: `aria-label="Coloring"`
- Each button contains an `<svg>` element as a direct child

---

## TC-06: No Regressions in Navigation

**Steps:**
1. Tap the dress-up nav icon (mermaid tail) — should navigate to `#/dressup`
2. Tap the coloring nav icon (pencil) — should navigate to `#/coloring`
3. Tap the home nav icon (house) — should navigate to `#/home`
4. On home screen, tap the "Dress Up" activity button — should navigate to `#/dressup`
5. Return to home, tap the "Coloring" activity button — should navigate to `#/coloring`

**Expected:**
- All 5 navigation paths work identically to before the icon change
- No broken links, no console errors
