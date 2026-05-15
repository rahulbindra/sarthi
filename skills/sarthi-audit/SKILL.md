---
name: sarthi-audit
description: Run weekly multi-domain audits across security, privacy, vulnerability, engineering, fair attribution, usability, legal, ethical hacking, and keys/PII. Dispatches parallel sub-agents per domain and produces a scored report.
argument-hint: "[optional: security|privacy|vulnerability|engineering|attribution|usability|legal|hacker|keys — runs all if omitted]"
---

# Sarthi Audit

Runs up to 9 parallel audit agents across your codebase — one per domain. Each agent scores its domain pass/warn/fail and returns findings. Results are aggregated into a single report.

After the audit completes, the weekly clock resets:
```bash
touch ~/.claude/.sarthi-audit-ts
```

---

## Step 1 — Determine scope

If the user passed a specific domain argument, run only that domain. Otherwise run all 9.

Domains: `security`, `privacy`, `vulnerability`, `engineering`, `attribution`, `usability`, `legal`, `hacker`, `keys`

---

## Step 2 — Dispatch parallel sub-agents

Launch one sub-agent per domain in parallel. Each agent must:
1. Scan the codebase for issues in its domain
2. Return a structured result: `{ domain, status: pass|warn|fail, findings: [...] }`
3. Keep findings actionable — file path + line number + description where possible

Use `subagent_type: "compound-engineering:ce-correctness-reviewer"` for engineering. Use `subagent_type: "Explore"` for all others.

---

### Agent 1 — Security

Audit for OWASP Top 10 and common security weaknesses:
- SQL injection, XSS, CSRF, command injection, path traversal
- Insecure deserialization, broken auth, missing rate limiting
- Unsafe use of eval, exec, or shell commands
- Missing input validation at system boundaries (API endpoints, user input handlers)
- Hardcoded credentials (also caught by Agent 9, flag here too)
- Insecure direct object references
- Missing HTTPS enforcement, insecure cookies, missing security headers

If `security-guidance` plugin is installed, note its findings alongside this agent's output.

---

### Agent 2 — Privacy

Audit for privacy risks:
- PII collected but not disclosed (name, email, phone, location, device ID, IP)
- Data retained longer than necessary — look for logs, analytics, or DB writes of user data without TTL
- Third-party SDKs that may exfiltrate data (analytics, crash reporters, ad SDKs)
- Missing consent flows before data collection
- User data passed to external APIs without anonymisation
- GDPR/CCPA gaps: no deletion mechanism, no data export, no opt-out
- Sensitive fields not encrypted at rest or in transit

---

### Agent 3 — Vulnerability

Audit for known vulnerabilities:
- Run dependency check:
  ```bash
  # Node
  npm audit --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"{d.get('metadata',{}).get('vulnerabilities',{})}\")  " 2>/dev/null || true
  # Python
  pip-audit 2>/dev/null | head -40 || safety check 2>/dev/null | head -40 || true
  # Ruby
  bundle audit 2>/dev/null | head -40 || true
  ```
- Flag any critical or high severity CVEs
- Outdated packages more than 2 major versions behind
- Deprecated APIs or functions with known security implications
- Transitive dependency risks (deep dependency chains with known vulns)

---

### Agent 4 — Engineering

Audit for engineering quality:
- Logic errors, off-by-one, null dereference, unchecked returns
- Missing error handling at system boundaries
- God objects, circular dependencies, deeply nested conditionals
- N+1 query patterns, missing indexes, unbounded queries
- Race conditions in async code
- Dead code, unused imports, stale feature flags
- Test coverage gaps on critical paths

Route to `/ce-code-review` if compound-engineering is installed, and include its output.

---

### Agent 5 — Fair Attribution

Audit for attribution and licensing compliance:
- Scan for open source code copied without attribution:
  ```bash
  grep -rn "stackoverflow\|copied from\|taken from\|ported from\|based on" . --include="*.js" --include="*.ts" --include="*.py" --include="*.rb" --include="*.go" --include="*.swift" 2>/dev/null | grep -v ".git" | head -30
  ```
- Check LICENSE file exists and matches dependencies' license requirements
- Flag GPL/AGPL dependencies in commercial projects (license incompatibility)
- Missing copyright headers in files
- AI-generated code used in contexts that require human authorship disclosure
- Third-party assets (fonts, icons, images) without license verification

---

### Agent 6 — Usability

Audit for usability and accessibility:
- Missing ARIA labels, roles, and landmark regions in UI code
- Non-descriptive button/link text ("click here", "submit")
- No keyboard navigation support (missing tabIndex, onKeyDown handlers)
- Missing alt text on images
- Colour contrast issues (flag hardcoded low-contrast colour pairs)
- Error messages that expose technical details to end users
- Forms with no validation feedback
- Missing loading/empty/error states in UI components
- Inconsistent terminology across the UI

---

### Agent 7 — Legal

Audit for legal risks:
- License file present and OSI-approved
- GPL/AGPL/LGPL dependencies in proprietary code (copyleft contamination)
- DMCA risks: third-party assets without clear license
- Missing privacy policy link if app collects user data
- Terms of service violations for third-party APIs (check comments/docs for API usage notes)
- Export control: cryptography libraries that may require export compliance (OpenSSL, libsodium)
- Trademark risks: use of third-party brand names in UI strings or domain references

---

