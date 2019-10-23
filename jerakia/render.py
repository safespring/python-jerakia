"""
lib for rendering jinja templates using Jerakia lookups
"""
import os
from jinja2 import Environment, FileSystemLoader


def dolookup(jerakia_client, metadata, item):
    """Retrieves the result from the Jerakia lookup"""
    namespace, key = item.split('/')
    response = jerakia_client.lookup(key=key,
                                     namespace=namespace,
                                     metadata_dict=metadata,
                                     content_type='json')
    return response['payload']


def render(template_path, jerakia_instance, metadata_dict, extensions=None, strict=False):
    """Renders a jinja2 template using data looked up via Jerakia"""
    extensions = extensions if extensions else []
    env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)),
                      extensions=extensions,
                      keep_trailing_newline=True)
    if strict:
        from jinja2 import StrictUndefined
        env.undefined = StrictUndefined

    def lookup_tag(item):
        """ Wrapper function around doLookup with fixed jerakia_client
        and metadata values. Used for looking up data in templates."""
        return dolookup(jerakia_instance, metadata_dict, item)

    env.globals['environ'] = os.environ.get
    env.globals['jerakia'] = lookup_tag

    output = env.get_template(os.path.basename(template_path)).render()
    return output
