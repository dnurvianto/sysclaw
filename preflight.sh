#!/usr/bin/env bash
# ==============================================================================
# SysClaw - Pre-Flight Diagnostic Check
# Validates environment and server readiness before deployment.
# ==============================================================================

set -e

GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
NC="\033[0m"

echo -e "${BLUE}=====================================================${NC}"
echo -e "${BLUE} 🐾 SysClaw Pre-Flight Diagnostic Check${NC}"
echo -e "${BLUE}=====================================================${NC}"

ERRORS=0

# 1. Check Python 3 Runtime
echo -n "[1/6] Checking Python 3 runtime... "
if command -v python3 &>/dev/null; then
    PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PY_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
    PY_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')
    
    if [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -ge 8 ]; then
        echo -e "${GREEN}OK (v${PY_VER})${NC}"
    else
        echo -e "${RED}FAILED (Requires Python 3.8+, detected v${PY_VER})${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${RED}FAILED (python3 executable not found)${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 2. Check Outbound Connection to Telegram API
echo -n "[2/6] Checking outbound connection to Telegram API... "
if curl -s --connect-timeout 5 https://api.telegram.org >/dev/null 2>&1; then
    echo -e "${GREEN}OK (Port 443 Reachable)${NC}"
else
    echo -e "${RED}FAILED (Unable to reach api.telegram.org:443)${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 3. Check Outbound Connection to DeepSeek API
echo -n "[3/6] Checking outbound connection to DeepSeek API... "
if curl -s --connect-timeout 5 https://api.deepseek.com >/dev/null 2>&1; then
    echo -e "${GREEN}OK (Port 443 Reachable)${NC}"
else
    echo -e "${YELLOW}WARNING (Unable to reach api.deepseek.com:443 - AI features may be unavailable)${NC}"
fi

# 4. Check Free Memory
echo -n "[4/6] Checking available RAM memory... "
if [ -f /proc/meminfo ]; then
    FREE_MEM_KB=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
    FREE_MEM_MB=$((FREE_MEM_KB / 1024))
    if [ "$FREE_MEM_MB" -ge 100 ]; then
        echo -e "${GREEN}OK (${FREE_MEM_MB} MB Available)${NC}"
    else
        echo -e "${YELLOW}WARNING (Only ${FREE_MEM_MB} MB available - Configure swap space if needed)${NC}"
    fi
else
    echo -e "${GREEN}OK${NC}"
fi

# 5. Check Systemd Service Unit Availability
echo -n "[5/6] Checking systemd service unit name 'sysclaw'... "
if command -v systemctl &>/dev/null; then
    if systemctl list-unit-files | grep -qw "sysclaw.service"; then
        echo -e "${YELLOW}EXISTS (sysclaw.service is already installed - will be updated upon reload)${NC}"
    else
        echo -e "${GREEN}OK (Service unit name is clean and available)${NC}"
    fi
else
    echo -e "${YELLOW}SKIPPED (systemctl is not available in this environment)${NC}"
fi

# 6. Check .env Configuration File
echo -n "[6/6] Checking .env configuration file... "
if [ -f ".env" ]; then
    echo -e "${GREEN}OK (.env detected)${NC}"
else
    echo -e "${YELLOW}MISSING (Please copy .env.example to .env and configure credentials)${NC}"
fi

echo -e "${BLUE}=====================================================${NC}"
if [ "$ERRORS" -eq 0 ]; then
    echo -e "${GREEN}🎉 RESULT: Server is 100% READY for SysClaw deployment!${NC}"
    echo -e "Next steps:"
    echo -e " 1. cp .env.example .env && nano .env"
    echo -e " 2. python3 bot.py"
else
    echo -e "${RED}❌ RESULT: Encountered $ERRORS blocking issue(s). Please resolve them before running SysClaw.${NC}"
    exit 1
fi
