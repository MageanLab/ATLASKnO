#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Magean Research
#
# Verify dual-license compliance across the ATLASKnO repository.
#
# Checks:
#   1. LICENSE.md exists and contains both CC BY-SA 3.0 and MIT sections
#   2. Python/TS/JS source files contain SPDX license headers
#   3. No proprietary license markers (GPL, AGPL, SSPL, BSL) are introduced
#
# Exit codes:
#   0 — all checks passed
#   1 — one or more compliance violations found
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ERRORS=0

echo "📜 ATLASKnO License Compliance Check"
echo "======================================"
echo ""

# ── Check 1: LICENSE.md exists and has required sections ───────────────
echo "🔍 Check 1: LICENSE.md integrity"

LICENSE_FILE="${REPO_ROOT}/LICENSE.md"
if [ ! -f "${LICENSE_FILE}" ]; then
    echo "   ❌ LICENSE.md not found at repo root!"
    ERRORS=$((ERRORS + 1))
else
    # Check for CC BY-SA 3.0 section
    if grep -qi "CC BY-SA 3.0\|Creative Commons Attribution-ShareAlike 3.0" "${LICENSE_FILE}"; then
        echo "   ✅ CC BY-SA 3.0 data license section found"
    else
        echo "   ❌ Missing CC BY-SA 3.0 data license section"
        ERRORS=$((ERRORS + 1))
    fi

    # Check for MIT section
    if grep -qi "MIT License\|Permission is hereby granted" "${LICENSE_FILE}"; then
        echo "   ✅ MIT software license section found"
    else
        echo "   ❌ Missing MIT software license section"
        ERRORS=$((ERRORS + 1))
    fi

    # Check for UDC Consortium attribution
    if grep -qi "UDC Consortium" "${LICENSE_FILE}"; then
        echo "   ✅ UDC Consortium attribution present"
    else
        echo "   ⚠️  UDC Consortium attribution may be missing"
    fi
fi

echo ""

# ── Check 2: SPDX headers in source files ─────────────────────────────
echo "🔍 Check 2: SPDX license headers in source files"

MISSING_HEADERS=()
SOURCE_EXTENSIONS=("py" "ts" "js" "tsx" "jsx")

for ext in "${SOURCE_EXTENSIONS[@]}"; do
    while IFS= read -r -d '' file; do
        # Skip node_modules, .git, __pycache__, virtual envs
        if [[ "${file}" == *"node_modules"* ]] || \
           [[ "${file}" == *".git/"* ]] || \
           [[ "${file}" == *"__pycache__"* ]] || \
           [[ "${file}" == *".venv"* ]] || \
           [[ "${file}" == *"venv/"* ]]; then
            continue
        fi

        # Check for SPDX identifier in the first 10 lines
        if ! head -n 10 "${file}" | grep -qi "SPDX-License-Identifier"; then
            rel_path="${file#${REPO_ROOT}/}"
            MISSING_HEADERS+=("${rel_path}")
        fi
    done < <(find "${REPO_ROOT}" -name "*.${ext}" -type f -print0 2>/dev/null)
done

if [ ${#MISSING_HEADERS[@]} -eq 0 ]; then
    echo "   ✅ All source files have SPDX license headers (or no source files found)"
else
    echo "   ⚠️  ${#MISSING_HEADERS[@]} file(s) missing SPDX-License-Identifier header:"
    for f in "${MISSING_HEADERS[@]}"; do
        echo "      • ${f}"
    done
    # Warning only — don't fail CI for missing headers during early development
    # Uncomment the next line to enforce strictly:
    # ERRORS=$((ERRORS + ${#MISSING_HEADERS[@]}))
fi

echo ""

# ── Check 3: No proprietary license markers ───────────────────────────
echo "🔍 Check 3: Scanning for proprietary license introductions"

PROPRIETARY_PATTERNS=(
    "GNU General Public License"
    "AGPL"
    "Server Side Public License"
    "SSPL"
    "Business Source License"
    "BSL-1.1"
    "Elastic License"
    "Commons Clause"
)

FOUND_PROPRIETARY=0
for pattern in "${PROPRIETARY_PATTERNS[@]}"; do
    # Search in all text files, excluding LICENSE.md itself (may have comparison text),
    # .git, node_modules, etc.
    matches=$(grep -rl --include="*.md" --include="*.txt" --include="*.toml" \
              --include="*.cfg" --include="*.yaml" --include="*.yml" \
              "${pattern}" "${REPO_ROOT}" 2>/dev/null \
              | grep -v "\.git/" \
              | grep -v "LICENSE.md" \
              | grep -v "node_modules" \
              | grep -v "SETUP_GUIDE.md" \
              || true)

    if [ -n "${matches}" ]; then
        echo "   ❌ Found proprietary license marker '${pattern}' in:"
        echo "${matches}" | while IFS= read -r m; do
            echo "      • ${m#${REPO_ROOT}/}"
        done
        FOUND_PROPRIETARY=1
    fi
done

if [ "${FOUND_PROPRIETARY}" -eq 0 ]; then
    echo "   ✅ No proprietary license markers detected"
else
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "======================================"

if [ "${ERRORS}" -gt 0 ]; then
    echo "❌ License compliance check FAILED with ${ERRORS} error(s)"
    exit 1
fi

echo "✅ All license compliance checks passed!"
exit 0
