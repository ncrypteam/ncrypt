#!/bin/bash
# Simple CLI to check if tests are passing locally and on GitHub

set -e

echo "🧪 ncrypt Test Checker"
echo "======================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check local tests
check_local() {
    echo "📍 Checking LOCAL tests..."
    echo ""
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Run tests
    if python -m pytest tests/ -v --tb=short; then
        echo ""
        echo -e "${GREEN}✅ All local tests PASSED!${NC}"
        return 0
    else
        echo ""
        echo -e "${RED}❌ Some local tests FAILED!${NC}"
        return 1
    fi
}

# Function to check GitHub Actions status
check_github() {
    echo ""
    echo "🐙 Checking GITHUB Actions status..."
    echo ""
    
    # Check if gh CLI is installed
    if ! command -v gh &> /dev/null; then
        echo -e "${YELLOW}⚠️  GitHub CLI (gh) not installed${NC}"
        echo "Install with: brew install gh"
        echo "Or check manually: https://github.com/$(git remote get-url origin | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/actions"
        return 1
    fi
    
    # Check latest workflow run
    latest_run=$(gh run list --workflow=tests.yml --limit 1 --json conclusion,status,headBranch,url)
    
    if [ -z "$latest_run" ] || [ "$latest_run" = "[]" ]; then
        echo -e "${YELLOW}⚠️  No GitHub Actions runs found${NC}"
        echo "Push your code to trigger the first run!"
        return 1
    fi
    
    # Parse the status
    status=$(echo $latest_run | jq -r '.[0].status')
    conclusion=$(echo $latest_run | jq -r '.[0].conclusion')
    branch=$(echo $latest_run | jq -r '.[0].headBranch')
    url=$(echo $latest_run | jq -r '.[0].url')
    
    echo "Branch: $branch"
    echo "Status: $status"
    echo "Result: $conclusion"
    echo "URL: $url"
    echo ""
    
    if [ "$conclusion" = "success" ]; then
        echo -e "${GREEN}✅ GitHub tests PASSED!${NC}"
        return 0
    elif [ "$conclusion" = "failure" ]; then
        echo -e "${RED}❌ GitHub tests FAILED!${NC}"
        echo "Check details: $url"
        return 1
    else
        echo -e "${YELLOW}⏳ GitHub tests still running...${NC}"
        return 1
    fi
}

# Main logic
case "${1:-both}" in
    local)
        check_local
        ;;
    github)
        check_github
        ;;
    both)
        local_result=0
        github_result=0
        
        check_local || local_result=$?
        check_github || github_result=$?
        
        echo ""
        echo "===================="
        echo "📊 SUMMARY"
        echo "===================="
        
        if [ $local_result -eq 0 ]; then
            echo -e "Local:  ${GREEN}✅ PASS${NC}"
        else
            echo -e "Local:  ${RED}❌ FAIL${NC}"
        fi
        
        if [ $github_result -eq 0 ]; then
            echo -e "GitHub: ${GREEN}✅ PASS${NC}"
        else
            echo -e "GitHub: ${YELLOW}⚠️  CHECK MANUALLY${NC}"
        fi
        
        exit $local_result
        ;;
    watch)
        echo "👀 Watching GitHub Actions..."
        gh run watch
        ;;
    *)
        echo "Usage: $0 [local|github|both|watch]"
        echo ""
        echo "  local  - Run tests locally only"
        echo "  github - Check GitHub Actions status only"
        echo "  both   - Check both (default)"
        echo "  watch  - Watch live GitHub Actions run"
        exit 1
        ;;
esac

