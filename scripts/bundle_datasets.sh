#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Magean Research
#
# Bundle ATLASKnO datasets for release distribution.
#
# Creates:
#   - atlaskno-data-vX.Y.Z.tar.gz  (tarball of data/ + schedules/ + shapes/)
#   - atlaskno-data-vX.Y.Z.zip     (zip archive of the same)
#   - SHA256SUMS                    (checksums for all release artifacts)
#
# Usage:
#   ./scripts/bundle_datasets.sh <version-tag> <output-dir>
#   ./scripts/bundle_datasets.sh v0.1.0 dist/
#
set -euo pipefail

VERSION="${1:?Usage: $0 <version-tag> <output-dir>}"
OUTDIR="${2:?Usage: $0 <version-tag> <output-dir>}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Strip leading 'v' for archive naming
VERSION_CLEAN="${VERSION#v}"
ARCHIVE_BASE="atlaskno-data-${VERSION_CLEAN}"

# Create output directory
mkdir -p "${OUTDIR}"

# Collect data directories that exist
DATA_DIRS=()
for dir in data schedules shapes; do
    if [ -d "${REPO_ROOT}/${dir}" ]; then
        DATA_DIRS+=("${dir}")
    fi
done

if [ ${#DATA_DIRS[@]} -eq 0 ]; then
    echo "⚠️  No data directories found (data/, schedules/, shapes/) — skipping bundle."
    exit 0
fi

echo "📦 Bundling ATLASKnO datasets ${VERSION}..."
echo "   Directories: ${DATA_DIRS[*]}"

# Create a temporary staging directory
STAGING=$(mktemp -d)
trap 'rm -rf "${STAGING}"' EXIT

# Copy data into staging under a named directory
STAGE_DIR="${STAGING}/${ARCHIVE_BASE}"
mkdir -p "${STAGE_DIR}"

for dir in "${DATA_DIRS[@]}"; do
    cp -r "${REPO_ROOT}/${dir}" "${STAGE_DIR}/${dir}"
done

# Include LICENSE.md for attribution compliance
if [ -f "${REPO_ROOT}/LICENSE.md" ]; then
    cp "${REPO_ROOT}/LICENSE.md" "${STAGE_DIR}/LICENSE.md"
fi

# Create tarball
TARBALL="${OUTDIR}/${ARCHIVE_BASE}.tar.gz"
tar -czf "${TARBALL}" -C "${STAGING}" "${ARCHIVE_BASE}"
echo "   ✅ Created: ${TARBALL}"

# Create zip
ZIPFILE="${OUTDIR}/${ARCHIVE_BASE}.zip"
(cd "${STAGING}" && zip -rq "${ZIPFILE}" "${ARCHIVE_BASE}")
echo "   ✅ Created: ${ZIPFILE}"

# Generate SHA256 checksums for all artifacts in output directory
echo "🔒 Generating checksums..."
CHECKSUMS="${OUTDIR}/SHA256SUMS"
(cd "${OUTDIR}" && sha256sum *.tar.gz *.zip *.whl *.tar.gz 2>/dev/null | sort -u > SHA256SUMS) || true

# Also checksum individual files explicitly to be safe
(cd "${OUTDIR}" && sha256sum "${ARCHIVE_BASE}.tar.gz" "${ARCHIVE_BASE}.zip" > SHA256SUMS)
echo "   ✅ Created: ${CHECKSUMS}"

echo ""
echo "📦 Dataset bundle complete!"
ls -lh "${OUTDIR}"
