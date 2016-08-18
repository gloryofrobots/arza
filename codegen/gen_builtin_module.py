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
    {% for arg in args %}{{arg.name}} =
        {%-if  arg.wrapper == ''  -%} routine.get_arg({{arg.index}}) {% else %} {{arg.wrapper}}(routine.get_arg({{arg.index}})) {% endif%}
    {%if  affirm_type != ''  -%} error.affirm_type({{arg.name}}, {{affirm_type}}) {% endif %}
    {% endfor %}
    {%if  result_wrap == ''  %}return {{source_module}}.{{source_function}}({% if process != '' %}process,{%endif%}{% for arg in args|sort(attribute='source_index') %}{{arg.name}}{% if not loop.last %}, {% endif %}{% endfor %})
    {% else %}return {{result_wrap}}({{source_module}}.{{source_function}}({% if process != '' %}process,{%endif%}{% for arg in args|sort(attribute='source_index') %}{{arg.name}}{% if not loop.last %}, {% endif %}{% endfor %})){% endif %}
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

def arg(index, source_index, wrapper=''):
    return {
        "name":"arg%d" % index,
        "index": index,
        "source_index": source_index,
        "wrapper":wrapper
    }

def func(func_name=None, func_native_name=None,
         func_arity=None, source_module=None,
        source_function=None, result_wrap='', affirm_type='', arguments=None, process=''):
    return dict(
        func_name=func_name,
        func_native_name=func_native_name,
        func_arity=func_arity,
        source_module = source_module,
        source_function=source_function if source_function else func_name,
        result_wrap = result_wrap,
        affirm_type = affirm_type,
        args = args(func_arity) if arguments is None else arguments,
        process = process
        )


def module(module_name, funcs):
    return dict(
        module_name = module_name,
        funcs=funcs
    )

LIST = module("lalan:lang:_list", [
    func(func_name="length", func_native_name="length", func_arity=1,
             source_module="plist", source_function="length"),
    func(func_name="is_empty", func_native_name="_is_empty", func_arity=1,
             source_module="plist", source_function="is_empty", result_wrap="space.newbool"),

    func(func_name="empty", func_native_name="_empty", func_arity=0,
             source_module="plist", source_function="empty"),
    func(func_name="cons", func_native_name="_cons", func_arity=2,
             source_module="plist", source_function="cons"),
    func(func_name="head", func_native_name="_head", func_arity=1,
             source_module="plist", source_function="head"),
    func(func_name="tail", func_native_name="_tail", func_arity=1,
             source_module="plist", source_function="tail"),

    func(func_name="slice", func_native_name="slice", func_arity=3,
             source_module="plist", source_function="slice",
            arguments=[arg(2,0), arg(1,1, wrapper='api.to_i'), arg(0, 0, wrapper='api.to_i')]),
    func(func_name="take", func_native_name="take", func_arity=2,
             source_module="plist", source_function="take",
            arguments=[arg(1, 0), arg(0, 0, wrapper='api.to_i')]),
    func(func_name="drop", func_native_name="drop", func_arity=2,
             source_module="plist", source_function="drop",
            arguments=[arg(1, 0), arg(0, 0, wrapper='api.to_i')]),
    ])

TUPLES = module("lalan:lang:_tuple", [
    func(func_name="to_list", func_native_name="_to_list", func_arity=1,
             source_module="tuples", source_function="to_list"),

    func(func_name="slice", func_native_name="slice", func_arity=3,
             source_module="tuples", source_function="slice",
            arguments=[arg(2,0), arg(1,1, wrapper='api.to_i'), arg(0, 0, wrapper='api.to_i')]),

    func(func_name="take", func_native_name="take", func_arity=2,
             source_module="tuples", source_function="take",
            arguments=[arg(1, 0), arg(0, 0, wrapper='api.to_i')]),

    func(func_name="drop", func_native_name="drop", func_arity=2,
             source_module="tuples", source_function="drop",
            arguments=[arg(1, 0), arg(0, 0, wrapper='api.to_i')]),

    func(func_name="prepend", func_native_name="prepend", func_arity=2,
             source_module="tuples", source_function="prepend",
            arguments=[arg(1, 0), arg(0, 0)]),

    func(func_name="concat", func_native_name="concat", func_arity=2,
             source_module="tuples", source_function="concat",
            arguments=[arg(0, 1), arg(1, 1)]),
    ]
)

STRING = module("lalan:lang:_string", [

    func(func_name="to_list", func_native_name="to_list", func_arity=1,
             source_module="string", source_function="to_list"),

    func(func_name="reverse", func_native_name="reverse", func_arity=1,
             source_module="string", source_function="reverse"),

    func(func_name="slice", func_native_name="slice", func_arity=3,
             source_module="string", source_function="slice",
            arguments=[arg(2,0), arg(1,1, wrapper='api.to_i'), arg(0, 0, wrapper='api.to_i')]),
    func(func_name="take", func_native_name="take", func_arity=2,
             source_module="string", source_function="take",
            arguments=[arg(1, 0), arg(0, 0, wrapper='api.to_i')]),
    func(func_name="drop", func_native_name="drop", func_arity=2,
             source_module="string", source_function="drop",
            arguments=[arg(1, 0), arg(0, 0, wrapper='api.to_i')]),

    func(func_name="concat", func_native_name="concat", func_arity=2,
             source_module="string", source_function="concat",
            arguments=[arg(0, 0), arg(1, 0)]),

    func(func_name="append", func_native_name="append", func_arity=2,
             source_module="string", source_function="append",
            arguments=[arg(1, 0), arg(0, 0)]),

    func(func_name="prepend", func_native_name="prepend", func_arity=2,
             source_module="string", source_function="prepend",
            arguments=[arg(1, 0), arg(0, 0)]),

    func(func_name="split", func_native_name="split", func_arity=2,
             source_module="string", source_function="split",
            arguments=[arg(1, 0), arg(0, 0)]),


    func(func_name="replace", func_native_name="replace", func_arity=3,
             source_module="string", source_function="replace",
             arguments=[arg(2,0), arg(1,1), arg(0, 0)]),
    func(func_name="replace_first", func_native_name="replace_first", func_arity=3,
             source_module="string", source_function="replace_first",
             arguments=[arg(2,0), arg(1,1), arg(0, 0)]),
    ])


