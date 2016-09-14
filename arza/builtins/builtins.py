from arza.types import api, space, symbol


def presetup(process, module, stdlib):
    import arza.builtins.lang
    arza.builtins.lang.setup(process, module, stdlib)

    # MODULES
    import arza.builtins.modules._module_lang_interfaces
    arza.builtins.modules._module_lang_interfaces.setup(process, stdlib)

    import arza.builtins.modules.module_lang_types
    arza.builtins.modules.module_lang_types.setup(process, stdlib)

    import arza.builtins.modules.module_list
    arza.builtins.modules.module_list.setup(process, stdlib)

    import arza.builtins.modules.module_tuple
    arza.builtins.modules.module_tuple.setup(process, stdlib)

    import arza.builtins.modules.module_coro
    arza.builtins.modules.module_coro.setup(process, stdlib)

    import arza.builtins.modules.module_bit
    arza.builtins.modules.module_bit.setup(process, stdlib)

    import arza.builtins.modules.module_io
    arza.builtins.modules.module_io.setup(process, stdlib)

    import arza.builtins.modules.module_api
    arza.builtins.modules.module_api.setup(process, stdlib)

    import arza.builtins.modules.module_number
    arza.builtins.modules.module_number.setup(process, stdlib)

    import arza.builtins.modules.module_string
    arza.builtins.modules.module_string.setup(process, stdlib)

    import arza.builtins.modules.module_map
    arza.builtins.modules.module_map.setup(process, stdlib)

    import arza.builtins.modules.module_datatype
    arza.builtins.modules.module_datatype.setup(process, stdlib)

    import arza.builtins.modules.module_generic
    arza.builtins.modules.module_generic.setup(process, stdlib)

    module.export_all()


def postsetup(process):
    create_lang_names(process)


def create_lang_names(process):
    from arza.builtins import lang_names
    prelude = process.modules.prelude
    exports = prelude.exports()
    lang_prefix = space.newsymbol_s(process, lang_names.PREFIX)
    for name in exports:
        new_name = symbol.concat_2(process, lang_prefix, name)
        val = api.at(prelude, name)
        api.put(prelude, new_name, val)


