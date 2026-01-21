#!/usr/bin/env python3
"""
Add FAQ Sections to Remaining Blog Posts
Creates appropriate FAQ sections for the 4 posts that are missing them.
"""

import re
import json
from modules.auth import WordPressAuth
from config import Config
from rich.console import Console
from rich.panel import Panel

console = Console()

# FAQ questions for each post based on their topics
POST_FAQS = {
    2697: {  # Counselors Support
        'title': 'How Camp Counselors Support First-Time Sleepaway Campers',
        'faqs': [
            {
                'question': 'What qualifications do Camp Lakota counselors have?',
                'answer': 'All Camp Lakota counselors undergo rigorous background checks, mandatory sexual abuse prevention training, reference verification, and comprehensive interviews. Once at camp, staff complete a week-long orientation covering child development, safety protocols, homesickness management, and camp culture. Many counselors hold certifications in lifeguarding, first aid, or activity-specific areas.'
            },
            {
                'question': 'How do counselors help with homesickness?',
                'answer': 'Our counselors are specifically trained to handle homesickness through normalization, engagement, and support. They help campers by normalizing feelings without amplifying them, keeping campers engaged in activities, creating social connections, and watching for patterns. If homesickness persists beyond 72 hours, directors step in with additional strategies and parent communication.'
            },
            {
                'question': 'What is the staff-to-camper ratio at Camp Lakota?',
                'answer': 'Camp Lakota maintains staff-to-camper ratios that exceed industry standards, ensuring adequate supervision for all activities. Our youngest divisions have additional support through "Camp Moms"—experienced parents who provide extra supervision and comfort for first-time younger campers.'
            },
            {
                'question': 'How do counselors handle campers who are shy or reluctant to participate?',
                'answer': 'Counselors use proximity and modeling rather than forcing participation. They sit near reluctant campers, participate in activities themselves, and create low-pressure invitations. Counselors respect boundaries while keeping doors open for future participation. This approach helps shy campers feel included without pressure.'
            },
            {
                'question': 'Can I communicate directly with my child\'s counselor?',
                'answer': 'For routine questions and concerns, we recommend contacting camp directors rather than counselors directly. This ensures consistent communication and allows directors to coordinate with counselors appropriately. In emergencies or urgent situations, directors will facilitate communication as needed.'
            }
        ]
    },
    2699: {  # Camp Safety
        'title': 'Sleepaway Camp Safety: What Parents Should Know',
        'faqs': [
            {
                'question': 'What medical care is available at Camp Lakota?',
                'answer': 'Camp Lakota has a registered nurse on-site for the entire summer, with doctors who rotate through or are on-call. We are located 10 minutes from urgent care and 20 minutes from a hospital. Our policy is to call parents for any issue beyond a simple band-aid, keeping you informed while handling minor issues in-house.'
            },
            {
                'question': 'How do you ensure water safety?',
                'answer': 'We employ certified lifeguards specifically for our pool and lake, with experienced waterfront directors overseeing operations. All water activities include the buddy system, clearly marked swim areas, swim assessments for appropriate placement, weather monitoring, and waterfront closure during non-activity times. Learn more about our comprehensive water sports program.'
            },
            {
                'question': 'What security measures are in place?',
                'answer': 'Camp Lakota uses a gated entrance with controlled access, delivery protocols that keep vendors off main campus, gates closed and secured at night, camera systems monitoring common areas, and visitor check-in requirements. All visitors must pre-register, and unannounced visits are not permitted during regular camp sessions.'
            },
            {
                'question': 'How do you handle emergencies?',
                'answer': 'We conduct routine emergency drills throughout the summer including fire drills, active shooter drills, large animal drills, and severe weather protocols. We maintain strong relationships with local first responders, have direct communication lines with fire and police departments, and have on-site staff with first responder certification.'
            },
            {
                'question': 'What is your policy on bullying?',
                'answer': 'Camp Lakota maintains a zero-tolerance policy for bullying. Our approach includes clear expectations from Day 1, staff training in recognizing and addressing bullying, immediate intervention when conflicts arise, restorative conversations to address root causes, and parent notification for serious or ongoing issues. We actively cultivate an inclusive environment where every camper belongs.'
            },
            {
                'question': 'Are you accredited by the American Camp Association?',
                'answer': 'Yes, Camp Lakota is accredited by the American Camp Association, which indicates adherence to 300+ safety and quality standards. Accreditation requires regular inspections and ongoing compliance with industry best practices for camp operations, safety, and programming.'
            }
        ]
    },
    2700: {  # Rookie Day
        'title': 'Rookie Day at Camp Lakota',
        'faqs': [
            {
                'question': 'What is Rookie Day?',
                'answer': 'Rookie Day is a low-pressure, one-day introduction to Camp Lakota designed for first-time camp families. It gives campers and parents a chance to experience camp before committing to a full session, helping reduce uncertainty and build confidence for the actual camp experience.'
            },
            {
                'question': 'Who should attend Rookie Day?',
                'answer': 'Rookie Day is most helpful for first-time sleepaway camp families, younger campers who benefit from previewing the environment, campers who feel nervous about new places or routines, and parents who want to understand our daily structure and supervision before enrolling.'
            },
            {
                'question': 'What happens during Rookie Day?',
                'answer': 'Rookie Day typically includes arrival and orientation, a walk-through of camp spaces (cabins, dining hall, activity areas), meeting counselors and learning about supervision, and opportunities for campers to try activities and meet other first-time campers. Parents can attend a tour in the afternoon and stay for dinner.'
            },
            {
                'question': 'Do I need to register for Rookie Day?',
                'answer': 'Yes, registration is required for Rookie Day. Contact our office to learn about upcoming Rookie Day dates and availability. Space may be limited, so we recommend registering early.'
            },
            {
                'question': 'Is Rookie Day required before enrolling?',
                'answer': 'No, Rookie Day is optional but highly recommended for first-time families. It helps both campers and parents feel more confident about the camp experience, but it is not a requirement for enrollment.'
            },
            {
                'question': 'What should we bring to Rookie Day?',
                'answer': 'For Rookie Day, bring a water bottle, comfortable clothes and shoes for walking, and a simple list of questions. Campers will participate in activities and make tie-dye shirts to bring home. Parents will receive information about local activities they can do during the day before returning for the afternoon tour.'
            }
        ]
    },
    2693: {  # Packing Guide
        'title': 'Packing for Sleepaway Camp',
        'faqs': [
            {
                'question': 'How much clothing should I pack for a 3-week vs 6-week session?',
                'answer': 'Since Camp Lakota does laundry weekly, you don\'t need to pack double the clothing for a 6-week session. Pack for about 7-10 days of clothing for both session lengths. The key is comfortable, durable items that can handle frequent washing, not quantity.'
            },
            {
                'question': 'What items are most commonly forgotten?',
                'answer': 'The most commonly forgotten items are shower shoes/flip-flops (essential for the shower house), water shoes for waterfront activities, a second pair of athletic shoes, clearly labeled toiletries, and pre-addressed stamped envelopes for letter writing. Labeling everything is also frequently overlooked but critical.'
            },
            {
                'question': 'Can my child bring electronics or a phone?',
                'answer': 'No, electronics including cell phones, smartphones, tablets, laptops, and video game systems are not permitted at Camp Lakota. This policy allows children to fully disconnect and engage in the camp experience. In emergencies, our staff can reach parents immediately.'
            },
            {
                'question': 'What should I NOT pack?',
                'answer': 'Do not pack electronics, valuables (expensive jewelry, large amounts of cash), outside food (candy, gum, snacks), weapons, fireworks, alcohol, drugs, or vaping products. Also avoid packing more than 10 days worth of clothing as it makes organization harder.'
            },
            {
                'question': 'How important is labeling?',
                'answer': 'Labeling is critical—it\'s the difference between "lost" and "found." Label every clothing item (including socks and underwear), shoes, towels, water bottles, and toiletry bags. Use permanent methods like iron-on labels or permanent marker. Labeled items are much more likely to be returned if lost.'
            },
            {
                'question': 'What type of luggage should we use?',
                'answer': 'We recommend large duffel bags or soft-sided trunks that fit under bunks. Avoid hard-sided suitcases with wheels (wheels break on rough terrain, cases don\'t fit under bunks) and multiple small bags (harder to keep track of).'
            },
            {
                'question': 'When will I receive the official packing list?',
                'answer': 'Camp Lakota provides a comprehensive, age-specific packing list upon enrollment. Contact us to receive the official 2026 Camp Lakota Packing List, or download it from your parent portal after enrollment. The list includes quantities, theme day requirements, and packing tips.'
            }
        ]
    }
}

