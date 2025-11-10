import importlib
import os
import sys
import types

# ensure repo package imports work
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, repo_root)
# Also insert the frontend package root so imports like 'pipelines.social_media' resolve
frontend_pkg = os.path.abspath(os.path.join(repo_root, 'frontend'))
if os.path.isdir(frontend_pkg):
    sys.path.insert(0, frontend_pkg)

checks = [
    ('Q11','pipelines.social_media.view_components.qual.q11_engagement_view','display_q11_engagement','q11_engagement.json'),
    ('Q12','pipelines.social_media.view_components.quant.q12_view','display_q12_comunidad','q12_comunidad.json'),
    ('Q13','pipelines.social_media.view_components.quant.q13_view','display_q13_frecuencia','q13_frecuencia.json'),
    ('Q14','pipelines.social_media.view_components.quant.q14_view','display_q14_formatos','q14_formatos.json'),
    ('Q15','pipelines.social_media.view_components.quant.q15_view','display_q15_hashtags','q15_hashtags.json'),
    # ('Q16','pipelines.social_media.view_components.quant.q16_view','display_q16_benchmark','q16_benchmark.json'),  # DISABLED
    ('Q17','pipelines.social_media.view_components.qual.q17_view','display_q17_sentimiento_agrupado','q17_sentimiento_agrupado.json'),
    ('Q18','pipelines.social_media.view_components.quant.q18_view','display_q18_anomalias','q18_anomalias.json'),
    ('Q19','pipelines.social_media.view_components.quant.q19_view','display_q19_correlacion','q19_correlacion.json'),
    ('Q20','pipelines.social_media.view_components.quant.q20_view','display_q20_kpi_global','q20_kpi_global.json'),
]

out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'orchestrator', 'outputs'))
print('Using outputs_dir:', out_dir)
print()

# Create minimal dummy `streamlit` and `plotly` modules so view files import successfully in this environment
def _make_dummy_streamlit():
    m = types.ModuleType('streamlit')

    # dummy UI functions
    def _noop(*args, **kwargs):
        return None

    for fn in ['header','write','info','error','subheader','metric','bar_chart','line_chart','table','json','plotly_chart','caption','dataframe','markdown','title','set_page_config','warning']:
        setattr(m, fn, _noop)

    # columns returns context-managers
    class _DummyCol:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
        def __getattr__(self, item):
            return _noop

    def _columns(spec):
        # return two dummy columns for convenience
        return [_DummyCol(), _DummyCol()]

    def _selectbox(label, options, key=None):
        if isinstance(options, (list, tuple)) and options:
            return options[0]
        return None

    m.columns = _columns
    m.selectbox = _selectbox
    m.beta_columns = _columns

    return m

def _make_dummy_plotly():
    plotly = types.ModuleType('plotly')
    graph_objects = types.ModuleType('plotly.graph_objects')
    express = types.ModuleType('plotly.express')

    class DummyFig:
        def update_layout(self, *a, **k):
            return None

    def dummy_scatter(*a, **k):
        return DummyFig()

    express.scatter = dummy_scatter
    plotly.graph_objects = graph_objects
    plotly.express = express
    return plotly, graph_objects, express

# install fakes into sys.modules
sys.modules.setdefault('streamlit', _make_dummy_streamlit())
plotly_mod, go_mod, px_mod = _make_dummy_plotly()
sys.modules.setdefault('plotly', plotly_mod)
sys.modules.setdefault('plotly.graph_objects', go_mod)
sys.modules.setdefault('plotly.express', px_mod)

for name, mod, fn, jsonf in checks:
    try:
        m = importlib.import_module(mod)
        hasfn = hasattr(m, fn)
        print(f"{name}: module imported OK; function {'FOUND' if hasfn else 'MISSING'} -> {mod}.{fn}")
    except Exception as e:
        print(f"{name}: IMPORT ERROR -> {mod}: {e}")
    print('    json file exists:', os.path.exists(os.path.join(out_dir, jsonf)))

print('\nScript finished')