BIT = module("lalan:lang:_bit",  [
    func(func_name="bitnot", func_native_name="bitnot", func_arity=1,
             source_module="number", source_function="bitnot",
                affirm_type='space.isint'),

    func(func_name="bitor", func_native_name="bitor", func_arity=2,
             source_module="number", source_function="bitor",
                affirm_type='space.isint'),


    func(func_name="bitxor", func_native_name="bitxor", func_arity=2,
             source_module="number", source_function="bitxor",
                affirm_type='space.isint'),



    func(func_name="bitand", func_native_name="bitand", func_arity=2,
             source_module="number", source_function="bitand",
                affirm_type='space.isint'),


    func(func_name="lshift", func_native_name="lshift", func_arity=2,
             source_module="number", source_function="lsh",
                affirm_type='space.isint'),

    func(func_name="rshift", func_native_name="rshift", func_arity=2,
             source_module="number", source_function="rsh",
              affirm_type='space.isint'),

    ])


API = module("lalan:lang:_api", [
    func(func_name="length", func_native_name="length", func_arity=1,
             source_module="api", source_function="length"),
    func(func_name="is_empty", func_native_name="is_empty", func_arity=1,
             source_module="api", source_function="is_empty"),
    func(func_name="put", func_native_name="put", func_arity=3,
             source_module="api", source_function="put",
            arguments=[arg(2,0), arg(1,1), arg(0, 0)]),
    func(func_name="at", func_native_name="at", func_arity=2,
             source_module="api", source_function="at",
            arguments=[arg(1, 0), arg(0, 0)]),
    func(func_name="elem", func_native_name="elem", func_arity=2,
             source_module="api", source_function="contains",
            arguments=[arg(1, 0), arg(0, 0)]),
    func(func_name="del", func_native_name="delete", func_arity=2,
             source_module="api", source_function="delete",
            arguments=[arg(1, 0), arg(0, 0)]),
    func(func_name="equal", func_native_name="equal", func_arity=2,
             source_module="api", source_function="equal",
            arguments=[arg(0, 0), arg(1, 0)]),
    func(func_name="to_string", func_native_name="to_string", func_arity=1,
             source_module="api", source_function="to_string",
            arguments=[arg(0, 0)]),
    func(func_name="to_repr", func_native_name="to_repr", func_arity=1,
             source_module="api", source_function="to_repr",
            arguments=[arg(0, 0)]),
])

NUMBER = module("lalan:lang:_number", [
    func(func_name="pow", func_native_name="_pow", func_arity=2,
         source_module="number", source_function="power",
         affirm_type='space.isnumber', arguments=[arg(0, 0), arg(1, 1)]),

    func(func_name="add", func_native_name="add", func_arity=2,
             source_module="number", source_function="add",
             affirm_type='space.isnumber', arguments=[arg(0, 0), arg(1, 1)]),
    func(func_name="sub", func_native_name="sub", func_arity=2,
             source_module="number", source_function="sub",
             affirm_type='space.isnumber', arguments=[arg(0, 0), arg(1, 1)]),
    func(func_name="mul", func_native_name="mul", func_arity=2,
             source_module="number", source_function="mul",
             affirm_type='space.isnumber', arguments=[arg(0, 0), arg(1, 1)]),
    func(func_name="div", func_native_name="div", func_arity=2,
             source_module="number", source_function="div",
             affirm_type='space.isnumber', arguments=[arg(0, 0), arg(1, 1)]),
    func(func_name="mod", func_native_name="mod", func_arity=2,
             source_module="number", source_function="mod",
             affirm_type='space.isnumber', arguments=[arg(0, 0), arg(1, 1)]),
    func(func_name="negate", func_native_name="negate", func_arity=1,
             source_module="number", source_function="negate",
             affirm_type='space.isnumber', arguments=[arg(0, 0)]),

    func(func_name="le", func_native_name="le", func_arity=2,
             source_module="number", source_function="le",
             affirm_type='space.isnumber', arguments=[arg(0, 0), arg(1, 1)]),
])
DATATYPE = module("lalan:lang:_datatype", [
    func(func_name="union_to_list", func_native_name="union_to_list", func_arity=1,
             source_module="datatype", source_function="union_to_list"),
    func(func_name="get_union", func_native_name="get_union", func_arity=1,
             source_module="datatype", source_function="get_union", process=True,),
    func(func_name="record_keys", func_native_name="record_keys", func_arity=1,
             source_module="datatype", source_function="record_keys"),
    func(func_name="record_values", func_native_name="record_values", func_arity=1,
             source_module="datatype", source_function="record_values"),
    func(func_name="record_index_of", func_native_name="record_index_of", func_arity=2,
             source_module="datatype", source_function="record_index_of",
             arguments=[arg(1, 0), arg(0, 0)]),
    ])
MAP = module("lalan:lang:_map", [
    func(func_name="to_list", func_native_name="_to_list", func_arity=1,
             source_module="pmap", source_function="to_list"),
    ])

print generate(TUPLES)
# print generate(LIST)
# print generate(API)
# print generate(BIT)
# print generate(NUMBER)
# print generate(STRING)
# print generate(MAP)
# print generate(DATATYPE)
