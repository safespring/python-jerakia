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
@click.option('-c', '--config-file',
              help='Path to Jerakia configuration file',
              type=click.Path(),
              default='$HOME/.jerakia/jerakia.yaml',
              show_default=True)
@click.pass_context
def main(ctx, token, port, host, protocol, config_file):
    """jerakia is a tool to perform hierarchical data lookups."""
    # Load configfile if exists
    if os.path.exists(config_file):
        with open(config_file, "r") as filename:
            config = yaml.load(filename, Loader=yaml.SafeLoader)
    # Merge dicts from cli args/env vars with config file
    else:
        config = dict()
    options_config = dict(token=token, port=port, host=host, version=1, protocol=protocol)
    combined_config = merge_dicts(config, options_config)

    ctx.ensure_object(dict)
    ctx.obj['client'] = Client(**combined_config)
    ctx.obj['metadata'] = dict()


@main.command('lookup')
@click.option('-m', '--metadata',
              help='Lookup metadata',
              required=False,
              multiple=True)
@click.option('-o','--output-format',
              type=click.Choice(['json', 'yaml']),
              default='json',
              help='Output format.',
              envvar='JERAKIA_OUTPUT',
              show_default=True)
@click.argument('namespace')
@click.argument('key', required=False, default=None)
@click.pass_context
def lookup(ctx, metadata, namespace, key, output_format):
    """Return data from Jerakia lookup"""
    namespaces = []
    namespaces.append(str(namespace))
    client = ctx.obj['client']
    for item in metadata:
        ctx.obj['metadata'].update([item.split('=')])
    metadata = ctx.obj['metadata']
    response = client.lookup(key=key,
                             namespace=namespaces,
                             metadata_dict=metadata,
                             content_type='json')

    data = response['payload']
    if output_format == 'json':
        out = json.dumps(data)
    elif output_format == 'yaml':
        out = yaml.safe_dump(data, encoding=None, allow_unicode=True, default_flow_style=False)
        # remove any trailing newline and document end outputs caused by safe_dump
        out = out.rstrip().rstrip('...\n')
    print(out)


@main.command('template')
@click.option('-m', '--metadata',
              help='Lookup metadata',
              required=False,
              multiple=True)
@click.option('-o', '--output-file',
              type=click.Path(),
              help='Path to rendered file')
@click.argument('template_file')
@click.pass_context
def template(ctx, metadata, template_file, output_file):
    """ Render Jinja2 template file with Jerakia as data source"""
    for item in metadata:
        ctx.obj['metadata'].update([item.split('=')])
    metadata = ctx.obj['metadata']
    rendered_data = template_render(template_file,
                                    jerakia_instance=ctx.obj['client'],
                                    metadata_dict=metadata)

    if not output_file:
        output_file = template_file.split('.j2')[0]
    with open(output_file, 'w') as rendered_template:
        rendered_template.write(rendered_data)
