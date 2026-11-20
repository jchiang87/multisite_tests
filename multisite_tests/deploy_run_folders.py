import os
import glob
from pathlib import Path
import click
from .rucio_registration import get_site_info


_PKG_DIR = Path(os.environ['MULTISITE_TESTS_DIR'])


def deploy_bps_folder(site_dir, site, weekly, tract):
    bps_dir = site_dir / "bps"
    os.makedirs(bps_dir, exist_ok=True)
    bps_files = sorted(glob.glob(str(_PKG_DIR / "bps/bps*yaml")))
    for bps_file in bps_files:
        os.symlink(bps_file, bps_dir / os.path.basename(bps_file))
    baseline_template = ( (_PKG_DIR / "config/bps_baseline.yaml")
                          .read_text(encoding="utf-8") )
    output = ( baseline_template.replace("{WEEKLY}", weekly)
               .replace("{TRACT}", str(tract))
               .replace("{SITE}", site) )
    with open(bps_dir / "bps_baseline.yaml", "w") as fobj:
        fobj.write(output)


@click.group()
def cli():
    """Script to create site-specific run sub-folders"""
    pass


@cli.command("deploy",
             help="Deploy sub-folders for running at designated sites.")
@click.argument("site",
                type=click.Choice(["ALL", "IN2P3", "LANCS", "RAL", "SLAC"]))
@click.option("--weekly", required=True, envvar="WEEKLY",
              help="lsst_distrib weekly version")
@click.option("--dest-dir", default='.',
              help="top-level directory for sub-folders")
@click.option("--site-config-file", default=None, type=click.Path(exists=True),
              help="site config file")
def deploy(site, weekly, dest_dir, site_config_file):
    if site == "ALL":
        sites = ["IN2P3", "LANCS", "RAL", "SLAC"]
    else:
        sites = [site]

    site_info = get_site_info(site_config_file=site_config_file, weekly=weekly)
    for site in sites:
        tract = str(site_info[site].tract)
        site_dir = Path(dest_dir) / site
        if os.path.isdir(site):
            continue
        os.makedirs(site_dir, exist_ok=True)
        deploy_bps_folder(site_dir, site, weekly, tract)


@cli.command("update",
             help="Update bps subfolders with current bps yamls.")
@click.argument("site",
                type=click.Choice(["ALL", "IN2P3", "LANCS", "RAL", "SLAC"]))
@click.option("--weekly", required=True, envvar="WEEKLY",
              help="lsst_distrib weekly version")
@click.option("--dest-dir", default='.',
              help="top-level directory for sub-folders")
@click.option("--site-config-file", default=None, type=click.Path(exists=True),
              help="site config file")
def update(site, weekly, dest_dir, site_config_file):
    if site == "ALL":
        sites = ["IN2P3", "LANCS", "RAL", "SLAC"]
    else:
        sites = [site]
    site_info = get_site_info(site_config_file=site_config_file, weekly=weekly)
    for site in sites:
        tract = str(site_info[site].tract)
        site_dir = Path(dest_dir) / site
        if not os.path.isdir(site_dir):
            raise RuntimeError(f"{site_dir} does not exist")
        # Clear out bps sub-folder, make new symlinks and bps_baseline.yaml.
        for item in glob.glob(str(site_dir / "bps/bps*.yaml")):
            os.remove(item)
        deploy_bps_folder(site_dir, site, weekly, tract)


def main():
    cli()
