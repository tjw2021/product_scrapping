"""
Interactive Google Sheets Setup Helper
Guides you through the entire setup process
"""

import os
import sys
import json
import webbrowser


def print_step(number, title):
    """Print step header"""
    print(f"\n{'='*70}")
    print(f"  STEP {number}: {title}")
    print(f"{'='*70}\n")


def wait_for_user():
    """Wait for user to press Enter"""
    input("\nPress Enter when you've completed this step...")


def check_credentials():
    """Check if credentials.json exists"""
    if os.path.exists('credentials.json'):
        try:
            with open('credentials.json', 'r') as f:
                creds = json.load(f)

            if 'client_email' in creds:
                return True, creds['client_email']
        except:
            pass

    return False, None


def main():
    """Interactive setup wizard"""

    print("\n" + "="*70)
    print("  🌞 GOOGLE SHEETS API SETUP WIZARD")
    print("="*70)
    print("\nThis wizard will guide you through setting up Google Sheets API.")
    print("The entire process takes about 5-10 minutes.\n")

    wait_for_user()

    # Check if already set up
    has_creds, email = check_credentials()

    if has_creds:
        print(f"\n✅ Found existing credentials.json")
        print(f"   Service account email: {email}")
        print("\nDo you want to:")
        print("  1. Use existing credentials")
        print("  2. Set up new credentials")

        choice = input("\nEnter 1 or 2: ").strip()

        if choice == "1":
            print("\n✅ Using existing credentials!")
            print(f"\n⚠️  IMPORTANT: Make sure your Google Sheet is shared with:")
            print(f"   {email}")
            print(f"   Grant 'Editor' permissions")

            input("\nPress Enter to continue to sheet setup...")
            setup_google_sheet(email)
            return

    # Step 1: Google Cloud Console
    print_step(1, "Access Google Cloud Console")

    print("We'll open Google Cloud Console in your browser.")
    print("\nWhat to do:")
    print("  1. Sign in with your Google account")
    print("  2. If you see a welcome page, click through it")

    wait_for_user()

    try:
        webbrowser.open('https://console.cloud.google.com/')
        print("\n✅ Opened Google Cloud Console in your browser")
    except:
        print("\n⚠️  Please manually open: https://console.cloud.google.com/")

    wait_for_user()

    # Step 2: Create Project
    print_step(2, "Create a New Project")

    print("In Google Cloud Console:")
    print("  1. Click the project dropdown at the top (says 'Select a project')")
    print("  2. Click 'NEW PROJECT' button")
    print("  3. Project name: 'Solar Inventory Scraper' (or any name)")
    print("  4. Click 'CREATE'")
    print("  5. Wait for project to be created (takes ~30 seconds)")
    print("  6. Select your new project from the dropdown")

    wait_for_user()

    # Step 3: Enable APIs
    print_step(3, "Enable Required APIs")

    print("We need to enable 2 APIs. Let's do them one at a time.\n")

    print("📌 FIRST API: Google Sheets API")
    print("\nWhat to do:")
    print("  1. In the search bar at top, type 'Google Sheets API'")
    print("  2. Click on 'Google Sheets API' in results")
    print("  3. Click the blue 'ENABLE' button")
    print("  4. Wait for it to enable (~10 seconds)")

    wait_for_user()

    print("\n📌 SECOND API: Google Drive API")
    print("\nWhat to do:")
    print("  1. Click the back button or use search bar again")
    print("  2. Search for 'Google Drive API'")
    print("  3. Click on 'Google Drive API' in results")
    print("  4. Click the blue 'ENABLE' button")
    print("  5. Wait for it to enable (~10 seconds)")

    wait_for_user()

    # Step 4: Create Service Account
    print_step(4, "Create Service Account")

    print("Now we'll create a service account (this is like a 'bot' user).\n")
    print("What to do:")
    print("  1. In the left sidebar, click 'Credentials'")
    print("     (or search 'Credentials' at the top)")
    print("  2. Click '+ CREATE CREDENTIALS' at the top")
    print("  3. Select 'Service Account'")
    print("  4. Service account name: 'solar-scraper-bot' (or any name)")
    print("  5. Click 'CREATE AND CONTINUE'")
    print("  6. Skip the optional steps - click 'CONTINUE' then 'DONE'")

    wait_for_user()

    # Step 5: Create Key
    print_step(5, "Download Credentials JSON")

    print("Now we'll download the credentials file.\n")
    print("What to do:")
    print("  1. You should see your service account in the list")
    print("  2. Click on the service account (the email address)")
    print("  3. Go to the 'KEYS' tab at the top")
    print("  4. Click 'ADD KEY' → 'Create new key'")
    print("  5. Choose 'JSON' format")
    print("  6. Click 'CREATE'")
    print("  7. A JSON file will download automatically")
    print("\n⚠️  IMPORTANT: This file contains secrets. Keep it safe!")

    wait_for_user()

    # Step 6: Move credentials file
    print_step(6, "Move Credentials to Project Folder")

    print("The JSON file is probably in your Downloads folder.\n")
    print("We need to:")
    print("  1. Rename it to 'credentials.json'")
    print("  2. Move it to this folder:")
    print(f"     {os.path.abspath('.')}")

    print("\nI'll wait while you do this...")

    while True:
        wait_for_user()

        if os.path.exists('credentials.json'):
            try:
                with open('credentials.json', 'r') as f:
                    creds = json.load(f)

                if 'client_email' in creds:
                    email = creds['client_email']
                    print(f"\n✅ Perfect! Found credentials.json")
                    print(f"   Service account email: {email}")
                    break
                else:
                    print("\n⚠️  File found but doesn't look right. Make sure it's the JSON file from Google Cloud.")
            except:
                print("\n⚠️  File found but couldn't read it. Make sure it's a valid JSON file.")
        else:
            print(f"\n⚠️  Can't find credentials.json in: {os.path.abspath('.')}")
            print("    Please move the file here and press Enter again.")

    # Step 7: Create and Share Google Sheet
    setup_google_sheet(email)

    # Step 8: Test Connection
    print_step(8, "Test the Connection")

    print("Let's test if everything is working!\n")
    print("I'll run a quick test to verify the setup...")

    wait_for_user()

    print("\n🧪 Running connection test...\n")

    # Run test
    os.system('python test_setup.py')

    # Done!
    print("\n" + "="*70)
    print("  🎉 SETUP COMPLETE!")
    print("="*70)
    print("\nYou're ready to run the scraper!")
    print("\nNext steps:")
    print("  1. Run once:      python main.py")
    print("  2. Run scheduled: python scheduled_runner.py")
    print("\n📚 For more info, see QUICK_START.md")
    print("="*70 + "\n")


