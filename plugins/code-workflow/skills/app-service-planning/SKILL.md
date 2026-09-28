---
name: app-service-planning
description: "Turn an app or service idea into a focused product brief, MVP scope, and implementation-ready development plan. Use for product discovery, PRD drafting, or deciding the scope of a new product or existing-product extension. Do not select for ordinary code changes, bug fixes, generic task breakdowns, architecture-only analysis, or implementation of an approved plan."
---

# App & Service Planning

Help a solo developer decide who a product serves, what problem it solves, and
what is worth building first. Finish with a development plan another coding
agent can use without reconstructing the conversation. Support Codex and Claude
Code equally; no particular agent, connector, or MCP server is required.

Respond in the same language the user writes in. Detect the user's language
from the current conversation; retain technical identifiers as written.

## Choose the entry point

Infer new-product versus existing-product mode and the current planning stage
from the request and context. State a reasonable starting point and proceed;
do not ask the user to reconfirm information already provided.

- A new idea: identify the target user, problem, present workaround, and proposed
  value. Establish constraints before suggesting a stack.
- An existing product extension: read [existing-project guidance](shared/references/existing-project.md)
  first. Reuse verified analysis and inspect only the relevant code paths.
- An existing product brief or PRD: preserve its decisions and fill only gaps
  that affect scope or acceptance. Go directly to handoff if those are settled.
- A request only to code, fix a bug, review, or break down a specified engineering
  change belongs to native development workflows. A repository path alone does
  not make that request product planning.

## Develop the product decision

Read [product discovery](shared/references/product-discovery.md) when the problem,
MVP, or user journey is unsettled. Work through only the unresolved decisions:

1. Target user, problem, value, and a concrete success signal.
2. Core user journey and observable acceptance criteria.
3. MVP, later work, and explicit exclusions with reasons.
4. Material assumptions, constraints, and the cheapest useful validation.

Ask one or two high-impact questions at a time when missing information changes
the product decision. Continue independent work while awaiting answers when the
host allows it. Label reversible assumptions; never treat silence as approval
for a material decision. Avoid turning every stage into an approval gate.

Use the smallest scope that tests the value proposition. Do not automatically
add accounts, billing, cloud sync, analytics, or administration. Add optional UX
states only when they affect the core journey. Honor an explicit narrower
request (such as a PRD only) instead of forcing a full development plan.

## Produce the handoff

Read [handoff guidance](shared/references/handoff.md) to select a single plan or
roadmap with vertical phases. When the working directory is the target
project's repository, save Markdown in its existing planning location,
defaulting to `docs/plans/`; use a feature-specific filename and preserve
unrelated documents. For a new idea with no project yet, or when the working
directory is unrelated or not a repository, do not write into it: ask for a
location, or deliver the documents in the response if none is given. Explain the
format choice without making routine formatting or file creation depend on
another confirmation.

Use the linked templates as starting structures, omitting irrelevant sections.
Ground existing paths, patterns, and commands in inspected source. Mark proposed
new files and unverified commands explicitly. Include task outcomes, dependencies,
acceptance criteria, and verification procedures, not invented implementation facts.

A checkpoint records how to validate an outcome. It does not require user
approval after every task. Carry forward existing authorization and preferences;
ask only for unresolved material product choices or actions needing new authority.
The plan itself does not authorize implementation, deployment, purchases, or
external publishing. Complete the requested planning artifacts, then hand them
back; implement only when the user requests implementation too.

## Resume and finish

For a continuation, read the saved brief/plan and relevant conversation context
available in the current environment. Revalidate affected source assumptions
against the current checkout. Do not require a conversation-search API or trust
a document solely because its modification time is recent.

Before delivering, check only what applies to the requested artifacts: every
MVP item in a plan has an observable acceptance test, each roadmap phase ends
with a usable result, and open decisions are visible. Do not add plans, phases,
or tasks to a PRD-only or brief-only request to satisfy this check.
Report any saved document paths, agreed scope, assumptions, and any decision
that still blocks implementation. Verification commands in a plan are proposed
procedures, not evidence that implementation or testing has already happened.
