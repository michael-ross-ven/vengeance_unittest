
from string import ascii_lowercase
from random import choice
from vengeance import write_file
from vengeance import flux_cls


def main():
    """
    code coverage

    sticky issues:
        rename columns, no conflicts
        flux_a + flux_b
        write to worksheet, flux is empty


    where are points of unneccessary complexity?
        matrix to 2-dimen, too many data types

    row.namedtuples()
        same number of names as values?
        iter.index_sequence

    matrix_by_headers
        column = [None] * self.num_rows
        copy?


    flux.append_rows(flux)
    flux.insert_rows(flux)
        if is_vengeance_class(rows):
            rows = list(rows.rows())[1:]

    performance?
    """
    # write_flux_small()

    flux = flux_cls()
    flux = flux_cls([])
    # flux = flux_cls([None])
    flux = flux_cls([[]])

    flux = flux_cls(random_matrix())
    # flux._matrix[1][0] = 'mike'

    # flux.insert_columns(None, None, None)
    # flux.insert_columns((None, None))
    # flux.insert_columns((0, None),
    #                     (1, None))

    # flux.insert_columns((0, None))

    # should insert in order of ins_a, ins_b, ins_c, ins_d
    flux.insert_columns((0,  None),
                        (0, 'ins_c'),
                        (0, 'ins_b'),
                        (0, 'ins_a'),
                        (-1, 'ins_d'))

    # flux.insert_columns((1, 'ins_d'), (1, 'ins_d'))

    # flux.delete_columns(None)       # hmmmm
    flux.delete_columns('None')

    a = flux.rows()
    b = list(a)

    a = flux.flux_rows()
    b = list(a)

    # failllll
    # m = list(flux.rows(0, -10))

    a = flux['col_a']
    a = flux.columns('col_a')
    a = flux.columns('col_a', 'col_c')
    a, b = flux.columns('col_a', 'col_c')

    a = flux[1:]
    a = flux.columns(-2, -1)
    b = flux[-2:]
    assert a == b

    flux['mike'] = flux['col_a']
    flux['mike'] = ['a'] * flux.num_rows
    flux['mike'] = [['a']] * flux.num_rows

    flux.append_columns('(append_col_a)')
    flux.matrix_by_headers('col_a',
                           '(append_col_a)')

    flux.delete_columns(-1)

    a = flux.index_row(('col_a',))      # keys should be tuples
    a = flux.index_row('col_a')         # keys should be strings

    # rows = iter(flux)
    # a = next(rows).col_a
    # flux.append_columns('col_d')
    #
    # for row in rows:
    #     pass

    flux.label_row_indices()

    a = flux.namedtuples()

    # m = flux[11_740:11_752]
    # flux.replace_matrix(m)

    del flux.matrix[2:]
    pass


def random_matrix(num_rows=1_000,
                  num_cols=5,
                  len_values=10):
    m = [[]]
    for i in range(num_cols):
        m[0].append('col_{}'.format(chr(i + 97)))

    alc = ascii_lowercase
    for _ in range(num_rows):
        row = [''.join(choice(alc) for _ in range(len_values))
                                   for _ in range(num_cols)]
        m.append(row)

    return m


def write_flux_small():
    m = random_matrix()
    write_file('c:/users/mike/documents/source code/python/exper/flux_small.csv', m)


