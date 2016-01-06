__author__ = 'gloryofrobots'


class PMCondition:
    def __init__(self, condition, children=None):
        pass


class PMAction:
    def __init__(self, action, children=None):
        pass


"""
((x,y), true)
((x,x), false)
((x,y,25), {name:"Alice"})
((x,y,25), {name:"Alice"})
(M, {name:"Alice"})
"""


PMAction(
    "push",
    children=[
        PMCondition(
            "is_seq",
            children=[
                PMCondition(
                    "length==2",
                    children=[
                        PMAction(
                            "push [0]",
                            children=[
                                PMCondition(
                                    "is_seq"
                                ),
                                PMCondition(
                                    "success",
                                    children=[
                                        PMAction(
                                            "store M",
                                            children=[
                                                PMAction(
                                                    "push [1]",
                                                    children=[
                                                        PMCondition(
                                                            "is_map",
                                                            children=[
                                                                PMAction(
                                                                    "push [name]",
                                                                    children=[
                                                                        PMCondition
                                                                    ]
                                                                )
                                                            ]
                                                        )
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                ),
            ]
        )
    ]
)
