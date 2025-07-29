"""
Setup script for Supermarket Management System
"""
import os
import sys
import subprocess

def install_requirements():
    """Install required packages"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed!")
        return True
    except:
        print("❌ Failed to install requirements")
        return False

def main():
    print("🚀 Setting up Supermarket Management System...")
    
    if install_requirements():
        if not os.path.exists('.env'):
            if os.path.exists('.env.example'):
                import shutil
                shutil.copy('.env.example', '.env')
                print("✅ Created .env file - please edit with your credentials")
        
        print("\n✅ Setup completed!")
        print("📝 Next steps:")
        print("   1. Edit .env file with your database credentials")
        print("   2. Run: python setup_database.py")
        print("   3. Run: python main.py")
    else:
        print("❌ Setup failed!")

if __name__ == "__main__":
    main()
