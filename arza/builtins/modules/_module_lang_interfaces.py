from arza.types import space, api


def setup(process, stdlib):
    name = space.newsymbol(process, u'arza:lang:_interfaces')
    _module = space.newemptyenv(name)
    _module.export_all()
    process.modules.add_env(_module)


