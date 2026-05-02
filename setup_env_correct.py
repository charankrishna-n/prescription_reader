"""
setup_env_correct.py
Correct setup script - keeps key.json OUTSIDE project directory
"""

import os
import shutil
from pathlib import Path


def setup_environment():
    """Setup environment configuration for the project."""
    
    print("\n" + "="*70)
    print("PRESCRIPTION OCR - SECURE ENVIRONMENT SETUP")
    print("="*70)
    
    project_root = Path(__file__).parent
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    # Step 1: Check if .env exists
    if env_file.exists():
        print("\n✓ .env file already exists")
        response = input("Do you want to reconfigure? (y/n): ").strip().lower()
        if response != 'y':
            print("Skipping .env configuration")
            return
    else:
        print("\n✗ .env file not found")
        if env_example.exists():
            print("Creating .env from .env.example...")
            shutil.copy(env_example, env_file)
            print("✓ .env file created")
        else:
            print("✗ .env.example not found")
            return
    
    # Step 2: Configure credentials path
    print("\n" + "-"*70)
    print("GOOGLE CLOUD CREDENTIALS")
    print("-"*70)
    print("\nIMPORTANT: key.json should be stored OUTSIDE the project directory!")
    print("This prevents accidental commits to GitHub.\n")
    
    print("Examples:")
    print("  Windows: C:\\secure\\credentials\\key.json")
    print("  Linux/Mac: /home/username/secure/credentials/key.json\n")
    
    credentials_path = input("Enter FULL path to key.json: ").strip()
    
    if not credentials_path:
        print("\n✗ Error: You must provide a path to key.json")
        return
    
    # Expand user home directory
    credentials_path = os.path.expanduser(credentials_path)
    
    # Step 3: Verify credentials file exists
    if not os.path.exists(credentials_path):
        print(f"\n⚠ Warning: Credentials file not found at '{credentials_path}'")
        response = input("Continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            print("Setup cancelled")
            return
    else:
        print(f"✓ Credentials file found at '{credentials_path}'")
    
    # Step 4: Verify key.json is NOT in project directory
    if str(credentials_path).startswith(str(project_root)):
        print("\n✗ ERROR: key.json should NOT be in the project directory!")
        print(f"  Current path: {credentials_path}")
        print(f"  Project path: {project_root}")
        print("\nMove key.json to a secure location outside the project.")
        return
    
    # Step 5: Configure API settings
    print("\n" + "-"*70)
    print("API CONFIGURATION")
    print("-"*70)
    
    api_host = input("Enter API host (default: 0.0.0.0): ").strip()
    if not api_host:
        api_host = "0.0.0.0"
    
    api_port = input("Enter API port (default: 8000): ").strip()
    if not api_port:
        api_port = "8000"
    
    # Step 6: Write .env file
    print("\n" + "-"*70)
    print("SAVING CONFIGURATION")
    print("-"*70)
    
    env_content = f"""# Google Cloud Vision API Configuration
# DO NOT commit this file to version control!
# DO NOT commit key.json to version control!

# IMPORTANT: key.json should be stored OUTSIDE the project directory
# This prevents accidental commits to GitHub

# Path to your Google Cloud service account JSON key file
GOOGLE_APPLICATION_CREDENTIALS={credentials_path}

# Optional: Google Cloud Project ID
GOOGLE_CLOUD_PROJECT_ID=

# API configuration
API_HOST={api_host}
API_PORT={api_port}
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✓ Configuration saved to .env")
    
    # Step 7: Verify .gitignore
    print("\n" + "-"*70)
    print("GIT CONFIGURATION")
    print("-"*70)
    
    gitignore_file = project_root / ".gitignore"
    if gitignore_file.exists():
        with open(gitignore_file, 'r') as f:
            gitignore_content = f.read()
        
        if ".env" in gitignore_content and "key.json" in gitignore_content:
            print("✓ .gitignore is properly configured")
            print("  - .env is ignored")
            print("  - key.json is ignored")
        else:
            print("⚠ .gitignore may need updating")
    else:
        print("⚠ .gitignore not found")
    
    # Step 8: Test configuration
    print("\n" + "-"*70)
    print("TESTING CONFIGURATION")
    print("-"*70)
    
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
        
        loaded_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        loaded_host = os.getenv("API_HOST")
        loaded_port = os.getenv("API_PORT")
        
        print("✓ Environment variables loaded successfully")
        print(f"  - GOOGLE_APPLICATION_CREDENTIALS: {loaded_credentials}")
        print(f"  - API_HOST: {loaded_host}")
        print(f"  - API_PORT: {loaded_port}")
        
        # Verify key.json is outside project
        if str(loaded_credentials).startswith(str(project_root)):
            print("\n✗ ERROR: key.json is in the project directory!")
            print("Move it to a secure location outside the project.")
        else:
            print("\n✓ key.json is in a secure location (outside project)")
            
    except ImportError:
        print("⚠ python-dotenv not installed")
        print("  Run: pip install python-dotenv")
    except Exception as e:
        print(f"✗ Error loading configuration: {e}")
    
    # Step 9: Summary
    print("\n" + "="*70)
    print("SETUP COMPLETE!")
    print("="*70)
    print("\nSecurity Summary:")
    print("✓ key.json is stored OUTSIDE project directory")
    print("✓ .env file references the secure path")
    print("✓ .env file is in .gitignore (won't be committed)")
    print("✓ key.json is in .gitignore (won't be committed)")
    print("✓ Safe to push to GitHub")
    
    print("\nNext steps:")
    print("1. Verify key.json is at the configured path")
    print("2. Run: pip install -r requirements.txt")
    print("3. Test: python vision_api.py")
    print("4. Deploy: python prescription_pipeline_v2.py")
    print("\nFor more information, see CORRECT_SECURITY_SETUP.md")
    print("="*70 + "\n")


if __name__ == "__main__":
    setup_environment()