def create_faq_section(faq_items: list) -> str:
    """Create FAQ section with schema markup."""
    if not faq_items:
        return ''
    
    # Create schema
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": []
    }
    
    for item in faq_items:
        schema["mainEntity"].append({
            "@type": "Question",
            "name": item['question'],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": item['answer']
            }
        })
    
    schema_json = json.dumps(schema, ensure_ascii=False, indent=2)
    
    # Create FAQ section
    block = '<h2 style="margin-top: 2.5rem; margin-bottom: 1.5rem;">Frequently Asked Questions</h2>\n\n'
    block += f'<script type="application/ld+json">\n{schema_json}\n</script>\n\n'
    
    for item in faq_items:
        block += f'''<div class="faq-item" style="margin-bottom: 2rem;">
<h3 style="margin-top: 2rem; margin-bottom: 1rem; font-weight: bold;">{item['question']}</h3>
<p style="margin-bottom: 1.5rem; line-height: 1.7;">{item['answer']}</p>
</div>

'''
    
    return block

def main():
    console.print(Panel.fit(
        "[bold cyan]Add FAQ Sections to Remaining Blog Posts[/bold cyan]",
        border_style="cyan"
    ))
    
    auth = WordPressAuth()
    session = auth.get_session()
    
    for post_id, post_info in POST_FAQS.items():
        console.print(f"\n[cyan]Processing: {post_info['title']}[/cyan]")
        console.print(f"  [green]✓ Adding {len(post_info['faqs'])} FAQ questions[/green]")
        
        # Get post
        response = session.get(
            Config.get_api_url(f'posts/{post_id}'),
            params={'context': 'edit'},
            timeout=30
        )
        
        if response.status_code != 200:
            console.print(f"  [red]✗ Error fetching post {post_id}[/red]")
            continue
        
        post = response.json()
        content = post.get('content', {}).get('raw', '')
        
        # Check if FAQ already exists
        if re.search(r'<h2[^>]*>Frequently Asked Questions</h2>', content, re.IGNORECASE):
            console.print(f"  [yellow]⚠ FAQ section already exists, skipping[/yellow]")
            continue
        
        # Create FAQ section
        faq_section = create_faq_section(post_info['faqs'])
        
        # Insert before CTA section or at the end
        cta_pattern = r'(<h3[^>]*>Ready|</div>\s*<hr>|<div class="cta-section")'
        cta_match = re.search(cta_pattern, content, re.IGNORECASE)
        
        if cta_match:
            insert_pos = cta_match.start()
            new_content = content[:insert_pos] + '\n\n' + faq_section + '\n\n' + content[insert_pos:]
        else:
            # Append at end
            new_content = content + '\n\n' + faq_section
        
        # Update post
        update_response = session.post(
            Config.get_api_url(f'posts/{post_id}'),
            json={'content': new_content},
            timeout=30
        )
        
        if update_response.status_code == 200:
            console.print(f"  [green]✓ FAQ section added successfully[/green]")
        else:
            console.print(f"  [red]✗ Error updating: {update_response.status_code}[/red]")
    
    console.print("\n" + "="*60)
    console.print(Panel.fit(
        "[bold green]FAQ Sections Added[/bold green]",
        border_style="green"
    ))
    console.print("\n[cyan]All blog posts now have FAQ sections with schema markup![/cyan]")

if __name__ == '__main__':
    main()
