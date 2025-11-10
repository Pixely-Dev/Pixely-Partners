import json
import random
from datetime import datetime, timedelta
from faker import Faker
import gspread
from google.oauth2 import service_account
import os

fake = Faker()

# --- Configuration --- #
# Assuming gcp_credentials.json is at the root of pixely_stable
CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'gcp_credentials.json')
# This should be the URL of your Google Sheet
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1kGDc9GI1qnnQHk4n2TfbmRhuua-FOno6mTXXO0czmp4/edit?gid=261178786#gid=261178786"

# --- Google Sheets Helper Functions --- #
def authenticate_gspread():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scope)
    client = gspread.authorize(creds)
    return client

def get_or_create_worksheet(spreadsheet, sheet_name, headers):
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="1", cols=str(len(headers)))
    
    # Clear existing content and add headers
    worksheet.clear()
    worksheet.append_row(headers)
    return worksheet

def write_data_to_sheet(worksheet, data, headers):
    if not data:
        return
    
    # Convert list of dicts to list of lists, ensuring order matches headers
    rows = []
    for item in data:
        row = [item.get(header) for header in headers]
        rows.append(row)
    
    worksheet.append_rows(rows)

# --- Data Generation Functions --- #
def generate_ficha_cliente_data(client_id, client_name, primary_business_goal, brand_archetype, tone_of_voice, content_pillars, competitors):
    # Build competitor landscape including synthetic follower counts so analyzers can compute
    # meaningful group metrics. Each competitor will include follower counts per network.
    competitor_landscape = []
    for comp_name, comp_instagram in competitors:
        competitor_landscape.append({
            "name": comp_name,
            "instagram": f"https://www.instagram.com/{comp_instagram}/",
            "instagram_followers": random.randint(5000, 800000),
            "tiktok_followers": random.randint(2000, 400000),
            "other_followers": random.randint(500, 100000)
        })

    return {
        "client_id": client_id,
        "client_name": client_name,
        "primary_business_goal": primary_business_goal,
        "brand_archetype": brand_archetype,
        "tone_of_voice": tone_of_voice,
        "content_pillars": content_pillars,
        # store as list (not json string) so downstream pipelines can consume directly
        "competitor_landscape": competitor_landscape,
        "seguidores_instagram": random.randint(10000, 1000000),
        "seguidores_tiktok": random.randint(5000, 500000),
        "seguidores_otra_red_x": random.randint(1000, 100000)
    }

def generate_social_media_posts_data(client_id, owner_username, is_competitor, num_posts=50):
    posts = []
    # A small controlled pool of hashtags to ensure repetitions for testing
    hashtag_pool = ["promo", "brand", "tips", "IA", "reel", "video", "social", "marketing"]
    for i in range(num_posts):
        post_id = fake.uuid4()
        post_url = f"https://www.instagram.com/p/{post_id}/"
        timestamp = fake.date_time_between(start_date="-1y", end_date="now")
        content_type = random.choice(["Reel", "Carrusel", "Imagen", "Video"])
        # Build a caption that includes repeated hashtags from the controlled pool
        caption_text = fake.sentence(nb_words=random.randint(8, 18))
        extra_sentence = fake.sentence(nb_words=random.randint(4, 10))
        emoji_segment = random.choice(["✨", "💖", "🔥", "🤩", "🚀", "🌟", "💫", "💯", "🙌"]) + " " + fake.sentence(nb_words=random.randint(3, 8))
        # pick 2-4 hashtags, allowing repeats across posts to ensure frequency
        chosen_hashtags = random.choices(hashtag_pool, k=random.randint(2, 4))
        hashtags_segment = " " + " ".join(["#" + h for h in chosen_hashtags])
        caption_parts = [caption_text, extra_sentence, emoji_segment, hashtags_segment]
        caption = " ".join(caption_parts)
        likes_count = random.randint(100, 10000)
        comments_count = random.randint(10, 500)
        # Ensure viewsCount exists for all content types (helps ER calculations in tests)
        if content_type in ["Reel", "Video"]:
            views_count = random.randint(1000, 100000)
        else:
            # Images and Carrusels typically have fewer recorded views; still include a number
            views_count = random.randint(200, 20000)

        posts.append({
            "client_id": client_id,
            "post_url": post_url,
            "ownerUsername": owner_username,
            "social_network": "Instagram",
            "timestamp": timestamp.isoformat(),
            "content_type": content_type,
            "caption": caption,
            "likesCount": likes_count,
            "commentsCount": comments_count,
            "viewsCount": views_count,
            "is_sponsored": fake.boolean(chance_of_getting_true=10),
            "is_competitor": is_competitor
        })
    return posts

