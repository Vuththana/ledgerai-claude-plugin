#!/usr/bin/env bash
# PostToolUse (Write|Edit): run ESLint --fix on the edited JS/TS file.
# Does nothing in repos without a local ESLint install, so it is safe in every repo.

f=$(jq -r '.tool_response.filePath // .tool_input.file_path // empty')

case "$f" in
  *.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs) ;;
  *) exit 0 ;;
esac

cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
[ -x node_modules/.bin/eslint ] || exit 0

node_modules/.bin/eslint --fix "$f" >/dev/null 2>&1 || true
exit 0
