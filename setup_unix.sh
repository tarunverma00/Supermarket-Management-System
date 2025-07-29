# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE} SUPERMARKET MANAGEMENT SYSTEM - COMPLETE SETUP${NC}"
echo -e "${BLUE}================================================${NC}"
echo
echo "This script will automatically:"
echo "  - Check Python installation"
echo "  - Install required dependencies"
echo "  - Set up MySQL database"
echo "  - Create admin user account"
echo

# Check Python installation
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    # Check if it's Python 3
    if [[ $PYTHON_VERSION == 3.* ]]; then
        echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
        PYTHON_CMD="python"
    else
        echo -e "${RED}❌ Python 3.8+ required, found Python $PYTHON_VERSION${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Python is not installed${NC}"
    echo
    echo "Please install Python 3.8+ and try again:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip"
    echo "  CentOS/RHEL:   sudo yum install python3 python3-pip"
    echo "  macOS:         brew install python3"
    exit 1
fi

# Check Python version
VERSION_CHECK=$($PYTHON_CMD -c "import sys; print(sys.version_info >= (3, 8))")
if [ "$VERSION_CHECK" != "True" ]; then
    echo -e "${RED}❌ Python 3.8 or higher required${NC}"
    echo -e "   Current version: $PYTHON_VERSION"
    exit 1
fi

# Check MySQL availability
echo
echo "Checking MySQL availability..."
if command -v mysql &> /dev/null; then
    MYSQL_VERSION=$(mysql --version 2>&1 | awk '{print $5}' | sed 's/,//')
    echo -e "${GREEN}✅ MySQL tools found - $MYSQL_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️  MySQL command line tools not found in PATH${NC}"
    echo "MySQL server should still be accessible via Python"
fi

# Make the automated setup script executable
chmod +x automated_setup.py 2>/dev/null

echo
echo "Starting automated setup..."
echo

# Run the automated setup script
$PYTHON_CMD automated_setup.py

# Check if setup was successful
if [ $? -eq 0 ]; then
    echo
    echo -e "${GREEN}✅ Setup completed successfully!${NC}"
    echo
    echo -e "${BLUE}🚀 You can now run the application with:${NC}"
    echo "   $PYTHON_CMD main.py"
    echo
    echo -e "${BLUE}🔐 Use the login credentials shown above${NC}"
    echo
else
    echo
    echo -e "${RED}❌ Setup failed! Please check the error messages above.${NC}"
    echo
    echo "Common solutions:"
    echo "  - Make sure MySQL server is running"
    echo "  - Check your MySQL credentials"
    echo "  - Ensure you have proper permissions"
    echo "  - Try: sudo systemctl start mysql (Linux)"
    echo "  - Try: brew services start mysql (macOS)"
    exit 1
fi
