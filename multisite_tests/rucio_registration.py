import os
from pathlib import Path
from dataclasses import dataclass
import yaml
import click


__all__ = ["SiteInfo", "read_site_config", "get_site_info",
           "generate_rucio_scripts"]


_CONFIG_DIR = Path(os.environ['MULTISITE_TESTS_DIR']) / 'config'


@dataclass
class SiteInfo:
    name: str
    repo: str
    rucio_rse: str
    scope: str
    rse_root: str
    dtn_url: str
    tract: int
    collection_template: str
    weekly: str = ""
    ticket: str = ""

    @property
    def collection(self):
        vars = {"WEEKLY": self.weekly, "TICKET": self.ticket}
        return self.collection_template.format(**vars)


def read_site_config(section, site_config_file=None):
    if site_config_file is None:
        site_config_file = _CONFIG_DIR / 'site_info.yaml'
    with open(site_config_file) as fobj:
        site_config = yaml.safe_load(fobj)
    return site_config[section]


def get_site_info(site_config_file=None, weekly=None, ticket=None):
    site_config = read_site_config('sites', site_config_file=site_config_file)
    site_info = {item['name']: SiteInfo(**item) for item in site_config}
    if weekly is not None:
        for mapping in site_info.values():
            mapping.weekly = weekly
    if ticket is not None:
        for mapping in site_info.values():
            mapping.ticket = ticket
    return site_info


@click.group()
def cli():
    """Create scripts to transfer DRP datasets"""
    pass


@cli.command("generate")
@click.argument("src_site")
@click.argument("dest_site")
@click.option("--dstype-config", required=True,
              help="Config entry for dstypes to transfer")
@click.option("--weekly", required=True, envvar="WEEKLY",
              help="lsst_distrib weekly version")
@click.option("--ticket", required=True, envvar="TICKET",
              help="JIRA ticket number, e.g., 'DM-57008'")
@click.option("--site-config-file", default=None, type=click.Path(exists=True),
              help="site config file")
def generate_rucio_scripts(src_site, dest_site, dstype_config,
                           weekly, ticket, site_config_file=None):
    # Generate shell script.
    dstypes = read_site_config(
        'dstypes', site_config_file=site_config_file)[dstype_config]
    template = ( (_CONFIG_DIR / "rucio_transfer_template.bash")
                 .read_text(encoding="utf-8") )
    site_info = get_site_info(site_config_file=site_config_file, weekly=weekly,
                              ticket=ticket)
    src = site_info[src_site]
    dest = site_info[dest_site]
    dataset_type_list = ' '.join(dstypes)
    shell_script = f"{src_site}_to_{dest_site}_transfer.sh"
    with open(shell_script, "w") as fobj:
        fobj.write(template.format(**locals()))

    # Generate bps submitcmd yaml file.
    template = ( (_CONFIG_DIR / "remote_job_template.yaml")
                 .read_text(encoding="utf-8") )
    WEEKLY = weekly
    SITE = src.name
    BASH_SCRIPT = os.path.abspath(f"./{shell_script}")
    bps_configs = read_site_config('bps_configs',
                                   site_config_file=site_config_file)
    REQUEST_CPUS = bps_configs['requestCpus']
    REQUEST_MEMORY = bps_configs['requestMemory']
    PAYLOAD_NAME = shell_script[:-len(".sh")]
    yaml_file = f"{src_site}_to_{dest_site}_transfer.yaml"
    with open(yaml_file, "w") as fobj:
        fobj.write(template.format(**locals()))

def main():
    cli()
