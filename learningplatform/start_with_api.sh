#!/bin/bash

###############################################################################
# Start Script for Learning Tools and Learning Web Application (Linux/Ubuntu)
###############################################################################
# This script starts both the Learning Tools API and the Learning Web App
# and opens a browser to access the application.
#
# Prerequisites:
# - Python 3 must be installed
# - All required packages must be installed (see requirements.txt)
#
# Usage:
#   chmod +x start_with_api.sh
#   ./start_with_api.sh
###############################################################################

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Starting Learning Tools and Web Application"
echo "=========================================="
echo ""

# Check if Python 3 is installed
echo "Checking Python installation..."

# Use RobotPythonPath if set, otherwise fall back to python3
if [ -z "$RobotPythonPath" ]; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="$RobotPythonPath/python"
fi

if ! command -v $PYTHON_CMD &> /dev/null; then
    echo -e "${RED}Error: Python is not installed or not in PATH${NC}"
    echo "Please install Python or set RobotPythonPath environment variable."
    exit 1
fi

# Display Python version
PYTHON_VERSION=$($PYTHON_CMD --version)
echo -e "${GREEN}Found: $PYTHON_VERSION${NC}"
echo -e "${GREEN}Using: $PYTHON_CMD${NC}"
echo ""

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "=========================================="
    echo "Shutting down services..."
    echo "=========================================="
    
    if [ ! -z "$API_PID" ] && ps -p $API_PID > /dev/null 2>&1; then
        echo "Stopping Learning Tools API (PID: $API_PID)..."
        kill $API_PID 2>/dev/null
    fi
    
    if [ ! -z "$WEBAPP_PID" ] && ps -p $WEBAPP_PID > /dev/null 2>&1; then
        echo "Stopping Learning Web App (PID: $WEBAPP_PID)..."
        kill $WEBAPP_PID 2>/dev/null
    fi
    
    echo -e "${GREEN}Services stopped successfully${NC}"
    exit 0
}

# Set up trap to cleanup on script exit (Ctrl+C or normal exit)
trap cleanup SIGINT SIGTERM EXIT

# Get the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Bypass proxy for localhost connections
export NO_PROXY="localhost,127.0.0.1,::1"
export no_proxy="localhost,127.0.0.1,::1"

# Disable Jupyter detection (we're in API mode)
export LEARNINGTOOLS_DISABLE_JUPYTER_DETECTION=1

# Disable Flask debug mode in production
export FLASK_DEBUG=false

# Create logs directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/logs"

# Start Learning Tools API
echo "Starting Learning Tools API on port 5001..."
cd "$SCRIPT_DIR/learningtools" || {
    echo -e "${RED}Error: Cannot find learningtools directory${NC}"
    exit 1
}

$PYTHON_CMD api.py > "$SCRIPT_DIR/logs/api.log" 2>&1 &
API_PID=$!

if ps -p $API_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Learning Tools API started (PID: $API_PID)${NC}"
    echo "  Log: $SCRIPT_DIR/logs/api.log"
else
    echo -e "${RED}✗ Failed to start Learning Tools API${NC}"
    exit 1
fi

# Wait for API to initialize
echo "Waiting for API to initialize..."
sleep 3

# Check if API is still running
if ! ps -p $API_PID > /dev/null 2>&1; then
    echo -e "${RED}✗ API process died! Check logs:${NC}"
    tail -n 20 "$SCRIPT_DIR/logs/api.log"
    exit 1
fi

# Start Learning Web Application
echo "Starting Learning Web Application on port 5000..."
cd "$SCRIPT_DIR/learningwebapp" || {
    echo -e "${RED}Error: Cannot find learningwebapp directory${NC}"
    kill $API_PID
    exit 1
}

$PYTHON_CMD app.py > "$SCRIPT_DIR/logs/webapp.log" 2>&1 &
WEBAPP_PID=$!

if ps -p $WEBAPP_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Learning Web App started (PID: $WEBAPP_PID)${NC}"
    echo "  Log: $SCRIPT_DIR/logs/webapp.log"
else
    echo -e "${RED}✗ Failed to start Learning Web App${NC}"
    kill $API_PID
    exit 1
fi

# Wait for web app to initialize
echo "Waiting for web application to initialize..."
sleep 2

# Check if WebApp is still running
if ! ps -p $WEBAPP_PID > /dev/null 2>&1; then
    echo -e "${RED}✗ WebApp process died! Check logs:${NC}"
    tail -n 20 "$SCRIPT_DIR/logs/webapp.log"
    kill $API_PID 2>/dev/null
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}All services started successfully!${NC}"
echo "=========================================="
echo ""
echo "Learning Tools API:     http://localhost:5001"
echo "Learning Web App:       http://localhost:5000"
echo ""
echo "Log files:"
echo "  API:    $SCRIPT_DIR/logs/api.log"
echo "  WebApp: $SCRIPT_DIR/logs/webapp.log"
echo ""
echo "To view logs in real-time:"
echo "  tail -f $SCRIPT_DIR/logs/api.log"
echo "  tail -f $SCRIPT_DIR/logs/webapp.log"
echo ""
echo "Opening browser..."

# Try to open browser (different commands for different Linux distributions)
if command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:5000" 2>&1 &
elif command -v gnome-open &> /dev/null; then
    gnome-open "http://localhost:5000" 2>&1 &
elif command -v kde-open &> /dev/null; then
    kde-open "http://localhost:5000" 2>&1 &
else
    echo -e "${YELLOW}Could not automatically open browser.${NC}"
    echo "Please manually open: http://localhost:5000"
fi

echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services and exit${NC}"
echo ""

# Wait indefinitely (until Ctrl+C is pressed)
wait
