"""
For each site:
  * generate bash script to run rucio-register and launch transfers
  * run bps submitcmd for that batch script
"""
import os
from pathlib import Path
from dataclasses import dataclass
import yaml


@dataclass
class SiteInfo:
    name: str
    repo: str
    rucio_rse: str
    scope: str
    rse_root: str
    dtn_url: str
    tract: int
    collection: str = ""


_CONFIG_DIR = Path(os.environ['MULTISITE_TESTS_DIR']) / 'config'

TRANSFER_TEMPLATE = (_CONFIG_DIR / "rucio_transfer_template.bash").read_text(encoding="utf-8")

# Load the site info at file scope for now.
site_config_file = _CONFIG_DIR / 'site_info.yaml'
with open(site_config_file) as fobj:
    data = yaml.safe_load(fobj)
SITE_INFO = {item['name']: SiteInfo(**item) for item in data['sites']}

def generate_rucio_move_script(src, dest, dstypes):
    dataset_type_list = ' '.join(dstypes)
    return TRANSFER_TEMPLATE.format(**locals())

dstypes = ["isolated_star", "isolated_star_association", "preliminary_visit_image"]

foo = generate_rucio_move_script(SITE_INFO['LANCS'], SITE_INFO['SLAC'], dstypes)
