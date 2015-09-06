
def gen_array_pack(name, itemtype, constructor):
    import templates as tpls
    from jinja2 import Template
    template = Template(tpls.ARRAY_PACK_TPL)
    data = template.render(dict(name=name, type=itemtype, constructor=constructor))
    return data

print gen_array_pack("OArray_pack", "OAny", "item")
print gen_array_pack("OArray_ofCStrings", "ostring", "OString(S, item)")
print gen_array_pack("OArray_ofInts", "oint", "OInteger(item)")
