from behavior import *


def gen_method(name, arity):
    method = Method(name, arity)
    return __gen_method(method)

def __gen_method(method):
    import templates as tpls
    from jinja2 import Template
    template = Template(tpls.METHOD_IMPLEMENTATION_DECLARATION)
    data = template.render(method.as_dict())
    return data

def gen_methods(methods):
    return [__gen_method(method) for method in methods]


for m in gen_methods(BASE):
    print m
for m in gen_methods(NUMBER_CAST):
    print m
for m in gen_methods(NUMBER_OPERATIONS):
    print m

"""
print gen_method("__false_compare__", 2)
print gen_method("__false_hash__", 1)
"""
