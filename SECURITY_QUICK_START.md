"""
QUICK START - SECURITY SETUP
=============================

WHAT WAS DONE
-------------
✓ API credentials moved from code to .env file
✓ .env file added to .gitignore (won't be committed)
✓ .env.example created as template
✓ Code updated to load credentials from environment
✓ python-dotenv added to requirements.txt

SETUP (5 MINUTES)
-----------------

1. Install dependencies:
   pip install -r requirements.txt

2. Create .env file:
   cp .env.example .env

3. Edit .env and add your credentials:
   GOOGLE_APPLICATION_CREDENTIALS=key.json

4. Place key.json in project root

5. Test:
   python vision_api.py

VERIFY SETUP
------------

Check that .env is NOT in git:
  git status
  
Should NOT show:
  - .env
  - key.json

Check that .env.example IS in git:
  git status
  
Should show:
  - .env.example

PUSH TO GITHUB
--------------

Your credentials are safe:
  git push origin main

Only these files are pushed:
  ✓ .env.example (template)
  ✓ .gitignore (configuration)
  ✓ All code files
  ✓ Documentation

NOT pushed:
  ✗ .env (your credentials)
  ✗ key.json (your API key)

TEAM MEMBER SETUP
-----------------

When someone clones your repo:

1. Clone:
   git clone https://github.com/user/repo.git

2. Setup:
   cp .env.example .env

3. Add credentials:
   Edit .env with their own credentials

4. Install:
   pip install -r requirements.txt

5. Run:
   python prescription_pipeline_v2.py

FILES CREATED
-------------

.env.example
  - Template for environment variables
  - Safe to commit
  - Shows required configuration

.env (created by you)
  - Your actual credentials
  - NOT committed (in .gitignore)
  - Created from .env.example

.gitignore
  - Prevents .env and key.json from being committed
  - Prevents __pycache__ and other build files

setup_env.py
  - Interactive setup script
  - Configures environment automatically

ENVIRONMENT_SETUP.md
  - Detailed setup guide
  - Troubleshooting tips

SECURITY_IMPROVEMENTS.md
  - What was changed
  - Best practices

COMMANDS
--------

Setup:
  python setup_env.py

Test:
  python vision_api.py

Run pipeline:
  python prescription_pipeline_v2.py

Run API:
  python api.py

Run tests:
  python test_extraction.py

TROUBLESHOOTING
---------------

Error: "Google Cloud credentials file not found"
Fix:
  1. Check .env exists
  2. Check GOOGLE_APPLICATION_CREDENTIALS path
  3. Check key.json exists
  4. Run: python setup_env.py

Error: "ModuleNotFoundError: No module named 'dotenv'"
Fix:
  pip install python-dotenv

Error: Still seeing "N/A" in extraction
Fix:
  1. Test credentials: python vision_api.py
  2. Check API quota
  3. Check image file
  4. Check debug output

SECURITY CHECKLIST
------------------

Before pushing to GitHub:

□ .env file created from .env.example
□ .env file is in .gitignore
□ key.json is in .gitignore
□ No hardcoded credentials in code
□ python-dotenv installed
□ Credentials loaded from environment
□ .env.example committed to git
□ .gitignore committed to git
□ Tested with python vision_api.py
□ Ready to push to GitHub

SUMMARY
-------

Your project is now secure for GitHub:

✓ Credentials in .env (not in code)
✓ .env not committed to git
✓ .env.example shows structure
✓ Easy for team members to set up
✓ Safe to push to GitHub

You're ready to go!
"""
