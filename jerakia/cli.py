"""Jerakia command line utility"""
import sys
import os
import click
import yaml, json
from jerakia.render import render as template_render
from .client import Client


sys.path.insert(0, os.getcwd())


class InvalidDataFormat(Exception):
    """Invalid data exception"""
    pass


class InvalidInputData(Exception):
    """Invalid input data exception"""
    pass


class MalformedYAML(InvalidInputData):
    """Invalid YAML data exception"""
    pass


def merge_dicts(*dicts):
    """Merge dictionaries using standard lib"""
    result = {}
    for dictionary in dicts:
        result.update(dictionary)
    return result


@click.group()
@click.option('-T', '--token',
              envvar='JERAKIA_TOKEN',
              help='Authenticatoin token',
              default='NOTCONFIGURED',
              show_default=True)
@click.option('-P', '--port',
              default='9843',
              help='Jerakia server port',
              envvar='JERAKIA_PORT',
              show_default=True)
@click.option('-H', '--host',
              default='localhost',
              help='Jerakia server host',
              envvar='JERAKIA_HOST',
              show_default=True)
@click.option('--protocol',
              type=click.Choice(['http', 'https']),
              default='http',
              help='Connection protocol',
              envvar='JERAKIA_PROTOCOL',
              show_default=True)
@click.option('-m', '--metadata',
              help='Lookup metadata',
              required=False,
              multiple=True)
@click.option('-i', '--configfile',
              help='Path to Jerakia configuration file',
              type=click.Path(),
              default='$HOME/.jerakia/jerakia.yaml',
              show_default=True)
@click.pass_context
def main(ctx, token, port, host, protocol, metadata, configfile):
    """jerakia is a tool to perform hierarchical data lookups."""
    # Parse metadata options
    met = dict()
    for item in metadata:
        met.update([item.split('=')])
    # Load configfile if exists
    if os.path.exists(configfile):
        with open(configfile, "r") as filename:
            config = yaml.load(filename, Loader=yaml.SafeLoader)
    # Merge dicts from cli args/env vars with config file
    else:
        config = dict()
    options_config = dict(token=token, port=port, host=host, version=1, protocol=protocol)
    combined_config = merge_dicts(config, options_config)

    ctx.ensure_object(dict)
    ctx.obj['client'] = Client(**combined_config)
    ctx.obj['metadata'] = met


@main.command('lookup')
@click.option('--output',
              type=click.Choice(['json', 'yaml']),
              default='json',
              help='Output format.',
              envvar='JERAKIA_OUTPUT',
              show_default=True)
@click.argument('namespace')
@click.argument('key', required=False, default=None)
@click.pass_context
def lookup(ctx, namespace, key, output):
    """Return data from Jerakia lookup"""
    namespaces = []
    namespaces.append(str(namespace))
    client = ctx.obj['client']
    metadata = ctx.obj['metadata']
    response = client.lookup(key=key,
                             namespace=namespaces,
                             metadata_dict=metadata,
                             content_type='json')

    try:
        if output == 'json':
            print(json.dumps(response['payload']))
        elif output == 'yaml':
            print(yaml.safe_dump(response['payload'], allow_unicode=True, explicit_start=True, default_flow_style=False))
    except Exception as detail:
            print('The Jerakia lookup resulted in an unknown response:', detail)


@main.command('render')
@click.option('-f', '--templatefile',
              type=click.Path(),
              help='Path to template file')
@click.option('-o', '--outputfile',
              type=click.Path(),
              help='Path to rendered file')
@click.pass_context
def render(ctx, templatefile, outputfile):
    """ Render Jinja2 template file with Jerakia as data source"""
    metadata = ctx.obj['metadata']
    rendered_data = template_render(templatefile,
                                    jerakia_instance=ctx.obj['client'],
                                    metadata_dict=metadata)

    if not outputfile:
        outputfile = templatefile.split('.j2')[0]

    with open(outputfile, 'w') as rendered_template:
        rendered_template.write(rendered_data)
