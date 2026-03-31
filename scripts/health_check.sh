#!/bin/bash
set -euo pipefail

HOST="${HOST:-localhost}"
PORT="${PORT:-5000}"
MAX_RETRIES="${MAX_RETRIES:-5}"
RETRY_DELAY="${RETRY_DELAY:-3}"
BASE_URL="http://${HOST}:${PORT}"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { echo -e "${GREEN}✅ PASS${NC} — $1"; }
fail() { echo -e "${RED}❌ FAIL${NC} — $1"; }
warn() { echo -e "${YELLOW}⚠️  WARN${NC} — $1"; }

check_endpoint() {
  local endpoint="$1"
  local expected_key="$2"
  local url="${BASE_URL}${endpoint}"

  for attempt in $(seq 1 $MAX_RETRIES); do
    echo "  Checking ${url} (attempt ${attempt}/${MAX_RETRIES})..."
    HTTP_CODE=$(curl -s -o /tmp/response_body.json -w "%{http_code}" --max-time 5 "$url" 2>/dev/null || echo "000")

    if [ "$HTTP_CODE" = "200" ]; then
      if [ -n "$expected_key" ]; then
        VALUE=$(python3 -c "
import json
try:
    data = json.load(open('/tmp/response_body.json'))
    print(data.get('${expected_key}', 'KEY_MISSING'))
except:
    print('PARSE_ERROR')
" 2>/dev/null)
        if [ "$VALUE" = "KEY_MISSING" ] || [ "$VALUE" = "PARSE_ERROR" ]; then
          fail "Endpoint ${endpoint} missing key '${expected_key}'"
          return 1
        fi
        pass "Endpoint ${endpoint} → ${expected_key}=${VALUE}"
      else
        pass "Endpoint ${endpoint} → HTTP 200"
      fi
      return 0
    fi

    warn "Got HTTP ${HTTP_CODE}, retrying in ${RETRY_DELAY}s..."
    sleep "$RETRY_DELAY"
  done

  fail "Endpoint ${endpoint} unreachable after ${MAX_RETRIES} attempts"
  return 1
}

echo ""
echo "═══════════════════════════════════════════"
echo "   🩺 Self-Healing App — Health Check"
echo "═══════════════════════════════════════════"
echo ""

FAILED=0
check_endpoint "/" "status"       || FAILED=$((FAILED + 1))
check_endpoint "/health" "status" || FAILED=$((FAILED + 1))
check_endpoint "/info" "version"  || FAILED=$((FAILED + 1))

echo ""
echo "═══════════════════════════════════════════"
if [ "$FAILED" -eq 0 ]; then
  echo -e "${GREEN}✅ All health checks passed!${NC}"
  exit 0
else
  echo -e "${RED}❌ ${FAILED} check(s) failed.${NC}"
  exit 1
fi
