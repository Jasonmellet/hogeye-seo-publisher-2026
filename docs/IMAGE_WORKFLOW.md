# Image Metadata Workflow Guide

## 🎯 Goal
Update ~300 WordPress images with professional metadata (titles, alt text, captions, descriptions)

## ✅ Test Case Success
**Image:** DSC03139 (ID: 2705)  
**Result:** Successfully updated with full metadata ✓

---

## 📋 Three-Step Workflow

### Step 1: Analyze & Download Images
**Script:** `scripts/images/analyze_images.py`

**What it does:**
- Connects to WordPress
- Finds all images missing metadata (~300 images)
- Downloads first batch (10-20 images) to `work/image-metadata/temp_images_for_analysis/`
- Creates a JSON file with image data

**Run it:**
```bash
python -m scripts.images.analyze_images
```

**Output:**
- Downloaded images in `work/image-metadata/temp_images_for_analysis/`
- `work/image-metadata/batches/image_batch_1_for_analysis.json`

---

### Step 2: Generate Metadata (Interactive)
**Process:** Human reviews images + AI generates metadata

**How it works:**
1. Open images from `work/image-metadata/temp_images_for_analysis/`
2. For each image, AI (me) will:
   - View the image
   - Identify what's in it (activity, location, people, mood)
   - Generate:
     - Professional title
     - SEO-optimized alt text
     - Engaging caption
     - Detailed description
     - Suggested filename
     - Relevant keywords

3. Save all metadata to:
   - `image_metadata_generated.json` (for script processing)
   - `image_metadata_generated.csv` (for human review)

**Quality Standard (from DSC03139):**
- **Title:** Descriptive and professional
- **Alt Text:** 10-15 words, SEO keywords included
- **Caption:** 1-2 sentences, explains significance
- **Description:** 2-3 sentences, more detail
- **Keywords:** 5-7 relevant tags

---

### Step 3: Update WordPress
**Script:** `scripts/images/update_image_metadata.py`

**What it does:**
- Reads `image_metadata_generated.json`
- Updates each image in WordPress via API
- Shows progress and results

**Test first (DRY RUN):**
```bash
DRY_RUN=true python -m scripts.images.update_image_metadata
```

**Run for real:**
```bash
python -m scripts.images.update_image_metadata
```

**Output:**
- Success/failure report
- Updated count
- Any errors

---

## 🔄 Processing All 300 Images

**Batch Processing Strategy:**

### Option A: Small Batches (Recommended)
- Process 10-20 images at a time
- Review each batch before uploading
- Safer, more controlled

**Workflow:**
1. Run `analyze_images.py` (downloads 10 images)
2. Generate metadata for those 10
3. Run `update_image_metadata.py` (updates those 10)
4. Repeat for next batch

**Time estimate:** ~30 batches × 15 minutes = 7-8 hours total

### Option B: Larger Batches
- Process 50 images at a time
- Faster but less review
- Still safe with dry run testing

**Workflow:**
1. Modify batch size in `analyze_images.py` to 50
2. Generate metadata for all 50
3. Review CSV file
4. Update WordPress
5. Repeat ~6 times

**Time estimate:** ~6 batches × 45 minutes = 4-5 hours total

### Option C: Full Automation (Future)
- Integrate Perplexity API for image analysis
- Process all 300 automatically
- Human review at end
- Most time-efficient

**Time estimate:** 1-2 hours of setup + 1 hour runtime

---

## 📊 Metadata Guidelines

### What Makes Good Image Metadata?

#### Title
- Clear and descriptive
- Include activity or subject
- Include location if relevant
- Professional tone

**Examples:**
- ✅ "Camp Lakota CIT Counselors in Training Group Photo"
- ✅ "Kids Swimming at Masten Lake Waterfront"
- ✅ "Arts and Crafts Activity in Camp Studio"
- ❌ "DSC03139"
- ❌ "IMG_5432"

#### Alt Text (SEO Critical)
- 10-15 words ideal
- Describe what's actually in the image
- Include 2-3 keywords naturally
- Complete sentence structure

