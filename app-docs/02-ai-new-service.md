# AI Instructions — Adding a New Ambulance Service

**How to use:** Paste the block below at the start of a new AI session (Claude Code, Claude, ChatGPT, etc.) before describing your request.

---

```
=== EMS PROTOCOL ASSISTANT — ADD NEW SERVICE ===

REPO: pairamedic/protocolassistant
FILE: ProtocolAssistant.html (single-file app — all HTML, CSS, and JS inline)
HOSTING: GitHub Pages from main branch
DEV BRANCH: claude/easi-protocols-2026-service-c30fH

--- WHAT CHANGES PER SERVICE ---
Each service has its own: protocols, meds, contacts.
Resources (calculators, Peds Ref, vent settings) are SHARED — do NOT duplicate or modify them.

--- SERVICE DATA STRUCTURE ---
A service is a plain JS object stored in the SAMPLE_STATE.services map.
It has three arrays: protocols, meds, contacts.

PROTOCOLS:
{
  id: 'unique-kebab-id',           // lowercase, hyphens, no spaces — must be unique
  title: 'Protocol Name',
  summary: 'One-line description shown under title.',
  steps: [
    'Step text here.',
    'Multiple criteria step: 1) First item. 2) Second item. 3) Third item.',
    'Treatment arrow syntax: Condition → Treatment.'
  ],
  tags: ['lowercase','search','keywords']
}

MEDS:
{
  name: 'Drug Name',
  route: 'IV / IM / Neb / SL',
  notes: 'Dosing and indications.',
  contra: 'Contraindications.',
  se: 'Side effects.',
  default_mgkg: 0.5,   // optional — enables weight-based calculator button
  max_mg: 100          // optional — caps the weight calc result
}

CONTACTS:
{
  id: 'c-unique-id',
  group: 'internal',             // 'internal' or 'clinical'
  name: 'Full Name',
  role: 'Job Title',
  desc: 'What this person handles.',
  phone: '8705551234',           // 10 digits, no formatting
  email: 'name@example.com',
  hours_restricted: false,       // true = shows red "Business Hours Only" badge
  exec: false,                   // true = renders as executive VIP card (large name, indigo badge)
  wide: false,                   // true = spans full grid width
  badge: '① First Contact',     // optional escalation badge text
  badge_color: 'accent'          // 'accent' (teal), 'danger' (red), 'warning' (yellow)
}

--- STEPS TO ADD A NEW SERVICE ---

1. OPEN ProtocolAssistant.html in the editor.

2. CREATE THE SERVICE CONSTANT after EASI_2026_SERVICE:
   const NEWSERVICE_DATA = { protocols: [...], meds: [...], contacts: [...] };

3. REGISTER THE SERVICE in the load() function (search for "if(!data.services['EASI Protocols - 2026'])"):
   if(!data.services['New Service Name']){
     data.services['New Service Name'] = JSON.parse(JSON.stringify(NEWSERVICE_DATA));
     save(data);
   }

4. ADD DISPLAY NAME in SERVICE_DISPLAY map (search for "SERVICE_DISPLAY"):
   'New Service Name': 'Full Organization Name',

5. ADD PIN PROTECTION if needed (search for "PINNED_SERVICES"):
   - Compute SHA-256 hash of the PIN (e.g. in terminal: echo -n "12345" | sha256sum)
   - Add to PINNED_SERVICES: 'New Service Name': 'THE_HASH_HERE'

6. ADD LOGO if the service has one:
   - Upload the logo file (JPG/PNG) to the repo root
   - In updateTitle(), add a condition for the new service name
   - Follow the pattern used for EASI logo

7. PRESERVE all existing services — do not remove or modify EASI_2026_SERVICE,
   EASI_2025_SERVICE, SAMPLE_SERVICE, or any existing registration logic.

8. DO NOT touch: Resources section HTML, calculator JS, Peds Ref,
   SW cache version, Firebase config, or ADMIN_EMAILS set.

9. COMMIT AND PUSH to both main and claude/easi-protocols-2026-service-c30fH.
   After pushing, log in as admin and use ⚙️ → Push to Cloud.

--- FIRESTORE NOTE ---
EASI Protocols - 2026 reads from Firestore (service_data/easi-2026).
New services fall back to the hardcoded constant until admin does Push to Cloud.
A new Firestore doc will need to be created for each new service if cloud sync is desired.

--- CONTACTS SECTION ---
Contacts are data-driven. Add them in the contacts array of the service constant.
The renderContacts() function handles all rendering automatically.
Contacts with the 'exec: true' flag render as large VIP cards (use for CEO/President).
Contacts with a 'badge' property and badge_color contribute to the auto-derived escalation chain.
=== END ===
```
