import click
from .cli.kernelpatcher import kernelpatcher
from .cli.asrpatcher import asrpatcher

@click.group()
def cli():
    pass
   
cli.add_command(kernelpatcher)
cli.add_command(asrpatcher)

cli.context_settings = dict(help_option_names=['-h', '--help'])

cli()