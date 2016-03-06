from jinja2 import Template, Environment

def render(body, data):
    tpl = Template(body, trim_blocks=True, lstrip_blocks=True)
    return tpl.render(data)
