from collections import defaultdict
from itertools import pairwise
import pickle
import multiprocessing
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import pandas as pd
import lsst.daf.butler as daf_butler

repo = 'dp2'
collections = ["dp2"]
dstype = 'deep_coadd'

butler = daf_butler.Butler(repo, collections=collections)

#skymap = butler.get('skyMap', skymap='lsst_cells_v2')
#
#refs = butler.query_datasets(dstype, limit=None)
#
#print(len(refs))
#
#data = defaultdict(list)
#for ref in tqdm(refs):
#    for dim in ('band', 'tract', 'patch'):
#        data[dim].append(ref.dataId[dim])
#df0 = pd.DataFrame(data)
#
#tracts = sorted(set(df0['tract']))
#
#data = defaultdict(list)
#for tract in tracts:
#    tract_info = skymap[tract]
#    coord =  tract_info.getCtrCoord()
#    data['ra'].append(coord.getLongitude().asDegrees())
#    data['dec'].append(coord.getLatitude().asDegrees())
#    data['tract'].append(tract)
#df1 = pd.DataFrame(data)
#
#plt.ion()
#
#fignum = 1
#plt.figure(fignum)
#if plt.fignum_exists(fignum):
#    plt.clf()
#
#plt.scatter(df1['ra'], df1['dec'], s=4)
#
#ra0, dec0 = 319.5, -15.0
#
#df1['offset'] = np.sqrt((ra0 - df1['ra'])**2 + (dec0 - df1['dec'])**2)
#df1 = df1.sort_values('offset', ascending=True)
#
#df2 = df1.head(4)
#
#plt.scatter(df2['ra'], df2['dec'], color='red', s=4)
#
#"""
#In [31]: df2
#Out[31]:
#              ra        dec  tract    offset
#1074  320.000000 -15.619835   7041  0.796364
#1158  318.813559 -14.132231   7276  1.106446
#1159  320.338983 -14.132231   7277  1.207027
#1073  318.461538 -15.619835   7040  1.209379
#"""

where = "tract in (7040, 7041, 7276, 7277)"
refs = butler.query_datasets(dstype, where=where)

def get_det_visits(refs, disable_progress=True):
    det_visits = set()
    for ref in tqdm(refs, disable=disable_progress):
        dc = butler.get(ref)
        for row in dc.provenance.contributions:
            det_visits.add((row['visit'], row['detector']))

    return det_visits


processes = 20
indexes = np.linspace(0, len(refs), processes + 1, dtype=int)
print(indexes)
with multiprocessing.Pool(processes=processes) as pool:
    workers = []
    for imin, imax in pairwise(indexes):
        disable_progress = (imin != 0)
        workers.append(pool.apply_async(get_det_visits, (refs[imin:imax],),
                                        {'disable_progress': disable_progress}))
    pool.close()
    pool.join()
    det_visits = set()
    for worker in workers:
        det_visits.update(worker.get())

with open("det_visits.pickle", "wb") as fobj:
    pickle.dump(det_visits, fobj)
