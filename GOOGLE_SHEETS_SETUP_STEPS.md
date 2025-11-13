# Google Sheets API Setup - Step by Step 🚀

## Overview

This guide walks you through setting up Google Sheets API access. Takes ~5-10 minutes.

**Alternative:** Run `python setup_google_sheets.py` for an interactive guided wizard!

---

## Step 1: Access Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. If you see a welcome page, click through it

---

## Step 2: Create a New Project

1. Click the **project dropdown** at the top (says "Select a project")
2. Click **"NEW PROJECT"** button (top right)
3. **Project name:** "Solar Inventory Scraper" (or any name you like)
4. Click **"CREATE"**
5. Wait ~30 seconds for project creation
6. **Select your new project** from the dropdown

---

## Step 3: Enable Google Sheets API

1. In the **search bar** at top, type: `Google Sheets API`
2. Click on **"Google Sheets API"** in the results
3. Click the blue **"ENABLE"** button
4. Wait ~10 seconds for it to enable

---

## Step 4: Enable Google Drive API

1. Go back or use search bar again
2. Search: `Google Drive API`
3. Click on **"Google Drive API"**
4. Click the blue **"ENABLE"** button
5. Wait ~10 seconds for it to enable

---

## Step 5: Create Service Account

A service account is like a "bot user" that will access your sheet.

1. In the left sidebar, click **"Credentials"**
   - Or search "Credentials" at the top
2. Click **"+ CREATE CREDENTIALS"** (top of page)
3. Select **"Service Account"**
4. **Service account name:** `solar-scraper-bot` (or any name)
5. **Service account ID:** Will auto-fill (leave as is)
6. Click **"CREATE AND CONTINUE"**
7. **Skip optional steps:** Click "CONTINUE" → "DONE"

---

## Step 6: Create and Download Key

1. You should see your service account listed
2. **Click on the service account** (click the email address)
3. Go to the **"KEYS"** tab at the top
4. Click **"ADD KEY"** → **"Create new key"**
5. Choose **"JSON"** format
6. Click **"CREATE"**
7. A JSON file will **download automatically** to your Downloads folder

⚠️ **IMPORTANT:** This file contains secrets. Keep it safe and never share it publicly!

---

## Step 7: Move Credentials File

1. Find the downloaded JSON file (probably in Downloads)
2. **Rename it to:** `credentials.json`
3. **Move it to your project folder:**
   ```
   /home/user/product_scrapping/credentials.json
   ```

You can use:
```bash
mv ~/Downloads/your-project-*.json /home/user/product_scrapping/credentials.json
```

---

## Step 8: Create Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Click **"+ Blank"** to create a new spreadsheet
3. **Name it:** "Solar Inventory Tracker" (or your preferred name)
4. **Remember this name** - you'll need it!

---

## Step 9: Share Sheet with Service Account

This is the **most critical step**!

1. Open the `credentials.json` file and find the `client_email` field
   - It looks like: `solar-scraper-bot@your-project-123456.iam.gserviceaccount.com`

2. In your Google Sheet, click **"Share"** button (top right)

3. **Paste the service account email** in the "Add people" field

4. Make sure the role is set to **"Editor"**

5. **UNCHECK "Notify people"** (it's a bot, doesn't need email)

6. Click **"Share"** or **"Done"**

✅ Your sheet is now accessible by the scraper!

---

## Step 10: Configure Environment Variable

Create a `.env` file in your project folder:

```bash
# Create .env file
cat > .env << 'EOF'
GOOGLE_SHEET_NAME=Solar Inventory Tracker
EOF
```

Or if your sheet has a different name:
```bash
echo 'GOOGLE_SHEET_NAME=Your Sheet Name Here' > .env
```

---

## Step 11: Test the Setup

Run the test script to verify everything works:

```bash
python test_setup.py
```

This will check:
- ✅ Credentials file is valid
- ✅ Can connect to Google Sheets
- ✅ Scrapers are working
- ✅ Configuration is correct

---

## Troubleshooting

### "Permission denied" Error

**Problem:** Scraper can't access the sheet

**Solution:**
1. Make sure you **shared the sheet** with the service account email
2. Check the email is correct (from credentials.json → `client_email`)
3. Grant **"Editor"** permissions (not just Viewer)
4. Make sure sheet name matches exactly (case-sensitive!)

### "Spreadsheet not found" Error

**Problem:** Can't find your Google Sheet

**Solution:**
1. Check `GOOGLE_SHEET_NAME` in `.env` matches exactly
2. Make sure the sheet is shared with service account
3. Try opening the sheet manually to confirm it exists

### Can't Find credentials.json

**Problem:** File not in correct location

**Solution:**
```bash
# Check if file exists
ls -la /home/user/product_scrapping/credentials.json

# If not there, find it
find ~ -name "*.json" -path "*/Downloads/*"

# Move it
mv ~/Downloads/your-file.json /home/user/product_scrapping/credentials.json
```

### JSON Parsing Error

**Problem:** credentials.json is corrupted or wrong file

**Solution:**
1. Open the file and check it's valid JSON
2. Should start with: `{"type": "service_account", ...}`
3. If corrupted, re-download from Google Cloud Console

---

## Security Best Practices

⚠️ **NEVER commit credentials.json to git!**

The `.gitignore` should include:
```
credentials.json
*.json
.env
```

For production, use environment variables instead:
```bash
export GOOGLE_CREDENTIALS='{"type":"service_account",...}'
```

---

## Next Steps

Once setup is complete:

✅ **Test the connection:**
```bash
python test_setup.py
```

✅ **Run the scraper once:**
```bash
python main.py
```

✅ **Run scheduled scraper:**
```bash
python scheduled_runner.py
```

---

## Need Help?

- Run interactive setup wizard: `python setup_google_sheets.py`
- Read full guide: `COMPLETE_GUIDE.md`
- Check troubleshooting section above

---

**You're all set!** 🎉

Once you see "All tests passed!" from `test_setup.py`, you're ready to start scraping!
