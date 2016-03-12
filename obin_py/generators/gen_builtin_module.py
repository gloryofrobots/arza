from jinja2 import Template


TPL_SETUP_HEADER = """
def setup(process, stdlib):
    _module_name = space.newsymbol(process, u'{{module_name}}')
    _module = space.newemptyenv(_module_name)
"""

TPL_INSTALL_FUNC = "    api.put_native_function(process, _module, u'{{func_name}}', {{func_native_name}}, {{func_arity}})"
TPL_FOOTER = """
    _module.export_all()
    process.modules.add_module(_module_name, _module)
"""

TPL_FUNC = """
@complete_native_routine
def {{func_native_name}}(process, routine):
    {% for arg in args %}{{arg.name}} = routine.get_arg({{arg.index}}) {%if  affirm_type != ''  %} 
    error.affirm_type({{arg.name}}, {{affirm_type}}) {% endif %}
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
    return [arg(i, i) for i in range(arity)]

def arg(index, source_index):
    return {
        "name":"arg%d" % index,
        "index": index,
        "source_index": source_index,

    }

def func(func_name=None, func_native_name=None,
         func_arity=None, source_module=None,
        source_function=None, result_wrap='', affirm_type='', arguments=None):
    return dict(
        func_name=func_name,
        func_native_name=func_native_name,
        func_arity=func_arity,
        source_module = source_module,
        source_function=source_function if source_function else func_name,
        result_wrap = result_wrap,
        affirm_type = affirm_type,
        args = args(func_arity) if arguments is None else arguments
        )


def module(module_name, funcs):
    return dict(
        module_name = module_name,
        funcs=funcs
    )

LISTS = module("obin:lang:list", [
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
    func(func_name="slice", func_native_name="_slice", func_arity=2,
             source_module="plist", source_function="slice",
            arguments=[arg(2,0), arg(1,1), arg(0, 0)]),
    ])

TUPLES = module("obin:lang:tuple", [
    func(func_name="length", func_native_name="_length", func_arity=1,
             source_module="api", source_function="length"),
    func(func_name="to_list", func_native_name="_to_list", func_arity=1,
             source_module="tuples", source_function="to_list"),
    ])

BIT = module("_bit",  [
    func(func_name="bitnot", func_native_name="bitnot", func_arity=1,
             source_module="number", source_function="bitnot_i",
                affirm_type='space.isint'),

    func(func_name="bitor", func_native_name="bitor", func_arity=2,
             source_module="number", source_function="bitor_i_i",
                affirm_type='space.isint'),

    
    func(func_name="bitxor", func_native_name="bitxor", func_arity=2,
             source_module="number", source_function="bitxor_i_i",
                affirm_type='space.isint'),



    func(func_name="bitand", func_native_name="bitand", func_arity=2,
             source_module="number", source_function="bitand_i_i",
                affirm_type='space.isint'),


    func(func_name="lshift", func_native_name="lshift", func_arity=2,
             source_module="number", source_function="lsh_i_i",
                affirm_type='space.isint'),

    func(func_name="rshift", func_native_name="rshift", func_arity=2,
             source_module="number", source_function="rsh_i_i",
              affirm_type='space.isint'),

    ])


print generate(TUPLES)
# print generate(BIT)





