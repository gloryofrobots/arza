from arza.types import space, api


def setup(process, stdlib):
    name = space.newsymbol(process, u'arza:lang:_interfaces')
    _module = space.newemptyenv(name)
    setup_interfaces(_module, stdlib.interfaces)
    _module.export_all()
    process.classes.add_env(_module)


def setup_interfaces(module, interfaces):
    api.put(module, interfaces.Any.name, interfaces.Any)
    api.put(module, interfaces.Instance.name, interfaces.Instance)
    api.put(module, interfaces.Singleton.name, interfaces.Singleton)
