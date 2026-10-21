# Writing loop

Standing rule, rewritten October 19, 2026. The previous loop passed a piece that was not about anything. The water article is the example. Do not write that way again.

September stays as Schell approved it.

October 2026 in the hub is a placeholder. The copy was removed. The rows stay because the images stay. Do not push the October files that are still in the brand repos. A push puts the old copy back and sets the row to in review.

Paid count, and a refresh counts as one piece:

- Boar Blanket: 10
- Big Pig Traps: 10 from September on
- HogEye: 5

Writer for Boar Blanket, after the sentence below is approved: gpt-6 Luna, reasoning effort low, no temperature setting. Big Pig and HogEye stay on their own writer until a sample is chosen the same way.

## 0. The sentence

Before a model is called, write one sentence a landowner could say on the phone. It names the situation and the move.

Show that sentence. Do not draft until it is approved.

Stop, and do not draft, if any of these are true:

- The sentence is the keyword with grammar wrapped around it.
- The sentence is a list of sources, studies, or disclaimers.
- You cannot say what the reader should do.
- The only reason to write it is an empty paid slot, and nobody is searching for it. Say that. Wait.

## 1. Identity

- The piece fills one open slot in this month's paid count.
- It is either a new URL or a named refresh of one existing URL. A collision with a page we already have means refresh that page, not skip the slot.
- `externalId` is new for this month. It is not a September id, and it is not the slug.
- `period` is this month, `YYYY-MM`.
- A refresh sets `existing_url` to the live page and does not create a second slug.
- The September row is not edited and not re-ingested.
- An October 2026 placeholder row is not re-ingested with the old file.

Stop if the id or period points at an approved earlier month.

## 2. Facts

The article teaches the sentence from phase 0. A source is one sentence inside that scene. It is not a section of its own.

- The mechanism matches that brand's facts file. For the Boar Blanket net: it stays raised while the sounder feeds under it, the trapper lowers the skirt onto the ground by hand, the trapper leaves, and the hogs push under the skirt on the next visit. A phone or a camera does not lower it. Say this only when the piece is about the net.
- No invented size, price, capture rate, or competitor spec. If it is not sourced, it is left out.
- A number appears only when the reader needs it to do the thing in the sentence.
- A closed program is not described as open. The 2026 Arkansas cost-share signup is closed.
- Health and disease lines name the agency source already in the brief.
- HogEye does not claim the camera closes a gate by itself.
- The piece does not repeat another brand's article. Oklahoma and Mississippi stay on Boar Blanket. HogEye Mini on the panel trap is not the drop-trap article.
- Do not link another article unless this reader needs that page to do the thing in the sentence.

Stop if a fact is wrong. Voice does not excuse a wrong catch.

## 3. Voice

Facts from phase 2 still win.

The sound we are matching is Schell, on a dry bait site: "If you don't have any water on a site where you know hogs are active, you can create a mud hole with several buckets of water." Second person, a contraction, one practical move. Source: `BB_PRODUCT_FACTS.md` section 6.

- Boar Blanket: calm and concrete. Source: `BB_BRAND_BASELINE.md` section 9.
- HogEye: a field operator talking to someone already at the trap. Outcome first. No em dash. Source: HogEye `BRAND_BASELINE.md` voice table and `HUMANIZER_STYLE_GUIDE.md`.
- Big Pig: short, specific, and warm. "We love to talk pig." Lead with the steel and the job, not the price. Source: Big Pig `BRAND_BASELINE.md` "Voice and tone."

The first paragraph is the approved sentence, in normal English. The keyword goes in the slug, the title, and the meta description. It goes in the first paragraph only when a person would actually say that phrase.

Read the first paragraph out loud. It fails if it could not be said on a phone call, if it names the page, or if it opens with "Many landowners face the challenge."

If the read-aloud fails, stop. Do not add a table, a FAQ, or another source to repair it.

## 4. A second provider checks the draft

The model that writes the draft does not check it. Before Jason sees the article, one different provider reads it once against this loop.

- OpenAI writes it, Grok checks it.
- Grok writes it, gpt-6 Luna checks it. Reasoning effort low. No temperature setting.
- The checker does not write a replacement article. It names only what fails: a wrong fact, a first paragraph that cannot be said out loud, a repeat of a page we already have, a link to a competitor, or a keyword forced into broken English.
- Fix those failures. Then show the draft. A draft that skipped this check does not get shown.
- The food-plots refresh approved on October 20, 2026 was accepted before this rule. It is not sent back through the check.

## 5. Local gates

Run that repo's existing check. Set the word target to the real length of this draft.

- Boar Blanket: brief contract, rubric, SEO placement, readability, output hygiene.
- Big Pig Traps: `scripts/seo/validate_bpt_content.mjs` on this file only.
- HogEye: `scripts/seo/hogeye_content_quality.py` on this file only.

A local pass does not mean the piece is about something. Phase 0 still wins.

Stop on a hard fail.

## 6. Hub

- Push this piece only, for this month.
- `pass` goes to Schell.
- `flag` still saves. Read the reason. Fix it if the reason is a wrong fact or a first paragraph that cannot be said out loud, then push this piece again.
- `422` means nothing was saved. Return to phase 2.
- Do not push the rest of the month in the same call.
- Do not push over an October 2026 placeholder unless this piece is the approved replacement for that one row.

The TL;DR, if the draft has one, is for Schell. The publisher strips that opening paragraph before WordPress or Shopify.

## 7. Website

This phase waits until Schell has approved the piece.

- Create a CMS draft. Do not go live in the same step.
- If the live slug already exists, update that URL only when this piece is an ordered refresh. Otherwise use a new draft slug.
- Do not auto-insert images.
- Lily adds images, reads the draft, and publishes.

Live posts from earlier months are not pulled back through this loop unless a later month names that URL as a refresh.
