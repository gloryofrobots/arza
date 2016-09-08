from lalan.types import api, space, symbol


def presetup(process, module, stdlib):
    import lalan.builtins.lang
    lalan.builtins.lang.setup(process, module, stdlib)

    # MODULES
    import lalan.builtins.modules.module_core_types
    lalan.builtins.modules.module_core_types.setup(process, stdlib)

    import lalan.builtins.modules.module_list
    lalan.builtins.modules.module_list.setup(process, stdlib)

    import lalan.builtins.modules.module_tuple
    lalan.builtins.modules.module_tuple.setup(process, stdlib)

    import lalan.builtins.modules.module_coro
    lalan.builtins.modules.module_coro.setup(process, stdlib)

    import lalan.builtins.modules.module_bit
    lalan.builtins.modules.module_bit.setup(process, stdlib)

    import lalan.builtins.modules.module_io
    lalan.builtins.modules.module_io.setup(process, stdlib)

    import lalan.builtins.modules.module_api
    lalan.builtins.modules.module_api.setup(process, stdlib)

    import lalan.builtins.modules.module_number
    lalan.builtins.modules.module_number.setup(process, stdlib)

    import lalan.builtins.modules.module_string
    lalan.builtins.modules.module_string.setup(process, stdlib)

    import lalan.builtins.modules.module_map
    lalan.builtins.modules.module_map.setup(process, stdlib)

    import lalan.builtins.modules.module_datatype
    lalan.builtins.modules.module_datatype.setup(process, stdlib)

    import lalan.builtins.modules.module_generic
    lalan.builtins.modules.module_generic.setup(process, stdlib)

    module.export_all()


def postsetup(process):
    create_lang_names(process)


def create_lang_names(process):
    from lalan.builtins import lang_names
    prelude = process.modules.prelude
    exports = prelude.exports()
    lang_prefix = space.newsymbol_s(process, lang_names.PREFIX)
    for name in exports:
        new_name = symbol.concat_2(process, lang_prefix, name)
        val = api.at(prelude, name)
        api.put(prelude, new_name, val)


