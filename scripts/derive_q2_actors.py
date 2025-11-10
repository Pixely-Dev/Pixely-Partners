import json
import os
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(__file__))
outputs_dir = os.path.join(ROOT, 'orchestrator', 'outputs')
q2_path = os.path.join(outputs_dir, 'q2_personalidad.json')
ingested_path = os.path.join(outputs_dir, 'ingested_data.json')

if not os.path.exists(q2_path):
    print('q2_personalidad.json not found in outputs')
    raise SystemExit(1)

with open(q2_path, 'r', encoding='utf-8') as f:
    q2 = json.load(f)

with open(ingested_path, 'r', encoding='utf-8') as f:
    ingested = json.load(f)

posts = ingested.get('posts', [])
def extract_post_id(url):
    if not url:
        return None
    # Typical Instagram post URL: https://www.instagram.com/p/<post_id>/
    parts = url.split('/p/')
    if len(parts) > 1:
        pid = parts[1].strip('/')
        # sometimes there may be extra path components or query strings
        pid = pid.split('/')[0].split('?')[0]
        return pid
    # fallback: return the full url
    return url

# map by full url and by post id for more robust matching
post_owner = {}
for p in posts:
    url = p.get('post_url')
    if not url:
        continue
    owner = p.get('ownerUsername')
    post_owner[url] = owner
    pid = extract_post_id(url)
    if pid:
        post_owner[pid] = owner

analisis_por_publicacion = q2.get('analisis_por_publicacion', [])
actors_map = {}
for item in analisis_por_publicacion:
    url = item.get('post_url')
    owner = None
    if url:
        # try exact url first
        owner = post_owner.get(url)
        if not owner:
            # try by post id extracted from the analyzer output
            pid = extract_post_id(url)
            if pid:
                owner = post_owner.get(pid)
    if not owner:
        continue
    actors_map.setdefault(owner, {'rasgos': [], 'intensidades': []})
    rasgos = item.get('rasgos_distribuidos') or {}
    if rasgos:
        actors_map[owner]['rasgos'].append(rasgos)
    intensidad = item.get('intensidad_promedio', 0.0)
    actors_map[owner]['intensidades'].append(float(intensidad or 0.0))

# helper for followers
cf = ingested.get('client_ficha', {})

def find_followers(username):
    if not username:
        return None
    client_name = cf.get('client_name', '')
    if username.lower() in client_name.lower():
        return cf.get('seguidores_instagram')
    for c in cf.get('competitor_landscape', []) or []:
        insta = c.get('instagram') or ''
        if username.lower() in insta.lower():
            return c.get('instagram_followers')
    return None

actors = []
for owner, vals in actors_map.items():
    rasgos_list = vals.get('rasgos', [])
    intensidades = vals.get('intensidades', [])
    avg_rasgos = {}
    if rasgos_list:
        avg_rasgos = pd.DataFrame(rasgos_list).mean().to_dict()
    avg_int = float(pd.Series(intensidades).mean()) if intensidades else 0.0
    followers = find_followers(owner)
    actors.append({
        'actor': owner or 'unknown',
        'username': owner or 'unknown',
        'followers': followers,
        'rasgos_distribuidos': avg_rasgos,
        'intensidad_promedio': avg_int
    })

# write new file
out_path = os.path.join(outputs_dir, 'q2_personalidad_with_actors.json')
with open(out_path, 'w', encoding='utf-8') as f:
    new = dict(q2)
    new['actors'] = actors
    json.dump(new, f, ensure_ascii=False, indent=2)

print('Wrote', out_path)