def setup_google_sheet(service_account_email):
    """Guide user through creating and sharing Google Sheet"""

    print_step(7, "Create and Share Google Sheet")

    print("Now we need to create a Google Sheet and share it with the bot.\n")

    print("📌 CREATE THE SHEET:")
    print("  1. Go to https://sheets.google.com")
    print("  2. Click '+ Blank' to create a new sheet")
    print("  3. Name it: 'Solar Inventory Tracker' (or any name)")
    print("  4. Remember the name - you'll need it later!")

    wait_for_user()

    print("\n📌 SHARE WITH SERVICE ACCOUNT:")
    print(f"\n  ⚠️  CRITICAL STEP - Copy this email address:\n")
    print(f"  {service_account_email}\n")

    print("  Now in your Google Sheet:")
    print("  1. Click the 'Share' button (top right)")
    print("  2. Paste the service account email")
    print("  3. Make sure role is set to 'Editor'")
    print("  4. UNCHECK 'Notify people' (it's a bot, not a person)")
    print("  5. Click 'Share' or 'Done'")

    print("\n✅ Your sheet is now ready to receive data!")

    wait_for_user()

    # Ask for sheet name
    print("\n📝 What did you name your Google Sheet?")
    sheet_name = input("Enter sheet name (or press Enter for 'Solar Inventory Tracker'): ").strip()

    if not sheet_name:
        sheet_name = "Solar Inventory Tracker"

    print(f"\n✅ Sheet name: {sheet_name}")
    print("\nI'll set this as your default sheet name.")

    # Update .env or create it
    env_content = f"GOOGLE_SHEET_NAME={sheet_name}\n"

    if os.path.exists('.env'):
        print("\n⚠️  .env file already exists. Adding sheet name...")
        with open('.env', 'a') as f:
            f.write(f"\n{env_content}")
    else:
        print("\n📝 Creating .env file with your settings...")
        with open('.env', 'w') as f:
            f.write(env_content)

    print(f"✅ Saved to .env file")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup cancelled by user")
        sys.exit(1)
