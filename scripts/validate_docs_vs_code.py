import os
import glob
import json

ROOT = os.path.dirname(os.path.dirname(__file__))
DOCS_DIR = os.path.join(ROOT, 'docs')
OUTPUTS_DIR = os.path.join(ROOT, 'orchestrator', 'outputs')

report = []

def find_doc_qid(path):
    name = os.path.basename(path)
    # expect filenames like q11_engagement.md or q1_emociones.md
    if name.startswith('q'):
        parts = name.split('_')
        qid = parts[0]  # e.g., 'q11'
        return qid
    return None


doc_files = glob.glob(os.path.join(DOCS_DIR, 'q*.md'))
for doc in sorted(doc_files):
    qid = find_doc_qid(doc)
    if not qid:
        continue
    with open(doc, 'r', encoding='utf-8') as f:
        text = f.read().lower()
    mentions_actors = 'actor' in text or 'competidor' in text or 'competidores' in text or 'grupo' in text

    # try to load analyzer test output if exists
    test_output_path = os.path.join(OUTPUTS_DIR, f'{qid}_*_test_output.json')
    # fallback to any file that starts with the qid but avoid partial matches like q2 matching q20
    all_candidates = glob.glob(os.path.join(OUTPUTS_DIR, f'{qid}*'))
    outputs = [p for p in all_candidates if os.path.basename(p).startswith(qid + '_') or os.path.basename(p) == f'{qid}.json']
    analyzer_has_actors = False
    analyzer_keys = []
    sample_output = None
    actors_count = 0
    has_analisis_por_publicacion = False
    # look for explicit test output we created earlier
    candidates = [p for p in outputs if p.endswith('_test_output.json')]
    if not candidates and outputs:
        candidates = outputs
    if candidates:
        p = candidates[0]
        try:
            with open(p, 'r', encoding='utf-8') as f:
                data = json.load(f)
            sample_output = data
            # more precise: count actors and check if non-empty
            if isinstance(data, dict) and 'actors' in data:
                try:
                    actors_count = len(data.get('actors') or [])
                except Exception:
                    actors_count = 0
            analyzer_has_actors = isinstance(data, dict) and (actors_count > 0)
            has_analisis_por_publicacion = isinstance(data, dict) and ('analisis_por_publicacion' in data)
            analyzer_keys = list(data.keys())
        except Exception:
            analyzer_has_actors = False
    report.append({
        'doc': os.path.basename(doc),
        'qid': qid,
        'doc_mentions_actors': bool(mentions_actors),
        'analyzer_has_actors': analyzer_has_actors,
        'analyzer_keys': analyzer_keys,
        'actors_count': actors_count,
        'has_analisis_por_publicacion': has_analisis_por_publicacion,
        'sample_output_file': candidates[0] if candidates else None
    })

# print a human friendly summary and also write JSON
for r in report:
    status = 'OK' if (r['doc_mentions_actors'] == r['analyzer_has_actors']) else 'MISMATCH'
    print(f"{r['qid']}: doc={r['doc']} mentions_actors={r['doc_mentions_actors']} analyzer_has_actors={r['analyzer_has_actors']} -> {status}")

with open(os.path.join(OUTPUTS_DIR, 'docs_vs_code_report.json'), 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print('Wrote report to', os.path.join(OUTPUTS_DIR, 'docs_vs_code_report.json'))
