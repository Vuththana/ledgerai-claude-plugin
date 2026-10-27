# No dependency without a package request

**Don't add a new dependency until its package request is approved.** This covers every new line in the `dependencies` block of `build.gradle` (or in `gradle/libs.versions.toml`), every new Gradle plugin, and test-only dependencies. Spring Boot starters count too, even though their version comes from the Spring Boot BOM.

- Use the Gradle wrapper only (`./gradlew`). Never a locally installed `gradle`.
- Don't change the Spring Boot, Java or Gradle version without the team agreeing (they're settled in `docs/TRD.md` §2).
- Prefer what we already have (`build.gradle`), what Spring Boot already brings in, or the JDK, before reaching for a new library.
- Shared code for several services goes in `ledgervision-common`, not in a new third-party library.

When a new dependency seems necessary, **stop and draft a package request report** for the team instead of editing `build.gradle`. Post it in the team's agreed channel, or as a GitHub issue in this repo:

```markdown
### Package request: <group:artifact>

- **Repo:** <service-name>
- **Feature:** <the feature that needs it>
- **Package and version:** <group:artifact:version>, link to its page (Maven Central / project site)
- **Why we need it:** <what it does for this feature>
- **Alternatives considered:** <other libraries, Spring/JDK built-ins, or building it ourselves, and why not>
- **Size / impact:** <new transitive dependencies (`./gradlew dependencies`), startup or runtime changes>
- **Maintenance:** <licence, last release date, GitHub stars or usage>
```

Add it only after approval, and mention the approved request in the PR.
