# How to Rebuild the EMS Protocol Assistant from Scratch

Follow these steps in order. Total time: approximately 45–60 minutes.

---

## PART 1 — Firebase Setup

### 1.1 Create a Firebase Project

1. Go to https://console.firebase.google.com
2. Click **Add project**
3. Name it (e.g. `emsprotocolapp`)
4. Disable Google Analytics (not needed)
5. Click **Create project**

### 1.2 Enable Email/Password Authentication

1. In the Firebase console sidebar → **Authentication** → **Get started**
2. Under **Sign-in method** tab → click **Email/Password**
3. Enable it → **Save**
4. Go to **Users** tab → **Add user**
5. Enter your admin email (e.g. `eliasacaldwellnrp@gmail.com`) and a strong password
6. Click **Add user**

### 1.3 Create a Firestore Database

1. Sidebar → **Firestore Database** → **Create database**
2. Choose **Start in production mode** → **Next**
3. Select a region (e.g. `us-central`) → **Enable**

### 1.4 Set Firestore Security Rules

1. Firestore → **Rules** tab
2. Replace the default rules with:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // Only the admin email can write service protocol data
    match /service_data/{doc} {
      allow read: if request.auth != null;
      allow write: if request.auth != null
                   && request.auth.token.email == 'eliasacaldwellnrp@gmail.com';
    }

    // Each user can read/write their own state doc
    match /users/{uid}/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == uid;
    }

    // App-level state (favorites sync)
    match /appdata/{doc} {
      allow read, write: if request.auth != null;
    }
  }
}
```

3. Click **Publish**

### 1.5 Get Your Firebase Config

1. Firebase console → Project settings (gear icon top left) → **General** tab
2. Scroll down to **Your apps** → click **Web** icon (`</>`) if no app registered
3. Register app name (e.g. `EMS Protocol Assistant`)
4. Copy the `firebaseConfig` object — you'll need these values:

```javascript
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};
```

---

## PART 2 — GitHub Repository Setup

### 2.1 Create the Repository

1. Go to https://github.com → **New repository**
2. Name: `protocolassistant` (or any name)
3. Set to **Public** (required for free GitHub Pages)
4. Do NOT add README, .gitignore, or license (start empty)
5. Click **Create repository**

### 2.2 Enable GitHub Pages

1. In the new repo → **Settings** → **Pages** (left sidebar)
2. Source: **Deploy from a branch**
3. Branch: **main** / `/ (root)`
4. Click **Save**
5. Your app will be live at: `https://YOUR-USERNAME.github.io/protocolassistant/ProtocolAssistant.html`

---

## PART 3 — File Setup

### 3.1 Required Files

You need exactly four files in the repo root:

| File | Purpose |
|------|---------|
| `ProtocolAssistant.html` | The entire app (HTML + CSS + JS inline) |
| `sw.js` | Service worker for PWA / offline caching |
| `manifest.json` | PWA install manifest |
| `easi-logo.jpg` | EASI Medics logo image |

All four files are in the `backup/` folder of this project docs folder.

### 3.2 Configure Firebase in ProtocolAssistant.html

Open `ProtocolAssistant.html` and find the Firebase config block (search for `firebaseConfig`). Replace with your values from Step 1.5:

```javascript
firebase.initializeApp({
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
});
```

### 3.3 Set the Admin Email

In `ProtocolAssistant.html`, find:

```javascript
const ADMIN_EMAILS = new Set(['eliasacaldwellnrp@gmail.com']);
```

Replace the email with your admin email if different.

### 3.4 Upload Files to GitHub

**Option A — GitHub Web UI (easiest):**
1. In your repo → click **Add file** → **Upload files**
2. Drag all four files in
3. Commit directly to `main`

**Option B — Git command line:**
```bash
git clone https://github.com/YOUR-USERNAME/protocolassistant.git
cd protocolassistant
# copy your four files here
git add .
git commit -m "Initial app setup"
git push origin main
```

---

## PART 4 — First Login and Data Seeding

### 4.1 Open the App

Go to `https://YOUR-USERNAME.github.io/protocolassistant/ProtocolAssistant.html`

### 4.2 Log In

Use the email and password you created in Firebase Auth (Step 1.2).

### 4.3 Seed Protocol Data to Firestore

On first login as the admin:
1. The app automatically seeds `EASI Protocols - 2026` from the hardcoded data in the HTML
2. Select **EASI Protocols - 2026** from the service dropdown
3. Tap ⚙️ (top right) → **Admin Panel** → **☁️ Push to Cloud**
4. Firestore now has the live protocol data — all users will load from there going forward

### 4.4 Verify the App Works

- Protocols tab shows protocols ✓
- Meds tab shows medications ✓
- Resources tab shows calculators ✓
- Contacts tab shows contact cards ✓
- ⚙️ button is visible (admin only) ✓

---

## PART 5 — PWA / Add to Home Screen

The app is already configured as a Progressive Web App. Users can:

**iPhone/iPad (Safari):**
1. Open the app in Safari
2. Tap the Share button (box with arrow)
3. Scroll down → **Add to Home Screen**
4. Tap **Add**

**Android (Chrome):**
1. Open the app in Chrome
2. Tap the three-dot menu → **Add to Home screen**

---

## PART 6 — Adding More Users

1. Firebase console → **Authentication** → **Users** → **Add user**
2. Enter their email and a temporary password
3. Tell them their login credentials
4. They log in on their device and can change their password via Firebase Auth

Users do NOT need admin access — they just need any valid Firebase Auth account on your project.

---

## Notes

- The app is entirely client-side. There is no server or backend beyond Firebase.
- Firebase Free tier (Spark plan) is sufficient for a small EMS crew.
- If you hit Firebase read/write limits, upgrade to the Blaze pay-as-you-go plan (typically pennies per month for this usage).
- `index.html` in the repo root just redirects to `ProtocolAssistant.html`.