def generate_comments_data(client_id, post_url, num_comments=100):
    comments = []
    for _ in range(num_comments):
        timestamp = fake.date_time_between(start_date="-1y", end_date="now")
        comment_templates = [
            lambda: fake.sentence(nb_words=random.randint(5, 15)),
            lambda: f"¡{random.choice(['Gran', 'Excelente', 'Increíble'])} publicación! {fake.sentence(nb_words=random.randint(3, 8))}",
            lambda: f"Me encanta esto {random.choice(['✨', '💖', '🔥', '🤩'])}",
            lambda: f"¿Qué opinan de esto? {fake.sentence(nb_words=random.randint(4, 10))}?",
            lambda: f"{fake.sentence(nb_words=random.randint(2, 5))} 🙌",
            lambda: fake.paragraph(nb_sentences=random.randint(1, 2))
        ]
        comment_text = random.choice(comment_templates)()
        owner_username = fake.user_name()
        comments.append({
            "client_id": client_id,
            "post_url": post_url,
            "comment_text": comment_text,
            "timestamp": timestamp.isoformat(),
            "ownerUsername": owner_username
        })
    return comments

def main():
    # --- Data Generation --- #
    client_id = 1
    client_name = "PixelyBrand"
    primary_business_goal = "Aumentar Engagement"
    brand_archetype = "El Sabio"
    tone_of_voice = "Educativo"
    content_pillars = "Marketing Digital, IA, Analítica"
    
    competitors = [
        ("CompetitorA", "competitor_a_insta"),
        ("CompetitorB", "competitor_b_insta")
    ]

    ficha_cliente_data = [generate_ficha_cliente_data(
        client_id, client_name, primary_business_goal, brand_archetype,
        tone_of_voice, content_pillars, competitors
    )]

    all_posts = []
    client_posts = generate_social_media_posts_data(client_id, client_name.lower(), False, num_posts=50)
    all_posts.extend(client_posts)
    for comp_name, comp_instagram in competitors:
        comp_posts = generate_social_media_posts_data(client_id, comp_instagram, True, num_posts=50)
        all_posts.extend(comp_posts)
    
    all_comments = []
    for post in all_posts:
        comments = generate_comments_data(client_id, post["post_url"], num_comments=100)
        all_comments.extend(comments)

    # --- Google Sheets Writing --- #
    if GOOGLE_SHEET_URL == "YOUR_GOOGLE_SHEET_URL_HERE":
        print("ERROR: Please replace 'YOUR_GOOGLE_SHEET_URL_HERE' with your actual Google Sheet URL in populate_data.py")
        return

    try:
        client = authenticate_gspread()
        spreadsheet = client.open_by_url(GOOGLE_SHEET_URL)

        # Ficha Cliente
        ficha_cliente_headers = [
            "client_id", "client_name", "primary_business_goal", "brand_archetype",
            "tone_of_voice", "content_pillars", "competitor_landscape",
            "seguidores_instagram", "seguidores_tiktok", "seguidores_otra_red_x"
        ]
        ficha_cliente_ws = get_or_create_worksheet(spreadsheet, "Ficha Cliente", ficha_cliente_headers)
        write_data_to_sheet(ficha_cliente_ws, ficha_cliente_data, ficha_cliente_headers)
        print("Ficha Cliente data written successfully.")

        # Social_Media_Posts
        social_media_posts_headers = [
            "client_id", "post_url", "ownerUsername", "social_network", "timestamp",
            "content_type", "caption", "likesCount", "commentsCount", "viewsCount",
            "is_sponsored", "is_competitor"
        ]
        social_media_posts_ws = get_or_create_worksheet(spreadsheet, "Social_Media_Posts", social_media_posts_headers)
        write_data_to_sheet(social_media_posts_ws, all_posts, social_media_posts_headers)
        print("Social_Media_Posts data written successfully.")

        # Comentarios
        comentarios_headers = [
            "client_id", "post_url", "comment_text", "timestamp", "ownerUsername"
        ]
        comentarios_ws = get_or_create_worksheet(spreadsheet, "Comentarios", comentarios_headers)
        write_data_to_sheet(comentarios_ws, all_comments, comentarios_headers)
        print("Comentarios data written successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

    # --- Also write a local 'ingested_data.json' for orchestrator/frontend testing ---
    try:
        project_root = os.path.dirname(os.path.dirname(__file__))
        outputs_dir = os.path.join(project_root, 'orchestrator', 'outputs')
        os.makedirs(outputs_dir, exist_ok=True)

        ingested = {
            "client_ficha": ficha_cliente_data[0],
            "posts": all_posts,
            # include generated comments locally so analyzers can run offline/tests
            "comments": all_comments
        }
        ingested_path = os.path.join(outputs_dir, 'ingested_data.json')
        with open(ingested_path, 'w', encoding='utf-8') as jf:
            json.dump(ingested, jf, ensure_ascii=False, indent=2)
        print(f"Local ingested_data.json written to: {ingested_path}")
    except Exception as e:
        print(f"Warning: could not write local ingested_data.json: {e}")

if __name__ == "__main__":
    main()