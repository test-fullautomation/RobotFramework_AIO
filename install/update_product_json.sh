#!/usr/bin/env bash
set -e

# Default: $RobotVsCode/resources/app/product.json
PRODUCT_JSON_PATH="${1:-$RobotVsCode/resources/app/product.json}"

if [ -z "$RobotVsCode" ]; then
  echo "RobotVsCode environment variable is not set, skipping product.json update"
  exit 0
fi

if [ ! -f "$PRODUCT_JSON_PATH" ]; then
  echo "product.json not found: $PRODUCT_JSON_PATH"
  exit 0
fi

# Check jq exists
if ! command -v jq >/dev/null 2>&1; then
  echo "jq not found, skipping product.json update"
  exit 0
fi

tmp_file="$(mktemp)"

jq '
  if .extensionEnabledApiProposals["GitHub.copilot"] then
    .extensionEnabledApiProposals["GitHub.copilot"] = [
      "inlineCompletionsAdditions",
      "interactive",
      "interactiveUserActions",
      "terminalDataWriteEvent"
    ]
    |
    .extensionEnabledApiProposals["GitHub.copilot-nightly"] = [
      "inlineCompletionsAdditions",
      "interactive",
      "interactiveUserActions",
      "terminalDataWriteEvent"
    ]
  else
    .
  end
' "$PRODUCT_JSON_PATH" > "$tmp_file"

mv "$tmp_file" "$PRODUCT_JSON_PATH"

echo "Updated GitHub Copilot proposals in $PRODUCT_JSON_PATH"