### Agent 8 — Ethical Hacker (Injection & Extraction)

Audit from an attacker's perspective — look for vectors an ethical hacker would exploit:

**Injection vectors:**
- Unsanitised user input flowing into: SQL queries, shell commands, LDAP queries, XML parsers, template engines, eval/exec
- Server-side template injection (SSTI) — user input rendered in templates
- HTTP header injection — user-controlled values in response headers
- Log injection — user input written directly to logs without sanitisation
- Deserialization of untrusted data (pickle, YAML.load, JSON with reviver)
- XXE — XML parsers with external entity resolution enabled

**Information extraction vectors:**
- Verbose error messages exposing stack traces, DB schema, internal paths to end users
- Debug endpoints or admin routes without auth (e.g., `/debug`, `/admin`, `/metrics`, `/__health` exposed publicly)
- Timing attacks — variable-time comparisons for secrets or auth tokens
- Overly permissive CORS (`Access-Control-Allow-Origin: *` on authenticated endpoints)
- GraphQL introspection enabled in production
- Directory listing enabled on static file servers
- Insecure direct object references exposing other users' data
- API responses returning more fields than the client requested (over-fetching sensitive fields)

---

### Agent 9 — Keys & PII in Code

Scan for hardcoded secrets and PII — this agent runs grep patterns, not LLM reasoning:

```bash
# Hardcoded keys and tokens
grep -rn \
  -e "sk-ant-" \
  -e "sk-[a-zA-Z0-9]\{40\}" \
  -e "AKIA[0-9A-Z]\{16\}" \
  -e "ghp_[a-zA-Z0-9]\{36\}" \
  -e "gho_[a-zA-Z0-9]\{36\}" \
  -e "xoxb-\|xoxp-\|xoxa-" \
  -e "AIza[0-9A-Za-z_-]\{35\}" \
  -e "ya29\." \
  -e "-----BEGIN.*PRIVATE KEY-----" \
  -e "-----BEGIN RSA PRIVATE KEY-----" \
  -e "password\s*=\s*['\"][^'\"]\{4,\}['\"]" \
  -e "secret\s*=\s*['\"][^'\"]\{4,\}['\"]" \
  -e "api_key\s*=\s*['\"][^'\"]\{4,\}['\"]" \
  -e "token\s*=\s*['\"][^'\"]\{4,\}['\"]" \
  . --include="*.js" --include="*.ts" --include="*.py" --include="*.rb" \
    --include="*.go" --include="*.swift" --include="*.env" --include="*.json" \
    --include="*.yaml" --include="*.yml" --include="*.toml" --include="*.sh" \
    2>/dev/null | grep -v ".git" | grep -v "node_modules" | grep -v "test\|spec\|mock\|fixture" | head -50

# PII patterns
grep -rn \
  -e "[a-zA-Z0-9._%+-]\+@[a-zA-Z0-9.-]\+\.[a-zA-Z]\{2,\}" \
  -e "\b[0-9]\{3\}-[0-9]\{2\}-[0-9]\{4\}\b" \
  -e "\b[0-9]\{4\}[[:space:]-]\?[0-9]\{4\}[[:space:]-]\?[0-9]\{4\}[[:space:]-]\?[0-9]\{4\}\b" \
  . --include="*.js" --include="*.ts" --include="*.py" --include="*.rb" \
    --include="*.go" --include="*.swift" 2>/dev/null \
  | grep -v ".git" | grep -v "node_modules" | grep -v "test\|spec\|mock\|fixture\|example\|placeholder" | head -30
```

Flag every match with file path and line number. Also check:
- `.env` files committed to git: `git ls-files | grep -E "^\.env"`
- Secrets in git history: `git log --all --oneline -p | grep -E "sk-|password|secret|token" | head -20`
- `~/.gitignore` or `.gitignore` missing `.env` entry

---

## Step 3 — Aggregate results

After all agents return, compile the report:

```
Sarthi Audit Report — <date>
─────────────────────────────────────────────────────

  Security        ✓ pass   — no critical issues found
  Privacy         ⚠ warn   — 2 findings
  Vulnerability   ✗ fail   — 1 critical CVE (lodash@4.17.15)
  Engineering     ⚠ warn   — 3 findings
  Attribution     ✓ pass
  Usability       ⚠ warn   — 4 findings
  Legal           ✓ pass
  Ethical Hacker  ✗ fail   — GraphQL introspection enabled in prod
  Keys & PII      ✗ fail   — 2 hardcoded secrets found

─────────────────────────────────────────────────────
3 fail  ·  3 warn  ·  3 pass

Findings requiring immediate action:
  [Vulnerability] lodash@4.17.15 — CVE-2021-23337 (prototype pollution, critical)
    → npm install lodash@latest
  [Ethical Hacker] GraphQL introspection enabled — src/graphql/server.ts:42
    → Set introspection: process.env.NODE_ENV !== 'production'
  [Keys & PII] Hardcoded API key — src/services/stripe.ts:8
    → Move to environment variable, rotate the key immediately
```

Status rules:
- `✗ fail` — critical finding requiring immediate action
- `⚠ warn` — non-critical finding worth addressing
- `✓ pass` — no significant issues found

---

## Step 4 — Reset the weekly clock

```bash
touch ~/.claude/.sarthi-audit-ts
```

Confirm to the user: "Audit complete. Next audit due in 7 days."
