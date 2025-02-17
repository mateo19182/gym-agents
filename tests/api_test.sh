#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Base URL for the API
API_URL="http://localhost:8000"

# Counter for tests
PASSED=0
FAILED=0

# Function to print test results
print_result() {
    local test_name=$1
    local result=$2
    local expected=$3
    local actual=$4
    
    if [ $result -eq 0 ]; then
        echo -e "${GREEN}✓ $test_name passed${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗ $test_name failed${NC}"
        echo -e "${RED}Expected: $expected${NC}"
        echo -e "${RED}Got: $actual${NC}"
        FAILED=$((FAILED + 1))
    fi
    echo "------------------------"
}

echo "Starting API Tests..."
echo "------------------------"

# Test 1: Root endpoint
echo "Testing root endpoint (GET /)..."
response=$(curl -s $API_URL/)
expected='"message":"Welcome to the Gym Agent API'

if echo $response | grep -q "$expected"; then
    print_result "Root endpoint" 0 "$expected" "$response"
else
    print_result "Root endpoint" 1 "$expected" "$response"
fi

# Print summary
echo "Test Summary:"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

# Exit with failure if any tests failed
if [ $FAILED -gt 0 ]; then
    exit 1
else
    exit 0
fi 