---
name: daily-travel-culture-brief
description: Produce a daily message about one interesting place to visit or one interesting culture. Prefer summarizing a real article from trusted travel/culture sources (Atlas Obscura, BBC Travel, National Geographic Travel, Condé Nast Traveler, Lonely Planet, UNESCO). If no strong article is available, generate an original brief with factual references/links. Use when asked for recurring daily travel/culture inspiration.
---

# Daily Travel/Culture Brief

Create one concise daily brief for Pringles.

## Output requirements

- Keep to ~120-220 words total.
- Include exactly one featured place or culture topic.
- Include a short “Why it’s interesting” angle.
- Always include a **Links** section.
- In **Links**, include:
  - **1 primary source article URL** from a trusted travel/culture site when source-based, plus
  - **2-4 supporting reference URLs**.
- If fully self-generated, include **3-5 factual reference URLs** from reputable sources.
- End with one friendly question for reflection.

## Source-first workflow (default)

1. Search trusted sources for a fresh article:
   - Atlas Obscura
   - BBC Travel
   - National Geographic Travel
   - Condé Nast Traveler
   - Lonely Planet
   - UNESCO World Heritage
2. Pick one article with concrete cultural/place detail (not generic listicles if avoidable).
3. Read and summarize accurately in your own words.
4. Add the original article URL as the first link.
5. Add 2-4 supporting reference links (official tourism board, UNESCO, encyclopedia, museum, etc.).

## Fallback workflow (if source quality is weak)

1. Pick one place/culture topic.
2. Write an original mini-brief.
3. Add 2-4 reputable references for factual grounding.

## Style

- Warm, playful, curious.
- Concrete details over fluff.
- No repetitive country/topic on consecutive days when history is available.

## Response template

🌍 **Daily Travel/Culture Brief**

**Today’s Pick:** <place or culture>

<120-220 word brief>

**Why it’s interesting:** <1-2 lines>

**Links:**
- <url 1>
- <url 2 optional>
- <url 3 optional>

**Question for Pringles:** <one engaging question>

## Final check before sending

- Did you include a **Links:** header?
- Are there at least **3 total URLs**?
- Is the **first URL** the primary article (when source-based)?
- Are all links concrete and relevant to today’s pick?
