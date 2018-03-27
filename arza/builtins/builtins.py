from arza.types import api, space, symbol


def presetup(process, module, stdlib):
    import arza.builtins.lang

    arza.builtins.lang.setup(process, module, stdlib)

    import arza.builtins.classes.setup_object
    arza.builtins.classes.setup_object.setup(process, stdlib)

    import arza.builtins.classes.setup_class
    arza.builtins.classes.setup_class.setup(process, stdlib)

    module.export_all()


def postsetup(process):
    create_lang_names(process)


def create_lang_names(process):
    from arza.builtins import lang_names
    prelude = process.classes.prelude
    exports = prelude.exports()
    lang_prefix = space.newsymbol_s(process, lang_names.PREFIX)
    for name in exports:
        new_name = symbol.concat_2(process, lang_prefix, name)
        val = api.at(prelude, name)
        api.put(prelude, new_name, val)
