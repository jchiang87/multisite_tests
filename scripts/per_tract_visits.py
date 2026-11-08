from collections import defaultdict
from itertools import pairwise
import pickle
import multiprocessing
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import pandas as pd
import lsst.daf.butler as daf_butler


def get_det_visits(refs, disable_progress=True):
    det_visits = set()
    for ref in tqdm(refs, disable=disable_progress):
        dc = butler.get(ref)
        for row in dc.provenance.contributions:
            det_visits.add((row['visit'], row['detector']))

    data = defaultdict(list)
    for visit, detector in det_visits:
        data['visit'].append(visit)
        data['detector'].append(detector)
    return pd.DataFrame(data).sort_values('visit')


#repo = 'dp2'
#collections = ["dp2"]
#dstype = 'deep_coadd'
#
#butler = daf_butler.Butler(repo, collections=collections)
#
#tracts = (7040, 7041, 7276, 7277)
#
#processes = 20
#
#det_visit_dfs = []
#for tract in tracts:
#    print(tract, flush=True)
#    where = f"tract in ({tract})"
#    refs = butler.query_datasets("deep_coadd", where=where)
#    assert len(refs) == 600
#
#    indexes = np.linspace(0, len(refs), processes + 1, dtype=int)
#    with multiprocessing.Pool(processes=processes) as pool:
#        workers = []
#        for imin, imax in pairwise(indexes):
#            disable_progress = (imin != 0)
#            workers.append(
#                pool.apply_async(get_det_visits, (refs[imin:imax],),
#                                 {'disable_progress': disable_progress})
#            )
#        pool.close()
#        pool.join()
#        dfs = [worker.get() for worker in workers]
#    df = pd.concat(dfs)
#    df['tract'] = tract
#    det_visit_dfs.append(df)
#
#df0 = pd.concat(det_visit_dfs)
#
#df0.to_parquet("det_visits_per_tract.parquet")


df0 = pd.read_parquet("det_visits_per_tract.parquet")

exposures = [2025060400350, 2025060400354, 2025060400378, 2025060400385, 2025060400394, 2025060400395, 2025060400421, 2025060400422, 2025060800477, 2025060800481, 2025060800484, 2025060800505, 2025060800506, 2025060800512, 2025060800519, 2025060800526, 2025060800533, 2025060800561, 2025060800568, 2025060900544, 2025060900548, 2025060900572, 2025060900586, 2025060900593, 2025060900600, 2025060900626, 2025060900637, 2025060900640, 2025062000436, 2025062000484, 2025063000571, 2025070300427, 2025070400440, 2025070400441, 2025070400488, 2025070400489, 2025070600481, 2025070600482, 2025070600483, 2025070700252, 2025070700300, 2025070700317, 2025070700318, 2025070700365, 2025070700366, 2025070800194, 2025070800196, 2025070800242, 2025070800244, 2025070900485, 2025070900766, 2025070900767, 2025070900782, 2025071800218, 2025071800220, 2025071800258, 2025071800283, 2025071800289, 2025071800474, 2025071800478, 2025071800486, 2025071800487, 2025071900428, 2025071900429, 2025071900430, 2025071900431, 2025071900432, 2025071900622, 2025072100602, 2025072200256, 2025072200257, 2025072200258, 2025072300339, 2025072300340, 2025072800427, 2025072800475, 2025081000510, 2025081300351, 2025081300353, 2025081300376, 2025081600288, 2025081600289, 2025081600341, 2025081600503, 2025082700334, 2025090200248, 2025090200261, 2025090200272, 2025090200279, 2025090200293, 2025090200324, 2025092100029, 2025092100034, 2025092100105, 2025092100144]

tracts = sorted(set(df0['tract']))
for tract in tracts:
    df = df0.query(f"tract == {tract}")
    df = df[df['visit'].isin(exposures)]
    print(tract, len(set(df['visit'])))
