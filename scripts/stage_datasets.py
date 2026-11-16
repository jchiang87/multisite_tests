import os
from collections import defaultdict
from pathlib import Path
import warnings
import lsst.daf.butler as daf_butler
from lsst.pipe.base import Pipeline

repo = "dp2_prep"
butler = daf_butler.Butler(repo)
pipeline_yaml = (Path(os.environ["DRP_PIPE_DIR"]) / "pipelines"
                 / "LSSTCam" / "DRP.yaml")
pipeline = Pipeline.from_uri(pipeline_yaml)

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    pg = pipeline.to_graph(registry=butler.registry)

inputs = defaultdict(set)
outputs = defaultdict(set)
stages = [_ for _ in pg.task_subsets if _.startswith('stage')]
for stage in stages:
    stage_name = stage.split('-')[0]
    for task in pg.task_subsets[stage]:
        inputs[stage_name].update(pg.inputs_of(task))
        outputs[stage_name].update(pg.outputs_of(task))
inputs = dict(inputs)
outputs = dict(outputs)

print("inputs to stage 2 from stage 1:")
for item in sorted(outputs['stage1'].intersection(inputs['stage2'])):
    print(f"- {item}")
print()

print("inputs to stages 3 and 4 from stage 2:")
items = outputs['stage2'].intersection(inputs['stage3'])
items.update(outputs['stage2'].intersection(inputs['stage4']))
for item in sorted(items):
    print(f"- {item}")
print()
