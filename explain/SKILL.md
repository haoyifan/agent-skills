---
name: explain
description: Explain a technical concept at three levels of depth — simple (for a child), intermediate, and expert — with ASCII visualizations at each level. Input can be a word, term, or sentence to explain, or empty to explain the last concept mentioned in conversation.
---

# Explain

Break down a technical concept into three progressive levels of understanding, each accompanied by an ASCII visualization.

## Input

- **A word, term, or sentence** — explain that concept.
- **Empty** — identify the most recent technical concept from the conversation and explain it.

When the input is empty, scan the conversation for the last technical term, jargon, or concept the assistant or user mentioned. State what you identified before explaining.

## Output structure

Produce exactly three levels. Each level has a heading, a prose explanation, and a visualization.

### Level 1 — Simple (like explaining to a 10-year-old)

- Use everyday language, no jargon.
- Analogies to physical, tangible things the reader already knows (boxes, pipes, roads, kitchens, mailboxes, etc.).
- Max 4 sentences.
- Visualization: a simple ASCII diagram using the analogy (e.g., stick-figure flow, labeled boxes).

### Level 2 — Intermediate (someone who codes or has general tech literacy)

- Introduce the real terminology, but define each term on first use.
- Explain *how* it works — the mechanism, not just the metaphor.
- 4-6 sentences.
- Visualization: an ASCII diagram showing the actual components and their relationships (arrows, labeled nodes, data flow, layers).

### Level 3 — Expert (a practitioner in the field)

- Assume full domain vocabulary.
- Cover edge cases, tradeoffs, failure modes, or performance characteristics.
- Reference relevant protocols, algorithms, data structures, or standards by name.
- 4-8 sentences.
- Visualization: a detailed ASCII diagram — internal architecture, state machines, memory layouts, protocol sequences, or timing diagrams as appropriate.

## Visualization rules

- Every level MUST have exactly one ASCII diagram inside a fenced code block.
- Diagrams use box-drawing characters (`─`, `│`, `┌`, `┐`, `└`, `┘`, `├`, `┤`, `┬`, `┴`, `┼`), arrows (`→`, `←`, `↑`, `↓`, `⟶`, `──▶`), and plain ASCII (`+`, `-`, `|`, `>`, `*`) as needed.
- Keep diagrams under 20 lines tall and under 72 characters wide so they render well in a terminal.
- Label every box and arrow — no unlabeled shapes.
- Each level's diagram should be progressively more detailed than the previous, not a repeat.

## Formatting template

```
## {Concept Name}

### Simple

{Analogy-based explanation in 2-4 sentences.}

\```
{Simple ASCII diagram}
\```

### Intermediate

{Mechanism-level explanation in 4-6 sentences.}

\```
{Component-level ASCII diagram}
\```

### Expert

{Practitioner-level explanation in 4-8 sentences.}

\```
{Detailed architecture/protocol ASCII diagram}
\```
```

## Guidelines

- Start directly with the explanation — no preamble like "Great question!" or "Let me explain."
- If the concept spans multiple domains (e.g., "mutex" applies to OS, databases, distributed systems), pick the most common context unless the conversation makes the domain obvious.
- If the input is ambiguous (e.g., "tree" could be data structure or DOM tree), pick the most likely interpretation from conversation context and state your choice.
- Do not add a summary section at the end — the three levels speak for themselves.
