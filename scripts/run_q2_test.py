import asyncio
import json
import os

from orchestrator.pipelines.social_media.analysis_modules.q2_personalidad import Q2Personalidad

async def main():
    project_root = os.path.dirname(os.path.dirname(__file__))
    outputs_dir = os.path.join(project_root, 'orchestrator', 'outputs')
    os.makedirs(outputs_dir, exist_ok=True)

    analyzer = Q2Personalidad(openai_client=None, config={"outputs_dir": outputs_dir})
    res = await analyzer.analyze()

    path = os.path.join(outputs_dir, 'q2_personalidad.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

    print('Wrote Q2 output to', path)

if __name__ == '__main__':
    asyncio.run(main())
