# API_PATTERNS.md

## Purpose
Defines backend integration and API interaction standards for this project.
Prevents inconsistent implementations and reduces token waste from repeated pattern discovery.

---

## Core Principle
Every pattern defined here is the standard. Claude Code must follow these — not invent alternatives.
If a new pattern is needed, propose it before implementing it.

---

## Fill This Section for Your Project

### Base Configuration
<!-- Base URL handling, environment-based config, default headers, content type -->

### Authentication and Session Handling
<!-- How auth tokens are attached to requests, refreshed, and stored securely -->

### Request Conventions
<!-- Standard request structure, parameter naming, query vs body conventions -->

### Response Handling
<!-- Standard response shape, how data is normalised before use in the app -->

### Error Handling
<!-- Standard error response shape, error codes, how errors surface to the UI -->
<!-- User-facing error messages vs internal logging -->

### Retry Logic
<!-- Which calls retry automatically, retry count, backoff strategy -->

### Async and Loading State Handling
<!-- Async/await conventions, how loading states are managed, cancellation -->

### Pagination
<!-- Cursor-based vs offset, how pages are fetched and appended to lists -->

### Caching
<!-- What is cached, cache invalidation strategy, TTL rules -->

### Validation
<!-- Where validation happens (client vs server), library used, required vs optional fields -->

### Naming Conventions
<!-- API function naming, service file naming, endpoint constant naming -->

### Third-Party Integrations
<!-- List each integration and its pattern e.g. Supabase, Stripe, AI APIs -->

### AI API Integration (if applicable)
<!-- How AI API calls are structured, prompt management, context window conventions -->
<!-- Streaming response handling, fallback states -->

### Security Considerations
<!-- API key storage, sensitive data handling, what never goes in requests -->

### Environment Configuration
<!-- How dev, staging, prod environments are configured and switched -->

---

## AI Agent Guidance
- Reuse existing API abstractions — do not create parallel implementations
- Maintain consistent error handling across all integrations
- Avoid duplicating integration logic
- Follow async conventions defined above
- Never hardcode API keys, tokens, or credentials
- If a new integration is needed, propose the pattern before implementing
