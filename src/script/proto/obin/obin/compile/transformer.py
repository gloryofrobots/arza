__author__ = 'gloryofrobots'
from parser import *

class Transformer(object):
    def __init__(self):
        self.transformers = {}

    def _dispatch_many(self, nodes):
        result = []
        for n in nodes:
            r = self._dispatch(n)
            result.append(r)
        return result

    def _dispatch(self, node):
        pass

    def dispatch(self, node):
        if is_many(node):
            return self._dispatch_many(node)
        else:
            return self._dispatch(node)

    def transform(self, ast):
        pass

var transform = function(ast) {
    function tuple(node) {
        var newnode = {
            arity:"unary",
            first:[],
            id:","
        }

        function _t(n) {
            console.log("_t", n)
            var value;
            if(n.first != undefined) {
                if(n.first.id == ",") {
                    _t(n.first);
                } else {
                    value = traverse(n.first);
                    newnode.first.push(value);
                }
            }
            else {
                newnode.first.push(n);
            }

            if(n.second !== undefined) {
                if(n.second.id == ",") {
                    value = traverse(n.second);
                    newnode.first.push(value);
                } else {
                    _t(n.second);
                }
                //console.log("n.second", value, n.second, n.second !== undefined, n);
            }
        }
        newnode.from = node.from;
        newnode.to = node.to;
        _t(node);
        return newnode;
    }

    var handlers = {
        ',': tuple
    }

    function traverse(node) {
        var handler = handlers[node.id] || function(node) {
            return node;
        }

        console.log("traverse", node);

        node = handler(node);
         if(!node) {
            var x = 1;
        }
        if(node.first) {
            node.first = traverse(node.first)
        }
        if(node.second) {
            node.second = traverse(node.second)
        }
        if(node.third) {
            node.third = traverse(node.third)
        }

        return node;
    }

    var result = [];
    console.log("ast",ast);
    _.each(ast, function(node) {
        console.log("node:", node)
        result.push(traverse(node));
    });
    return result;
}