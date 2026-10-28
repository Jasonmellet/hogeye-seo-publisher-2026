# Agent 2 Instructions — Camp Lakota WordPress Image Metadata

## Your Assignment (Agent 2)

You are responsible for processing **List 2** of unprocessed WordPress Media images and updating each image with accurate, SEO-friendly metadata.

### Files (your input list)
- **Primary list (CSV):** `/Users/jasonmellet/Desktop/AGT_Camp_Lakota/work/image-metadata/inputs/image_remaining_unprocessed_part2.csv`
- **Backup list (JSON):** `/Users/jasonmellet/Desktop/AGT_Camp_Lakota/work/image-metadata/inputs/image_remaining_unprocessed_part2.json`

### List 2 range (for sanity check)
- **48 images**
- **First ID:** `2134`
- **Last ID:** `1849`

---

## Core Rules (Important)

- **Do NOT download images** (some are large). Only open by `source_url` in a browser.
- **Do NOT use generic templates**. Every image must be described based on what you actually see.
- **Do NOT guess details you can’t see** (e.g., don’t claim “Masten Lake” if it’s clearly indoors and no lake is visible).
- **Do NOT identify individual people** (no names; avoid describing any individual as a specific real person).
- Write metadata that’s consistent with Camp Lakota brand:
  - Camp Lakota is a **100+ year old residential (sleepaway) summer camp**
  - Location context can be used naturally: **Wurtsboro, New York**, **Masten Lake** (only when relevant)

---

## What You Must Produce (per image)

For each image (by WordPress Media ID), update:
- **Title** (human-friendly, specific)
- **Alt Text** (accurate, SEO-friendly; 12–20 words is a good target)
- **Caption** (1 sentence, friendly + contextual)
- **Description** (2–3 sentences, richer context; include “100+ year” + “residential/sleepaway” naturally where appropriate)

---

## Metadata Quality Guidelines

### Title
- Specific and descriptive
- Include activity + Camp Lakota context when possible
- Examples:
  - “Camp Lakota Campers Tubing on Masten Lake”
  - “Camp Lakota Archery Instruction at Summer Camp”

### Alt Text (most important for SEO + accessibility)
- Describe what’s visibly in the image
- Natural language; no keyword stuffing
- Include “Camp Lakota” when it fits
- Mention **Masten Lake** only if the lake/waterfront is clearly shown or implied

### Caption
- 1 sentence
- Adds meaning/benefit (community, confidence, safety, etc.)

### Description
- 2–3 sentences
- Can mention:
  - “100+ year old residential summer camp”
  - “sleepaway camp”
  - Wurtsboro, NY
  - Masten Lake (if relevant)

---

## Step-by-Step Workflow (repeat for each row)

1. Open the CSV row.
2. Copy the **source_url** and open it in a browser.
3. Visually inspect what’s in the image:
   - What activity? (waterfront / sports / arts / cabin life / dining / staff / facilities)
   - Where? (lakefront / field / indoor space / cabin / ropes course / etc.)
   - What’s the “story” of the photo (fun, instruction, teamwork, tradition)?
4. Draft Title / Alt / Caption / Description using the guidelines above.
5. Update the WordPress Media item:
   - Go to WordPress Admin → **Media** → search by **ID** or paste the Edit URL:
   - Edit URL format:
     - `https://www.camplakota.com/wp-admin/post.php?post=<ID>&action=edit`
6. Paste the metadata, click **Update**.
7. Record completion (see tracking below).

---

## Tracking (so we don’t overlap or miss anything)

Create a simple checklist file locally (recommended):
- `/Users/jasonmellet/Desktop/AGT_Camp_Lakota/work/agents/agent2_done_ids.txt`

Add one ID per line as you complete it:

```text
2134
2133
...
```

If you hit a questionable image (logo, icon, unclear scene), add it to:
- `/Users/jasonmellet/Desktop/AGT_Camp_Lakota/work/agents/agent2_questions.txt`

Include:
- ID
- URL
- what you’re unsure about

---

## Special Cases

### Logos / Icons
- Alt text should describe the logo (e.g., “Camp Lakota logo”).
- Don’t force “Masten Lake” or “sleepaway camp” if the image is purely a logo.

### Aerial/Drone photos
- Mention “aerial view” and describe what’s visible (lake, cabins, fields, etc.).
- Don’t assume details not visible.

### Duplicate images
- If two images appear identical, still give accurate metadata, but note in `agent2_questions.txt` so Jason can decide whether to delete duplicates later.

---

## Deliverable Back to Jason

After finishing the 48 images, send Jason:
- The completed `agent2_done_ids.txt`
- Any `agent2_questions.txt`

That’s it.

