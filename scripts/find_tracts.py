import lsst.geom
import lsst.daf.butler as daf_butler

repo = "dp2_prep"
collections = ["LSSTCam/defaults"]

butler = daf_butler.Butler(repo, collections=collections)

skymap = butler.get('skyMap', skymap='lsst_cells_v2')

ra = lsst.geom.Angle(348.0, lsst.geom.degrees)
dec = lsst.geom.Angle(-10.0, lsst.geom.degrees)

sky_pos = lsst.geom.SpherePoint(ra, dec)

tract_info = skymap.findTract(sky_pos)

"""
In [7]: skymap.findTract(sky_pos)
Out[7]: TractInfo(id=8011, ctrCoord=[0.9642513030564377, -0.20495794156351452, -0.1679632898701648])
8011, 8010
7838, 7837
"""
