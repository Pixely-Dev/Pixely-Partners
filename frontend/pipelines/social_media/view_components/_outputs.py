import os


def get_outputs_dir():
    """Resolve a single canonical orchestrator outputs directory.

    Resolution order:
    1. Environment variables: PIXELY_OUTPUTS_DIR, ORCHESTRATOR_OUTPUTS, OUTPUTS_DIR
    2. Container default: /app/orchestrator/outputs
    3. Repo-relative: climb from this file up to project root and check orchestrator/outputs
    4. Final fallback: the repo-relative candidate (even if not present)

    Returns an absolute path string.
    """
    env_vars = ["PIXELY_OUTPUTS_DIR", "ORCHESTRATOR_OUTPUTS", "OUTPUTS_DIR"]
    candidates = []

    # 1) Environment overrides
    for v in env_vars:
        val = os.environ.get(v)
        if val:
            candidates.append(os.path.abspath(val))

    # 2) Common container path
    candidates.append("/app/orchestrator/outputs")

    # 3) Repo-relative candidate (from this file's location)
    # view_components is at: <repo>/pixely_stable/frontend/pipelines/social_media/view_components
    # climb up 4 levels to reach pixely_stable, then orchestrator/outputs
    base = os.path.dirname(__file__)
    repo_relative = os.path.abspath(os.path.join(base, '..', '..', '..', '..', 'orchestrator', 'outputs'))
    candidates.append(repo_relative)

    # 4) Also try a few other reasonable climbs (in case of different layout)
    cur = base
    for _ in range(4):
        cur = os.path.dirname(cur)
        candidates.append(os.path.abspath(os.path.join(cur, 'orchestrator', 'outputs')))

    # Return the first existing path, else return the primary repo_relative as default
    for c in candidates:
        try:
            if os.path.exists(c) and os.path.isdir(c):
                return c
        except Exception:
            continue

    # If nothing exists, return the repo_relative candidate (useful for messages and writing files)
    return repo_relative


def get_run_config():
    """Attempt to load orchestrator run config (orchestrator/inputs/config.json).

    Uses the same repo-relative logic as get_outputs_dir to find the project root and then
    loads inputs/config.json when available. Returns a dict (empty if not found/invalid).
    """
    # Try to locate the orchestrator/inputs/config.json relative to this file (repo-relative)
    base = os.path.dirname(__file__)
    # climb to pixely_stable then to orchestrator/inputs
    candidate = os.path.abspath(os.path.join(base, '..', '..', '..', '..', 'orchestrator', 'inputs', 'config.json'))

    try:
        if os.path.exists(candidate):
            import json as _json
            with open(candidate, 'r', encoding='utf-8') as fh:
                return _json.load(fh)
    except Exception:
        # Fail silently and return empty dict; views will treat missing key as False
        return {}

    # fallback: try a few parent climbs
    cur = base
    for _ in range(4):
        cur = os.path.dirname(cur)
        alt = os.path.abspath(os.path.join(cur, 'orchestrator', 'inputs', 'config.json'))
        try:
            if os.path.exists(alt):
                import json as _json
                with open(alt, 'r', encoding='utf-8') as fh:
                    return _json.load(fh)
        except Exception:
            continue

    return {}
