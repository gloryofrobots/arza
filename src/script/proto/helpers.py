
class List(object):
    class Item(object):
        def __init__(self, previous, next, item):
            self.previous = previous
            self.next = next
            self.data = item

    def __init__(self, head=None, tail=None):
        self.head = head
        self.tail = tail

    def first(self):
        return self.at(0)

    def second(self):
        return self.at(1)

    def third(self):
        return self.at(2)

    def at(self, index):
        element = self.head
        for i in range(0, index):
            if not element:
                raise KeyError("List.at", index)
            element = element.next

        return element.data

    def append(self, *args):
        for item in args:
            self._append(List.Item(None, None, item))

    def _append(self, node):
        if not self.head:
            self.head = self.tail = node
        else:
            node.previous = self.tail
            node.next = None
            self.tail.next = node
            self.tail = node

    def remove(self, node_value):
        current_node = self.head

        while current_node is not None:
            if current_node.data == node_value:
                # if it's not the first element
                if current_node.previous is not None:
                    current_node.previous.next = current_node.next
                    current_node.next.previous = current_node.previous
                else:
                    # otherwise we have no prev (it's None), head is the next one, and prev becomes None
                    self.head = current_node.next
                    current_node.next.previous = None

            current_node = current_node.next

    def appendList(self, other):
        self._append(other.head)

    def to_list(self):
        result = []
        current_node = self.head
        while current_node is not None:
            result.append(current_node.data)
            current_node = current_node.next
        return result

    def __repr__(self):
        result = 'List[' + ",".join([str(i) for i in self.to_list()]) +  ']'
        return result


def main():
    l = List()
    l.append(1, None, 2, "sdasd", [])
    l.remove(None)

    print l
    print l.first()
    print l.second()
    print l.third()
    pass

if __name__ == "__main__":
    main()