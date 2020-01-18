

def main():
    """
    code coverage

    sticky issues:
        modify_iteration_depth
        iterator_to_list
        iteration_depth

        index_sequence
            include Nones, ''?
            convert values to strings?
            number of names must match number of values
    """
    pass


def proto_unittest():
    from types import GeneratorType

    a = [1, 2, 3]
    b = iter(a)
    # c = ['a', [['b']], [['c']]]
    # c = gen()

    # a = flux_row_cls({'a': 1}, ['mike'])
    # d = gen()
    # b = iter([iter(a), iter(a), iter(a)])
    # c = iter([iter(b), iter(b), iter(b)])
    # d = zip([1, 2, 3], [3, 2, 1])

    # e = b.__class__.__name__
    # e = c.__class__.__name__
    # e = hasattr(a, '__next__')
    # e = hasattr(b, '__next__')
    # e = hasattr(c, '__next__')
    # e = hasattr(d, '__next__')

    # i_copy = itertools.tee(b, 1)

    # flux = flux_cls([c])
    # z = iteration_depth(c)
    # z = iterator_to_list(c, True)

    # from vengeance.util.iter import index_sequence
    # skip Nones?
    # a = [None, 'a', 'b', 'c', None, None, 'd', '', '', 'e']
    # b = index_sequence(a)

    pass


def gen():
    for i in range(10):
        yield i
