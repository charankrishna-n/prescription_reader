"""
setup_env.py
Quick setup script to configure environment variables
"""

import os
import shutil
from pathlib import Path


def setup_environment():
    """Setup environment configuration for the project."""
    
    print("\n" + "="*60)
    print("PRESCRIPTION OCR - ENVIRONMENT SETUP")
    print("="*60)
    
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
    print("\n" + "-"*60)
    print("GOOGLE CLOUD CREDENTIALS")
    print("-"*60)
    
    credentials_path = input("Enter path to Google Cloud key.json (default: key.json): ").strip()
    if not credentials_path:
        credentials_path = "key.json"
    
    # Step 3: Verify credentials file exists
    if not os.path.exists(credentials_path):
        print(f"\n⚠ Warning: Credentials file not found at '{credentials_path}'")
        print("Make sure to place your key.json file in the project directory")
    else:
        print(f"✓ Credentials file found at '{credentials_path}'")
    
    # Step 4: Configure API settings
    print("\n" + "-"*60)
    print("API CONFIGURATION")
    print("-"*60)
    
    api_host = input("Enter API host (default: 0.0.0.0): ").strip()
    if not api_host:
        api_host = "0.0.0.0"
    
    api_port = input("Enter API port (default: 8000): ").strip()
    if not api_port:
        api_port = "8000"
    
    # Step 5: Write .env file
    print("\n" + "-"*60)
    print("SAVING CONFIGURATION")
    print("-"*60)
    
    env_content = f"""# Google Cloud Vision API Configuration
# DO NOT commit this file to version control!

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
    
    # Step 6: Verify .gitignore
    print("\n" + "-"*60)
    print("GIT CONFIGURATION")
    print("-"*60)
    
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
    
    # Step 7: Test configuration
    print("\n" + "-"*60)
    print("TESTING CONFIGURATION")
    print("-"*60)
    
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
    except ImportError:
        print("⚠ python-dotenv not installed")
        print("  Run: pip install python-dotenv")
    except Exception as e:
        print(f"✗ Error loading configuration: {e}")
    
    # Step 8: Summary
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Ensure key.json is in the project directory")
    print("2. Run: pip install -r requirements.txt")
    print("3. Test: python vision_api.py")
    print("4. Deploy: python prescription_pipeline_v2.py")
    print("\nFor more information, see ENVIRONMENT_SETUP.md")
    print("="*60 + "\n")


if __name__ == "__main__":
    setup_environment()
