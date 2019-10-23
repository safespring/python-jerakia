import sys
import os
import collections
import errno
import subprocess
import six
import click
from os import walk
from .client import Client,ClientError
from jerakia.render import render as template_render
from pkg_resources import iter_entry_points
from click_plugins import with_plugins
from distutils import dir_util # https://github.com/PyCQA/pylint/issues/73; pylint: disable=no-name-in-module

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

def get_format(fmt):
    """Returns a data loading function"""
    try:
        return FORMATS[fmt]()
    except ImportError:
        raise InvalidDataFormat(fmt)

def _load_yaml():
    import yaml
    return yaml.load, yaml.YAMLError, MalformedYAML

def merge_dicts(*dicts):
    result = {}
    for dictionary in dicts:
        result.update(dictionary)
    return result

FORMATS = {
    'yaml': _load_yaml,
    'yml': _load_yaml,
}

@click.group()
@click.option('-T','--token', envvar='JERAKIA_TOKEN')
@click.option('-P','--port', default='9843', envvar='JERAKIA_PORT')
@click.option('-H','--host', default='localhost', envvar='JERAKIA_HOST')
@click.option('--protocol', default='http', envvar='JERAKIA_PROTOCOL')
@click.option('-t','--type')
@click.option('-p','--policy')
@click.option('-m','--metadata',required=False, multiple=True)
@click.option('-i', '--configfile', type=click.Path(), default='$HOME/.jerakia/jerakia.yaml')
@click.pass_context
def main(ctx, token, port, host, protocol, type, policy, metadata, configfile):
    """jerakia is a tool to perform hierarchical data lookups."""
    # Parse metadata options
    met = dict()
    for item in metadata:
        met.update([item.split('=')])
    # Load configfile if exists
    if os.path.exists(configfile):
        with open(configfile, "r") as filename:
            config = yaml.load(filename)
    # Merge dicts from cli args/env vars with config file
    else:
        config  = dict()
    options_config = dict(token=token,port=port,host=host,version=1,protocol=protocol)
    combined_config = merge_dicts(config,options_config)

    ctx.ensure_object(dict)
    ctx.obj['client'] = Client(**combined_config)
    ctx.obj['metadata'] = met


@main.command('lookup')
@click.argument('namespace')
@click.argument('key')
@click.pass_context
def lookup(ctx, namespace, key):
    ret = []
    ns = []
    ns.append(str(namespace))
    client = ctx.obj['client']
    metadata = ctx.obj['metadata']
    response =client.lookup(key=str(key), namespace=ns, metadata_dict=metadata, content_type='json')
    ret.append(response['payload'])

    try:
        print("Result outputs ", ret)
    except Exception as detail:
        print('The Jerakia lookup resulted in an empty response:', detail)


@main.command('render')
@click.option('-f', '--templatefile', type=click.Path(), help='Path to template file')
@click.option('-o', '--outputfile', type=click.Path(), help='Path to rendered file')
@click.pass_context
def render(ctx, templatefile, outputfile):
    """ Render Jinja2 template file with Jerakia as data source"""
    metadata = ctx.obj['metadata']
    rendered_data = template_render(templatefile, jerakia_instance=ctx.obj['client'], metadata_dict=metadata, data={})

    if not outputfile:
        outputfile = templatefile.split('.j2')[0]

    with open(outputfile, 'w') as rendered_template:
        rendered_template.write(rendered_data)

