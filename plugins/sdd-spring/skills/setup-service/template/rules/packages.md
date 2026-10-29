# Dependencies

Package requests are for `web-ui` only (`docs/TEAM-RULES.md` §7, since docs v3.1.0). This repo adds the dependencies a feature needs without one.

- Use the Gradle wrapper only (`./gradlew`). Never a locally installed `gradle`.
- Don't change the Spring Boot, Java or Gradle version without the team agreeing (they're settled in `docs/TRD.md` §2).
- Prefer what we already have (`build.gradle`), what Spring Boot already brings in, or the JDK, before reaching for a new library. Let the Spring Boot or Spring Cloud BOM manage versions where it can.
- Add only what the current feature needs, and list new dependencies in the PR description.
- Shared code for several services goes in `ledgervision-common`, not in a new third-party library.
