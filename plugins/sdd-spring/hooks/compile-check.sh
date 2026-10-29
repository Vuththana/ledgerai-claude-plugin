#!/usr/bin/env bash
# PostToolUse (Write|Edit): compile the Gradle project after a Java file changes,
# and hand compiler errors back to Claude (exit 2 → stderr is shown to Claude).
# Does nothing outside a Gradle repo with a wrapper, so it is safe in every repo.

f=$(jq -r '.tool_response.filePath // .tool_input.file_path // empty')

case "$f" in
  *.java) ;;
  *) exit 0 ;;
esac

cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
[ -x ./gradlew ] || exit 0
[ -f build.gradle ] || [ -f build.gradle.kts ] || exit 0

case "$f" in
  */src/test/*) task=compileTestJava ;;
  *) task=compileJava ;;
esac

out=$(./gradlew "$task" -q --console=plain 2>&1)
[ $? -eq 0 ] && exit 0

{
  echo "./gradlew $task failed after editing $f:"
  if echo "$out" | grep -q 'error:'; then
    echo "$out" | grep -A3 '^/.*error:' | grep -v '^--$' | head -60   # javac errors (first copy only) with their source line
  else
    echo "$out" | head -20                          # Gradle failure (config, toolchain, dependencies)
  fi
  echo "If an error points to a file you haven't written yet, carry on and it will clear."
} >&2
exit 2
