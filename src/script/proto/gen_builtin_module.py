from jinja2 import Template


TPL_SETUP_HEADER = """
def setup(process, module, stdlib):
    _module = space.newemptyenv(space.newsymbol(process, u'{{module_name}}'))
"""

TPL_INSTALL_FUNC = "    api.put_native_function(process, _module, u'{{func_name}}', {{func_native_name}}, {{func_arity}})"
TPL_FOOTER = """
    process.modules.add_module('{{module_name}}', _module)
"""

TPL_FUNC = """
@complete_native_routine
def {{func_native_name}}(process, routine):
    {% for arg in args %}{{arg.name}} = routine.get_arg({{arg.index}}) 
    {% endfor %}
    {%if  result_wrap == ''  %}return {{source_module}}.{{source_function}}({% for arg in args|sort(attribute='source_index') %}{{arg.name}}{% if not loop.last %}, {% endif %}{% endfor %})
    {% else %}return {{result_wrap}}({{source_module}}.{{source_function}}({% for arg in args|sort(attribute='source_index') %}{{arg.name}}{% if not loop.last %}, {% endif %}{% endfor %})){% endif %}
"""

def render(body, data):
    tpl = Template(body)
    return tpl.render(data)

def generate(module):
    result = []
    result.append(render(TPL_SETUP_HEADER, module))
    for func in module["funcs"]:
        result.append(render(TPL_INSTALL_FUNC, func))
    

    result.append(render(TPL_FOOTER, module))


    for func in module["funcs"]:
        result.append(render(TPL_FUNC, func))


    data = "\n".join(result)
    return data

def args(arity):
    return [arg(i) for i in range(arity)]

def arg(index):
    return {
        "name":"arg%d" % index,
        "index": index,
        "source_index": index,

    }

def func(func_name=None, func_native_name=None,
         func_arity=None, source_module=None,
        source_function=None, result_wrap=''):
    return dict(
        func_name=func_name,
        func_native_name=func_native_name,
        func_arity=func_arity,
        source_module = source_module,
        source_function=source_function if source_function else func_name,
        result_wrap = result_wrap,
        args = args(func_arity)
        )


def module(module_name, funcs):
    return dict(
        module_name = module_name,
        funcs=funcs
    )

LISTS = module("_lists", [
    func(func_name="tail", func_native_name="_tail", func_arity=1,
             source_module="plist", source_function="tail"),
    func(func_name="empty", func_native_name="_empty", func_arity=0,
             source_module="plist", source_function="empty"),
    func(func_name="is_empty", func_native_name="_is_empty", func_arity=1,
             source_module="plist", source_function="is_empty", result_wrap="space.newbool"),
    func(func_name="head", func_native_name="_head", func_arity=1,
             source_module="plist", source_function="head"),
    func(func_name="cons", func_native_name="_cons", func_arity=2,
             source_module="plist", source_function="cons"),
    ])

print generate(LISTS)