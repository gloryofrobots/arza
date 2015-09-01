var transform = function(ast) {
    function tuple(node) {
        var newnode = {
            arity:"unary",
            first:[]
        }

        function _t(n) {
            newnode.push(transform(n.first));
            newnode.push(transform(n.first));
            if ()
        }
        newnode.
        newnode
    }

    var handlers = {
        ',': functio
    }
}