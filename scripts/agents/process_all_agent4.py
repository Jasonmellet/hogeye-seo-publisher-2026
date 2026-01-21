#!/usr/bin/env python3
"""
Process all Agent 4 images - batch update script
This script processes images that have been viewed and metadata generated
"""

import json
from pathlib import Path
from modules.auth import WordPressAuth
from config import Config

WORK_AGENTS_DIR = Path("work") / "agents"
DONE_IDS_FILE = WORK_AGENTS_DIR / "agent4_done_ids.txt"
QUESTIONS_FILE = Path(__file__).parent / 'agent4_questions.txt'
PART4_JSON = Path(__file__).parent / 'image_remaining_unprocessed_part4.json'

def load_done_ids():
    if DONE_IDS_FILE.exists():
        with open(DONE_IDS_FILE, 'r') as f:
            return {int(line.strip()) for line in f if line.strip().isdigit()}
    return set()

def save_done_id(image_id):
    with open(DONE_IDS_FILE, 'a') as f:
        f.write(f"{image_id}\n")

def save_question(image_id, source_url, question):
    with open(QUESTIONS_FILE, 'a') as f:
        f.write(f"ID: {image_id}\nURL: {source_url}\nQuestion: {question}\n{'='*80}\n\n")

def update_metadata(image_id, metadata, session):
    update_data = {k: v for k, v in metadata.items() if v}
    if not update_data:
        return False
    
    try:
        media_url = Config.get_api_url(f'media/{image_id}')
        response = session.post(media_url, json=update_data, timeout=30)
        return response.status_code == 200
    except Exception as e:
        print(f"Error updating {image_id}: {e}")
        return False

# Metadata for images processed so far
metadata_batch = {
    1326: {
        'title': 'Camp Lakota Staff Member with Volleyball',
        'alt_text': 'Camp Lakota staff member wearing tie-dye shirt holding yellow volleyball at the camp waterfront area',
        'caption': 'Dedicated Camp Lakota staff members help create memorable experiences for campers.',
        'description': 'Camp Lakota staff play a vital role in the 100+ year old residential summer camp experience in Wurtsboro, New York. Their enthusiasm and dedication help ensure campers have safe, fun, and meaningful experiences throughout their stay.'
    },
    1325: {
        'title': 'Camp Lakota Staff Member at Waterfront Area',
        'alt_text': 'Camp Lakota staff member in tie-dye shirt holding Spalding volleyball at camp recreational area',
        'caption': 'Camp Lakota staff members are integral to creating a positive camp environment.',
        'description': 'The staff at Camp Lakota, a 100+ year old residential summer camp in Wurtsboro, New York, bring energy and expertise to every activity. Their commitment helps maintain the traditions and values that make Camp Lakota special.'
    }
}

if __name__ == '__main__':
    auth = WordPressAuth()
    session = auth.get_session()
    done_ids = load_done_ids()
    
    for image_id, metadata in metadata_batch.items():
        if image_id not in done_ids:
            if update_metadata(image_id, metadata, session):
                save_done_id(image_id)
                print(f"✅ Updated {image_id}")
            else:
                print(f"❌ Failed {image_id}")
    
    # Note potential duplicate
    save_question(1325, 'https://www.camplakota.com/wp-content/uploads/2024/04/michael-jpg.webp', 
                 'Similar to image 1326 - may be duplicate, both show same person with volleyball')
