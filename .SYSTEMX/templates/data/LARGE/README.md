# LARGE — local DATA

Large local datasets, compressed archives, and binaries. Keep version/provenance references in scoped records when useful; avoid committing payload.

Payload is ignored by the supplied Git rules. Only this exact README is scaffold;
README files in nested payload folders remain ignored. Run `data audit` to check
effective Git rules and already tracked files. Ignored does not mean secret.
