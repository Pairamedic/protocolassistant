# Manual Update Guide

How to update the app yourself, without AI assistance, directly on GitHub.

---

## Method 1 — Edit Directly on GitHub (Easiest)

No software needed. Works from any browser including your phone.

1. Go to https://github.com/pairamedic/protocolassistant
2. Click **ProtocolAssistant.html**
3. Click the **pencil icon** (Edit this file) in the top right
4. Use **Ctrl+F** (or Cmd+F on Mac) to search for text you want to change
5. Make your edits
6. Scroll to the bottom → **Commit changes**
7. Select **Commit directly to the main branch**
8. Write a brief description of what you changed
9. Click **Commit changes**

GitHub Pages updates within ~60 seconds. Users will see the change on their next app open.

---

## Method 2 — Force Everyone to Update Immediately

After committing, if you want all users to get the new version right away:

1. Edit **sw.js** on GitHub (same pencil-icon method above)
2. Change the cache version number:
   ```
   const CACHE = 'easi-protocols-v2';
   ```
   to:
   ```
   const CACHE = 'easi-protocols-v3';
   ```
   (just increment the number by 1 each time)
3. Commit to main

All devices will discard their cached copy and download fresh files on next open.

Users can also self-update anytime via: **Resources tab → Update App → Clear Cache & Update**

---

## Method 3 — Sync Protocols to Firestore After Editing

Whenever you edit protocol/med/contact data in the HTML and push to GitHub, you must also push those changes to Firestore so all logged-in users get the updated data (not just the HTML):

1. Open the app at https://pairamedic.github.io/protocolassistant/ProtocolAssistant.html
2. Log in as `eliasacaldwellnrp@gmail.com`
3. Select **EASI Protocols - 2026** from the dropdown
4. Tap ⚙️ (top right of header)
5. Click **☁️ Push to Cloud**
6. Done — Firestore now matches the HTML

---

## Common Edits

### Change a phone number
Search for the old phone number (e.g. `8705551234`) → replace with new number.
Phone numbers are stored as 10 digits with no dashes.

### Change a contact's name or role
Search for their name → edit `name:` and/or `role:` fields in the contacts array.

### Update a protocol step
Search for a few words from the step text → edit the quoted string.

### Add a new protocol step
Find the protocol's `steps: [` array → add a new quoted string at the end:
```javascript
steps: [
  'Existing step.',
  'Another existing step.',
  'Your new step goes here.'    // ← add before the closing ]
],
```

### Change the EASI 2025 PIN
The PIN is stored as a SHA-256 hash. To change it:
1. Compute the SHA-256 hash of your new PIN:
   - On Mac/Linux terminal: `echo -n "NEWPIN" | sha256sum`
   - Online: search "SHA-256 hash generator", enter your PIN, copy the result
2. In `ProtocolAssistant.html`, search for `PINNED_SERVICES`
3. Replace the long hash string with your new hash

### Add a new admin email
Search for `ADMIN_EMAILS` → add the new email to the Set:
```javascript
const ADMIN_EMAILS = new Set([
  'eliasacaldwellnrp@gmail.com',
  'newadmin@example.com'
]);
```

---

## Using the In-App Admin Panel

The ⚙️ panel (visible only to admin email after login) lets you edit without touching code:

| Task | How |
|------|-----|
| Edit a protocol | ⚙️ → find protocol in list → **Edit** |
| Add a protocol | ⚙️ → **+ Add Protocol** |
| Delete a protocol | ⚙️ → find protocol → **✕** |
| Edit a medication | ⚙️ → Medications section → **Edit** |
| Add a medication | ⚙️ → **+ Add Med** |
| Edit a contact | ⚙️ → Contacts section → **Edit** |
| Add a contact | ⚙️ → **+ Add Contact** |
| Save & push to cloud | Use **Save & Push ☁** button in the edit modal |
| Push everything to cloud | ⚙️ → **☁️ Push to Cloud** |

**Note:** Changes made in the admin panel are saved to your device immediately and to Firestore when you use Push to Cloud. They are NOT saved back to the GitHub HTML file. For permanent changes that survive a full rebuild, you should also update the HTML constant `EASI_2026_SERVICE` via GitHub.

---

## Branch Reference

| Branch | Purpose |
|--------|---------|
| `main` | Live production — GitHub Pages serves from here |
| `claude/easi-protocols-2026-service-c30fH` | AI development branch |

Always push to `main` for changes to go live.
