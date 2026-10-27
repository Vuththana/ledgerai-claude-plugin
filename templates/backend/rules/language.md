# Language: English now, Khmer later

- **The product is English only for now.** Every error message, email and notification text is in English.
- **Khmer is coming later.** `users.language` already has `Khmer` and `English` (default `English`), but only English can be selected until Khmer ships (see `docs/flow/profile-and-business.md`).
- **Get ready for it now:**
  - Put every user-facing string (error `message`, email subject and body, notification text) in `src/main/resources/messages.properties`, looked up by key through `MessageSource`. Never hard-code them in Java.
  - Write whole sentences with placeholders (`{0}`), not fragments joined together.
  - Error `code` values are stable English identifiers (`EMAIL_ALREADY_REGISTERED`) and are never translated. Only `message` is.
- Code, comments, log messages, commit messages and PRs are in English.
