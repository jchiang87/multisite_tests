# Find visits with boresight pointings with in 1.7 deg
# of the mean position of tracts 7040, 7041, 7276, 7277
import pickle
import sqlite3
import numpy as np
import pandas as pd
import lsst.daf.butler as daf_butler

# Get the inital list of exposures based on DP2 deep_coadds
with open("det_visits.pickle", "rb") as fobj:
    det_visits = pickle.load(fobj)
exposures = sorted(set([int(_[0]) for _ in det_visits]))

condition = f"where observationId >= {exposures[0]} and observationId <= {exposures[-1]}"
print(condition)

repo = "dp2_prep"
collections = ["u/jchiang/multisite_test/w_2026_45"]

butler = daf_butler.Butler(repo, collections=collections)

skymap = butler.get("skyMap", skymap='lsst_cells_v2')

tracts = (7040, 7041, 7276, 7277)

ras, decs = [], []
for tract in tracts:
    coord = skymap[tract].getCtrCoord()
    ras.append(coord.getLongitude().asDegrees())
    decs.append(coord.getLatitude().asDegrees())

ra0 = np.mean(ras)
dec0 = np.mean(decs)

print(ra0, dec0)

with sqlite3.connect("dp2_visits_fixed.db") as con:
    df0 = pd.read_sql(f"select observationId, fieldRA, fieldDec, band from observations {condition}", con)
    df0 = df0[df0['observationId'].isin(exposures)]

df0['offset'] = np.sqrt(  (df0['fieldDec'] - dec0)**2
                        + (np.cos(np.pi*df0['fieldDec'])*(df0['fieldRA'] - ra0))**2 )
df0 = df0.sort_values("offset")

print(len(df0))

visits = []
for band in "ugrizy":
    df = df0.query(f"band=='{band}'")
    if len(df) > 45:
        df = df.query("offset < 1.0")
    elif len(df) > 20:
        df = df.query("offset < 1.7")
    print(band, len(df))
    visits.extend(df['observationId'])
#
#    visit_list = " ".join(str(_) for _ in sorted(df['observationId']))
#    print(band)
#    print(visit_list)
#    print()
print(np.array(visits))
