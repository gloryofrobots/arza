from behavior import Method


def gen_method(name, arity):
    method = Method(name, arity)
    import templates as tpls
    from jinja2 import Template
    template = Template(tpls.METHOD_IMPLEMENTATION_DECLARATION)
    data = template.render(method.as_dict())
    return data


print gen_method("__true_tostring__", 1)
print gen_method("__true_tobool__", 1)
print gen_method("__clone__", 1)
print gen_method("__true_compare__", 2)
print gen_method("__true_hash__", 1)

print gen_method("__false_tostring__", 1)
print gen_method("__false_tobool__", 1)
print gen_method("__clone__", 1)
print gen_method("__false_compare__", 2)
print gen_method("__false_hash__", 1)

