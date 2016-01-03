from obin.objects import api


def setup(process, module, stdlib):
    traits = stdlib.traits
    api.put_trait(module, traits.Any)
    api.put_trait(module, traits.True)
    api.put_trait(module, traits.False)
    api.put_trait(module, traits.Boolean)
    api.put_trait(module, traits.Nil)
    api.put_trait(module, traits.Undefined)
    api.put_trait(module, traits.Char)
    api.put_trait(module, traits.Number)
    api.put_trait(module, traits.Integer)
    api.put_trait(module, traits.Float)
    api.put_trait(module, traits.Symbol)
    api.put_trait(module, traits.String)
    api.put_trait(module, traits.Vector)
    api.put_trait(module, traits.Tuple)
    api.put_trait(module, traits.Object)
    api.put_trait(module, traits.Generic)
    api.put_trait(module, traits.Module)
    api.put_trait(module, traits.Primitive)
    api.put_trait(module, traits.Function)
