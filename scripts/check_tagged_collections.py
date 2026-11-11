from collections import defaultdict
import pandas as pd
import lsst.daf.butler as daf_butler

repo = "dp2_prep"
butler = daf_butler.Butler(repo)

tracts = (7040, 7041, 7276, 7277)

for tract in tracts:
    collection = f"LSSTCam/raw/20250604-20250921/SV_320_15/DM-57008/{tract}"
    refs = butler.query_datasets("raw", collections=[collection])
    data = defaultdict(list)
    for ref in refs:
        for col in ("exposure", "detector"):
            data[col].append(ref.dataId[col])
    df0 = pd.DataFrame(data)
    print(tract, len(set(df0['exposure'])), len(df0))

