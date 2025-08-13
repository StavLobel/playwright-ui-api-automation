#!/bin/bash

# Allure Report Server Script
# Serves the Allure report locally for development

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Java is available
if ! command -v java &> /dev/null; then
    echo -e "${RED}❌ Java is not installed. Please install Java 11+ to run Allure reports.${NC}"
    echo "On macOS: brew install openjdk@11"
    exit 1
fi

# Check if Allure is available
if ! command -v allure &> /dev/null; then
    echo -e "${RED}❌ Allure CLI is not installed.${NC}"
    echo "Install with: npm install -g allure-commandline"
    exit 1
fi

# Check if allure-results directory exists
if [ ! -d "allure-results" ]; then
    echo -e "${YELLOW}⚠️  No allure-results directory found. Running tests first...${NC}"
    make test-all
fi

# Serve the Allure report
echo -e "${GREEN}🚀 Starting Allure report server...${NC}"
echo -e "${YELLOW}💡 The report will open in your default browser${NC}"
echo -e "${YELLOW}💡 Press Ctrl+C to stop the server${NC}"
echo ""

# Set Java path if on macOS with Homebrew Java
if [[ "$OSTYPE" == "darwin"* ]] && [ -d "/opt/homebrew/opt/openjdk@11" ]; then
    export PATH="/opt/homebrew/opt/openjdk@11/bin:$PATH"
fi

# Serve the report
allure serve allure-results
