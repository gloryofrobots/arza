from arza.types import space, api


def setup(process, stdlib):
    from arza.builtins import lang_names
    name = lang_names.get_lang_symbol(process, u"_interfaces")
    _module = space.newemptyenv(name)
    _module.export_all()
    process.modules.add_env(_module)


