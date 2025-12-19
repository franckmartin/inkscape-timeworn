#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR"/timeworn.* ~/snap/inkscape/common/extensions/
echo "Files synced to Inkscape extensions"
