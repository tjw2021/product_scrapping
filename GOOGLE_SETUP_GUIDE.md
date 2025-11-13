# 🔐 Google Sheets API Setup Guide

## Complete Step-by-Step Instructions with Visuals

### Part 1: Google Cloud Console Setup

#### Step 1: Create a Google Cloud Project

1. **Go to Google Cloud Console**
   - URL: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create New Project**
   - Click the project dropdown at the top (says "Select a project")
   - Click "NEW PROJECT" button
   - Project Name: `Solar Inventory Scraper` (or any name you want)
   - Click "CREATE"
   - Wait for project creation (takes ~10 seconds)

3. **Select Your New Project**
   - Click the project dropdown again
   - Select your newly created project

---

#### Step 2: Enable Required APIs

1. **Navigate to API Library**
   - In left sidebar, click "APIs & Services" → "Library"
   - Or search for "API Library" in the search bar

2. **Enable Google Sheets API**
   - In the API Library search box, type: `Google Sheets API`
   - Click on "Google Sheets API"
   - Click the blue "ENABLE" button
   - Wait for it to enable (~5 seconds)

3. **Enable Google Drive API**
   - Click "Library" again in the left sidebar
   - Search for: `Google Drive API`
   - Click on "Google Drive API"
   - Click the blue "ENABLE" button

---

#### Step 3: Create Service Account

1. **Navigate to Credentials**
   - In left sidebar: "APIs & Services" → "Credentials"

2. **Create Service Account**
   - Click "+ CREATE CREDENTIALS" at top
   - Select "Service Account"

3. **Service Account Details**
   - Service account name: `solar-scraper-bot`
   - Service account ID: (auto-filled, leave as is)
   - Description: `Bot for scraping solar panel inventory`
   - Click "CREATE AND CONTINUE"

4. **Grant Access (Optional)**
   - Skip this step by clicking "CONTINUE"

5. **Grant Users Access (Optional)**
   - Skip this step by clicking "DONE"

---

#### Step 4: Create and Download JSON Key

1. **Find Your Service Account**
   - You should see your new service account in the list
   - Email format: `solar-scraper-bot@your-project-id.iam.gserviceaccount.com`
   - **COPY THIS EMAIL - YOU'LL NEED IT!**

2. **Create Key**
   - Click on your service account name
   - Click the "KEYS" tab at the top
   - Click "ADD KEY" → "Create new key"

3. **Download Key**
   - Select "JSON" format
   - Click "CREATE"
   - A JSON file will download automatically
   - **Save this file safely!** (Name it `credentials.json`)

⚠️ **IMPORTANT**: This JSON file contains secret credentials. Never share it publicly or commit it to GitHub!

---

### Part 2: Google Sheets Setup

#### Step 5: Create Your Inventory Sheet

1. **Create New Google Sheet**
   - Go to: https://sheets.google.com
   - Click "+ Blank" to create new spreadsheet
   - Name it: `Solar Cellz USA Inventory`

2. **Share with Service Account**
   - Click the "Share" button (top right)
   - In the "Add people and groups" field, paste your service account email:
     `solar-scraper-bot@your-project-id.iam.gserviceaccount.com`
   - Change permission from "Viewer" to "Editor"
   - **UNCHECK** "Notify people" (it's a bot, not a person)
   - Click "Share" or "Done"

✅ **Your sheet is now ready!** The bot can read and write to it.

---

### Part 3: Verify Setup

#### Quick Verification Checklist

- [ ] Google Cloud project created
- [ ] Google Sheets API enabled
- [ ] Google Drive API enabled  
- [ ] Service account created
- [ ] JSON key file downloaded as `credentials.json`
- [ ] Service account email copied
- [ ] Google Sheet created
- [ ] Google Sheet shared with service account email (as Editor)

---

### Part 4: Using Your Credentials

#### Option A: Upload File to Replit

1. In Replit, click the "Files" icon
2. Click the three dots (⋮) → "Upload file"
3. Upload your `credentials.json` file
4. The scraper will automatically find and use it

#### Option B: Use Environment Variables (More Secure)

1. Open your `credentials.json` file in a text editor
2. Copy the ENTIRE contents (should start with `{` and end with `}`)
3. In Replit, go to "Secrets" (lock icon in left sidebar)
4. Add new secret:
   - Key: `GOOGLE_CREDENTIALS`
   - Value: (paste the entire JSON contents)
5. Click "Add new secret"

The scraper will check for the environment variable first, then fall back to the file.

---

### Part 5: Common Issues & Solutions

#### Issue: "Permission Denied" Error

**Cause**: Sheet not shared with service account

**Solution**:
1. Open your Google Sheet
2. Click "Share" button
3. Make sure the service account email is listed
4. Make sure it has "Editor" permission (not just "Viewer")

---

#### Issue: "Can't Find Credentials" Error

**Cause**: File not in right location or environment variable not set

**Solution**:
1. Make sure `credentials.json` is in the same folder as your script
2. OR make sure `GOOGLE_CREDENTIALS` environment variable is set
3. Check that the JSON is valid (not corrupted)

---

#### Issue: API Not Enabled

**Cause**: Forgot to enable Google Sheets API or Google Drive API

**Solution**:
1. Go back to Google Cloud Console
2. Navigate to "APIs & Services" → "Library"
3. Search for and enable both:
   - Google Sheets API
   - Google Drive API

---

#### Issue: "Invalid Grant" Error

**Cause**: Service account key might be deleted or project changed

**Solution**:
1. Create a new service account key
2. Download new JSON credentials
3. Replace old credentials with new ones

---

### Part 6: Security Best Practices

#### ✅ DO:
- Store credentials in environment variables when possible
- Keep credentials.json file secure and never share it
- Use service accounts (not personal OAuth)
- Regularly audit who has access to your Google Sheet
- Delete old/unused service accounts

#### ❌ DON'T:
- Commit credentials to GitHub or public repositories
- Share your credentials.json file with anyone
- Use the same credentials across multiple projects
- Leave credentials in plain text files on shared computers
- Hard-code credentials in your source code

---

### Part 7: What Your JSON File Contains

Your `credentials.json` file includes:

```json
{
  "type": "service_account",
  "project_id": "your-project-name-123456",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "solar-scraper-bot@your-project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  ...
}
```

The key fields the scraper uses:
- `client_email`: The service account email (share your sheet with this!)
- `private_key`: Secret key for authentication (keep this safe!)
- `project_id`: Your Google Cloud project identifier

---

### Need Help?

If you're stuck:
1. Check all checkboxes in the verification list above
2. Review the common issues section
3. Make sure APIs are enabled in Google Cloud Console
4. Verify sheet is shared with correct email
5. Try creating a new service account and starting fresh

Remember: The most common issue is forgetting to share the Google Sheet with the service account email!
