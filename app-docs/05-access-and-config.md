# Access, Credentials & Configuration

⚠️ Keep this file in a secure location. Do not share publicly.

---

## Admin Access

| Item | Value |
|------|-------|
| Admin email | `eliasacaldwellnrp@gmail.com` |
| Admin password | *(your Firebase Auth password — set by you at account creation)* |
| Admin panel access | Log in with admin email → ⚙️ button appears top-right |

The admin panel is available only to accounts whose email is listed in `ADMIN_EMAILS` in the HTML source.

---

## Service PINs

| Service | PIN | Notes |
|---------|-----|-------|
| EASI Protocols - 2025 | **37819** | Stored as SHA-256 hash in source — plain value only here |
| EASI Protocols - 2026 | *(no PIN)* | Open access after login |

To change a PIN: see `04-manual-update-guide.md` → "Change the EASI 2025 PIN".

---

## Firebase Configuration

These values are already embedded in `ProtocolAssistant.html`. Recorded here for rebuild reference.

```javascript
firebase.initializeApp({
  apiKey:            "AIzaSyAcnp4uXeOgzuzIHpO5UL6Eq9fvhVHFs7Y",
  authDomain:        "emsprotocolapp.firebaseapp.com",
  projectId:         "emsprotocolapp",
  storageBucket:     "emsprotocolapp.firebasestorage.app",
  messagingSenderId: "498482397906",
  appId:             "1:498482397906:web:5517abc5d83cf6cf15e30b"
});
```

**Note:** Firebase API keys for web apps are designed to be public. They identify your project but do not grant write access — that is controlled by Firestore security rules and Firebase Auth.

---

## Firestore Data Locations

| Data | Firestore path |
|------|---------------|
| EASI 2026 protocols/meds/contacts | `service_data/easi-2026` |
| User favorites & settings | `appdata/[user-uid]` |

---

## Key localStorage Keys (on each user's device)

| Key | Contents |
|-----|---------|
| `ems-protocols-multi-v1` | User state: current service, favorites, preferences |
| `easi_svc_v2` | Cached copy of EASI 2026 service data |
| `pref_tab` | Last active tab (protocols/meds/resources/contacts) |
| `pref_hdr` | Header collapsed state |
| `pref_cats` | Collapsed protocol categories |

These are stored in the user's browser. Clearing browser data or using Update App removes `easi_svc_v2` but preserves `ems-protocols-multi-v1` (favorites are safe).

---

## Repository

| Item | Value |
|------|-------|
| GitHub repo | https://github.com/pairamedic/protocolassistant |
| Live app URL | https://pairamedic.github.io/protocolassistant/ProtocolAssistant.html |
| Production branch | `main` |
| AI dev branch | `claude/easi-protocols-2026-service-c30fH` |

---

## Security Notes

- The admin email is visible in the HTML source — this is unavoidable in a client-side app. Access still requires the Firebase Auth password.
- The EASI 2025 PIN is stored as a SHA-256 hash in source — the plain value above should be kept private.
- Firestore security rules restrict writes to the admin email only. Even if someone opens the admin panel via browser console, cloud saves will be rejected by Firestore for non-admin accounts.
- Firebase Auth manages all login sessions. If you suspect compromise, change your Firebase Auth password at https://console.firebase.google.com → Authentication → Users.
