import asyncio
import json
import os
from orchestrator.pipelines.social_media.analysis_modules.q1_emociones import Q1Emociones

async def main():
    project_root = os.path.dirname(os.path.dirname(__file__))
    outputs_dir = os.path.join(project_root, 'orchestrator', 'outputs')
    os.makedirs(outputs_dir, exist_ok=True)

    analyzer = Q1Emociones(openai_client=None, config={"outputs_dir": outputs_dir})
    res = await analyzer.analyze()

    path = os.path.join(outputs_dir, 'q1_emociones.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

    print('Wrote q1_emociones.json to', path)

if __name__ == '__main__':
    asyncio.run(main())
