# 🧠 Casablanca Insight — Cursor Project Rules & Guardrails

These rules are designed to maximize AI-assisted development while keeping the project production-ready. Cursor, Codex, and ChatGPT are encouraged to handle as much scaffolding and boilerplate as possible, allowing for creative, fast, vibe-driven development.

---

## 1. ✨ Coding Philosophy

- **Let Cursor write first.** You review and refine.
- **Prompt clearly**: define inputs, expected outputs, edge cases, and format.
- **Stay in flow**: use Cursor inline with file-specific prompts.

---

## 2. 🛠️ File & Code Generation Rules

- Always generate:
  - `*.test.ts` or `*.test.tsx` files alongside logic-heavy components or utilities.
  - `zod` validation schemas or TypeScript interfaces for all external or unstructured data.
- Scraping/ETL scripts must include:
  - Logging of source URLs
  - Timestamp of data ingestion
  - Retry logic and exception handling

---

## 3. 💬 Prompt Guidelines

Use inline prompts in the following format:
```ts
// Cursor Prompt:
// Generate a Next.js API route that returns the top 5 movers from today’s market data,
// including company name, ticker, % change, and sector.
