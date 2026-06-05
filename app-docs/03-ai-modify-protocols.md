# AI Instructions — Modifying Protocols or Medications

**How to use:** Paste the block below at the start of a new AI session before describing your changes.

---

```
=== EMS PROTOCOL ASSISTANT — MODIFY PROTOCOLS / MEDS ===

REPO: pairamedic/protocolassistant
FILE: ProtocolAssistant.html (single-file app — all HTML, CSS, and JS inline)
HOSTING: GitHub Pages from main branch
DEV BRANCH: claude/easi-protocols-2026-service-c30fH

--- ACTIVE SERVICE DATA LOCATION ---
EASI Protocols - 2026 is the primary service.
Its data lives in TWO places that must be kept in sync:
  1. const EASI_2026_SERVICE in ProtocolAssistant.html (~line 1769)
  2. Firestore: project emsprotocolapp / collection service_data / doc easi-2026

The app loads live data from Firestore at runtime. After editing the HTML, the admin
must press ⚙️ → Push to Cloud to sync Firestore with the updated HTML constant.

--- PROTOCOL OBJECT STRUCTURE ---
{
  id: 'easi26-unique-id',        // must be unique; do NOT change existing IDs (breaks favorites)
  title: 'Protocol Title',
  summary: 'One-line summary shown in the card header.',
  steps: [
    'Plain step text.',
    'Step with sub-items: 1) First. 2) Second. 3) Third.',
    'Step with arrow: Condition → Treatment.'
  ],
  tags: ['search','keywords','lowercase','only']
}

--- STEP FORMATTING RULES ---
The app renderer (splitInlineList) automatically formats steps:
  - "1) 2) 3)" pattern → visual sub-steps with teal left border accent
  - "→" arrows → rendered as styled treatment arrows
  - Role prefix "EMT:", "Paramedic:", "Advanced EMT:" → colored role badge
  - Plain text only inside step strings — no HTML, no markdown

Example of a well-formatted multi-criteria step:
  'Inclusion Criteria (≥2 required): 1) MAP <65 mmHg. 2) SBP <100. 3) HR >100.'

--- HOW TO MODIFY AN EXISTING PROTOCOL ---
1. Search the HTML file for the protocol id or title string.
2. Edit the steps array. Each element is a single-quoted JS string.
   - Escape apostrophes with backslash: it\'s
   - Do NOT use backtick template strings or HTML inside step strings.
3. Update summary if the clinical overview changed.
4. Add/update tags if new keywords apply.
5. NEVER change the id of an existing protocol — this breaks saved favorites.

--- HOW TO ADD A NEW PROTOCOL ---
1. Find the correct category block inside EASI_2026_SERVICE.protocols
   (categories are marked with // ── CATEGORY ── comments).
2. Insert the new protocol object following the structure above.
3. Assign an id like 'easi26-topic-name' (must be globally unique in the file).
4. Add relevant lowercase search tags.

--- HOW TO DELETE A PROTOCOL ---
Remove the entire object from the protocols array.
Prefer using the in-app ⚙️ Admin Panel for deletions to avoid breaking surrounding JS syntax.

--- MEDICATION OBJECT STRUCTURE ---
{
  name: 'Drug Name',
  route: 'IV / IM / Neb / SL',
  notes: 'Dosing, indications, special instructions.',
  contra: 'Contraindications.',
  se: 'Side effects.',
  default_mgkg: 0.5,   // optional — enables weight-based calculator
  max_mg: 100          // optional — caps the weight calc
}
Meds live in EASI_2026_SERVICE.meds (separate array, same file, same service constant).

--- CONTACTS OBJECT STRUCTURE ---
{
  id: 'c-unique-id',
  group: 'internal',          // 'internal' or 'clinical'
  name: 'Full Name',
  role: 'Job Title',
  desc: 'Description of role.',
  phone: '8705551234',        // 10 digits only, no dashes
  email: 'name@example.com',
  hours_restricted: false,    // true = red "Business Hours Only" badge
  exec: false,                // true = VIP card style
  wide: false,                // true = full-width card
  badge: '',                  // escalation label e.g. '① First Contact'
  badge_color: 'accent'       // 'accent', 'danger', or 'warning'
}

--- AFTER MAKING CHANGES ---
1. Save the HTML file.
2. Commit:
   git add ProtocolAssistant.html
   git commit -m "Brief description of what changed"
3. Push to main:
   git push -u origin main
4. Push to dev branch:
   git push origin main:claude/easi-protocols-2026-service-c30fH
5. In the app: log in as eliasacaldwellnrp@gmail.com,
   select EASI Protocols - 2026,
   tap ⚙️ → Admin Panel → ☁️ Push to Cloud
6. Users get updates on next app open, or immediately via:
   Resources tab → Update App → Clear Cache & Update

--- CACHE BUST (force all users to update immediately) ---
Edit sw.js: increment the cache version number
  const CACHE = 'easi-protocols-v2';  →  const CACHE = 'easi-protocols-v3';
Commit and push. All devices receive fresh files on next open.

--- DO NOT MODIFY ---
- SAMPLE_SERVICE (demo/fallback data)
- const KEY, SVC_CACHE_KEY, SVC_DOC_ID variable values
- Firebase config block (apiKey, authDomain, etc.)
- ADMIN_EMAILS set (unless adding a new admin)
- Resources section HTML (calculators, Peds Ref, vent settings)
- sw.js cache version (unless intentionally forcing a cache bust)
=== END ===
```