**Examples:**
- ✅ "Camp Lakota CIT counselors in training posing together on the sandy beach at Masten Lake during summer camp"
- ✅ "Children learning archery skills with certified instructor at Camp Lakota outdoor range"
- ❌ "Kids at camp" (too short, not descriptive)
- ❌ "Camp Lakota summer camp kids children archery swimming lake activities" (keyword stuffing)

#### Caption
- 1-2 sentences
- Explains significance or context
- Can include program details
- Engaging and warm tone

**Examples:**
- ✅ "Our CIT (Counselors in Training) program develops teenage leadership skills through hands-on mentorship and responsibility at Camp Lakota."
- ✅ "Campers develop confidence and focus through our archery program, taught by certified instructors on our dedicated range."

#### Description
- 2-3 sentences
- More detail than caption
- Can include specific program info
- Educational or informative

#### Keywords/Tags
- 5-7 relevant keywords
- Mix of general and specific
- Include program names
- Include location names

**Common Keywords:**
- Camp Lakota
- Masten Lake
- Summer camp
- Sleepaway camp
- [Activity name]
- [Program name]
- [Age group]

---

## 🎨 Image Categories We'll Likely See

Based on typical summer camp photography:

### Waterfront Activities
- Swimming
- Kayaking
- Canoeing
- Paddleboarding
- Water skiing
- Beach games

**Common keywords:** Masten Lake, waterfront, water sports, swimming, boating

### Land Activities  
- Archery
- Sports (soccer, basketball, volleyball)
- Gaga ball
- Ropes course
- Rock climbing

**Common keywords:** outdoor activities, team sports, adventure activities

### Arts & Crafts
- Pottery
- Painting
- Tie-dye
- Jewelry making
- Woodworking

**Common keywords:** creative arts, arts and crafts, camp creativity

### Group & Social
- Campfires
- Cabin groups
- Dining hall
- Camp-wide events
- Assemblies

**Common keywords:** camp community, camp traditions, camp friendships

### Staff & Leadership
- Counselors
- CITs
- Instructors
- Group photos

**Common keywords:** camp counselors, camp staff, CIT program, youth leadership

### Facilities & Grounds
- Cabins
- Dining hall
- Lakefront
- Fields
- Campus views

**Common keywords:** Camp Lakota campus, camp facilities, Wurtsboro NY

---

## 📝 Current Status

### Completed:
- ✅ System design
- ✅ Test case (DSC03139) successful
- ✅ Scripts created:
  - `analyze_images.py`
  - `generate_image_metadata.py`
  - `update_image_metadata.py`

### Next Steps:
1. Run `analyze_images.py` to download first batch
2. AI reviews and generates metadata for batch 1
3. Save metadata to JSON/CSV
4. Test update with DRY_RUN=true
5. Update batch 1 in WordPress
6. Review results
7. Repeat for remaining batches

---

## 🚀 Ready to Start?

**Let's process the first batch:**

```bash
cd /Users/jasonmellet/Desktop/AGT_Camp_Lakota
source venv/bin/activate
python -m scripts.images.analyze_images
```

This will download the first 10 images and prepare them for metadata generation!

---

## 💡 Tips

1. **Be consistent** with naming conventions
2. **Use active voice** in descriptions when possible
3. **Focus on benefits** in captions (what kids learn/experience)
4. **Include location** (Masten Lake, Wurtsboro) for local SEO
5. **Mention Camp Lakota** in most descriptions
6. **Avoid duplicate** alt text (each should be unique)
7. **Keep it natural** - write for humans, not just SEO

---

## ⏱️ Time Tracking

- **Per image:** ~1-2 minutes (view, analyze, generate metadata)
- **Per batch of 10:** ~15 minutes
- **Per batch of 50:** ~60-90 minutes
- **All 300 images:** 5-10 hours total (depending on batch size)

---

**Questions?** Just ask! Ready to start processing when you are. 🎨📸
