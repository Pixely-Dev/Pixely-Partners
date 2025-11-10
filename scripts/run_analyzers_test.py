import asyncio
import json
import os

# import a selection of analyzers to run for testing. Add more as implemented.
from orchestrator.pipelines.social_media.analysis_modules.q5_influenciadores import Q5Influenciadores
from orchestrator.pipelines.social_media.analysis_modules.q6_oportunidades import Q6Oportunidades
from orchestrator.pipelines.social_media.analysis_modules.q11_engagement import Q11Engagement
from orchestrator.pipelines.social_media.analysis_modules.q12_comunidad import Q12Comunidad
from orchestrator.pipelines.social_media.analysis_modules.q13_frecuencia import Q13Frecuencia
from orchestrator.pipelines.social_media.analysis_modules.q17_sentimiento_agrupado import Q17SentimientoAgrupado
from orchestrator.pipelines.social_media.analysis_modules.q20_kpi_global import Q20KpiGlobal


async def run_one(analyzer_cls, outputs_dir):
    analyzer = analyzer_cls(openai_client=None, config={"outputs_dir": outputs_dir})
    res = await analyzer.analyze()
    return res


async def main():
    project_root = os.path.dirname(os.path.dirname(__file__))
    outputs_dir = os.path.join(project_root, 'orchestrator', 'outputs')
    os.makedirs(outputs_dir, exist_ok=True)

    analyzers = {
        'q5': Q5Influenciadores,
        'q6': Q6Oportunidades,
        'q11': Q11Engagement,
        'q12': Q12Comunidad,
        'q13': Q13Frecuencia,
        # 'q16': Q16Benchmark,  # DISABLED: Q16 commented out per single-client mode
        'q17': Q17SentimientoAgrupado,
        'q20': Q20KpiGlobal,
    }

    results = {}
    for key, cls in analyzers.items():
        try:
            results[key] = await run_one(cls, outputs_dir)
        except Exception as e:
            results[key] = {"error": str(e)}

    # write outputs
    for key, res in results.items():
        path = os.path.join(outputs_dir, f"{key}_test_output.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=2)

    print('Wrote test outputs to', outputs_dir)


if __name__ == '__main__':
    asyncio.run(main())
