
"""
flux_cls
    * a lightweight wrapper around list-of-lists matrices
    * applies semantic names to rows based on header names
    * when vectorization gets too complicated, and you need (or want)
      efficient row-major iteration
"""
from string import ascii_lowercase
from random import choices

import vengeance as ven
from vengeance import flux_cls
from vengeance import print_runtime
from vengeance import is_date

from root.examples import excel_shared as share

# from vengeance import print_performance
# from line_profiler import LineProfiler
# profiler = LineProfiler()


@print_runtime
def main():
    version = ven.__version__

    # invalid_instantiations()
    flux = instantiate_flux(num_rows=50,
                            num_cols=10,
                            len_values=5)

    iterate_flux_rows(flux)
    iterate_primitive_rows(flux)

    flux_aggregation_methods(flux)
    flux_sort_and_filter_methods(flux)

    flux_row_methods(flux)
    flux_jagged_rows(flux)
    flux_column_methods(flux)
    flux_column_values(flux)

    flux_join()

    write_to_file(flux)
    read_from_file()

    # read_from_excel()
    # write_to_excel(flux)

    flux_subclass()

    # attribute_access_performance(flux)


def invalid_instantiations():
    """
    1) matrix must not be one-dimensional
    2) there are certain reserved column names that cannot appear as
    dynamic column names in matrix, eg
        __bool__
        __dict__
        ...
        __weakref__
        _headers
        as_array
        dict
        header_names
        headers
        is_empty
        is_header_row
        is_jagged
        join_values
        namedrow
        namedtuple
        reserved_names
        values
    """
    # from vengeance.classes.flux_row_cls import flux_row_cls

    # reserved = flux_row_cls.reserved_names()
    # reserved = '\n'.join(reserved)
    # print('reserved header names: \n{}'.format(reserved))

    try:
        flux = flux_cls()                       # empty matrix is fine
        flux = flux_cls(['one', 'dimension'])   # this is not, unknown if list is meant to be a row or column
    except IndexError as e:
        print(e)

    try:
        flux = flux_cls([['_headers',
                          'values',
                          'header_names',
                          'is_jagged',
                          '__dict__',
                          '__len__']])
    except NameError as e:
        print(e)

    print()


def instantiate_flux(num_rows=100,
                     num_cols=3,
                     len_values=3):

    # matrix organized like csv data, column names are provided in first row
    m = __random_matrix(num_rows, num_cols, len_values)
    flux = flux_cls(m)

    a = repr(flux)

    a = flux.headers
    a = flux.header_names
    a = flux.as_preview

    a = flux.is_empty()
    a = flux.num_rows
    a = flux.num_cols

    # flux.min_num_cols will differ from flux.min_num_cols when matrix is jagged
    a = flux.is_jagged()
    a = flux.min_num_cols
    a = flux.max_num_cols

    return flux


def iterate_flux_rows(flux):
    """ rows as flux_row_cls objects

    for row in flux:
        * preferred iteration syntax
        * skips header row, begins at flux.matrix[1]
    """
    flux = flux.copy()

    assert flux.num_rows >= 10

    # individual rows
    row = flux.matrix[0]
    row = flux.matrix[5]
    row = flux.matrix[10]

    flux.label_row_indices()            # to help with debugging: modifies row's __repr__ and adds .i attribute
    row = flux.matrix[0]
    row = flux.matrix[5]
    row = flux.matrix[10]

    # .namedtuple() vs .namedtuples()
    # .namedrow()   vs .namedrows()

    m = [row.namedtuple() for row in flux]
    m = list(flux.namedtuples())

    m = [row.namedrow() for row in flux]
    m = list(flux.namedrows())

    # *** for row in flux: *** preferred iteration syntax
    for row in flux:
        # help(row.as_array)            # to help with debugging: triggers a special view in PyCharm
        i = row.i                       # .i attribute added by flux.label_row_indices()

        # a = row.is_header_row()
        a = row.headers
        a = row.header_names
        a = row.values

        a = row.dict()
        a = row.namedtuple()
        a = row.namedrow()

        # read row values
        a = row.col_a
        a = row['col_a']
        a = row[0]
        a = row.values[0]               # row.values[0] is faster than row[0]

        # assign row values
        row.col_a     = a
        row['col_a']  = a
        row[0]        = a
        row.values[0] = a

        # assign multiple row values
        # row.values = ['bleh'] * len(row)
        # row.values[2:] = ['bleh'] * (len(row) - 2)

    # slice matrix
    for row in flux.matrix[5:-5]:
        pass

    # stride matrix
    for row in flux.matrix[::3]:
        pass

    # row offset comparisions
    for row_1, row_2 in zip(flux.matrix[1:], flux.matrix[2:]):
        if row_1.col_a == row_2.col_b:
            pass


def iterate_primitive_rows(flux):
    """ rows as primitive values """
    flux = flux.copy()

    assert flux.num_rows >= 10

    # individual rows
    row = flux.matrix[0].values
    row = flux.matrix[5].values
    row = flux.matrix[10].values

    for row in flux.rows():
        a = row[0]

    for row in flux.rows(r_2=20):
        a = row[0]

    for row in flux.rows(5, 10):
        a = row[0]

    m = list(flux.rows())
    # or
    m = [row.values for row in flux]

    m = [row.dict() for row in flux]

    # build new matrix of primitive values
    m = [flux.header_names]
    for r, row in enumerate(flux, 1):
        if r % 2 == 0 and row[0].startswith('a'):
            m.append(row.values)

    pass


def flux_aggregation_methods(flux):
    """
    two EXTREMELY important methods introduced here:
        .map_rows()
        .map_rows_append()
    """
    flux = flux.copy()

    flux.label_row_indices()

    flux['col_a'] = ['a'] * len(flux)
    flux['col_b'] = ['b'] * len(flux)

    a = flux.unique('col_a')
    a = flux.unique('col_a', 'col_b')

    # **********************************************************************
    # * map rows by column
    # **********************************************************************
    # index_row()  renamed to .map_rows()
    # index_rows() renamed to .map_rows_append()
    # a = flux.index_row('col_a')
    # a = flux.index_rows('col_a')

    # .map_rows() and .map_rows_append() have slightly different behavior
    d_1 = flux.map_rows('col_a', 'col_b')
    d_2 = flux.map_rows_append('col_a', 'col_b')

    k = ('a', 'b')
    a = d_1[k]          # .map_rows():        only ever stores a single row
    b = d_2[k]          # .map_rows_append(): a list of rows, effectively, a groupby operation

    # specify column values to map
    d = flux.map_rows('col_a')
    d = flux.map_rows('col_a', 'col_b')
    d = flux.map_rows(1, 2)
    d = flux.map_rows(slice(-3, -1))

    # map dictionary values to types other than flux_row_cls
    d = flux.map_rows('col_a', 'col_b', rowtype=list)
    d = flux.map_rows('col_a', 'col_b', rowtype=tuple)

    d = flux.map_rows('col_a', 'col_b', rowtype='list')
    d = flux.map_rows('col_a', 'col_b', rowtype='tuple')
    d = flux.map_rows('col_a', 'col_b', rowtype='namedrow')
    d = flux.map_rows('col_a', 'col_b', rowtype='namedtuple')

    flux['value_a'] = [100.0] * len(flux)

    # **********************************************************************
    # * countif / sumif
    # **********************************************************************
    d = flux.map_rows_append('col_a', 'col_b')
    countifs = {k: len(rows) for k, rows in d.items()}
    sumifs   = {k: sum([row.value_a for row in rows])
                                    for k, rows in d.items()}

    # .contiguous()
    #   group rows where *adjacent* values are identical
    items = flux.contiguous('col_a')
    rows  = [flux.matrix[i_1:i_2+1] for _, i_1, i_2 in items]

    pass


def flux_sort_and_filter_methods(flux):

    # region {flux filter functions}

    # variables for filter functions
    criteria_a = {'c', 'd', 'e', 'f', 'z'}
    criteria_b = {'a', 'b', 'm'}

    def starts_with_a(_row_):
        """ first-class function

        filter functions should return a boolean value
            False for rows that will be excluded
            True  for rows that will be included
        """
        return (_row_.col_a.startswith('a') or
                _row_.col_b.startswith('a') or
                _row_.col_c.startswith('a'))

    def starts_with_criteria(_row_):
        """ first-class function referencing variables from closure

        filter functions should return a boolean value
            False for rows that will be excluded
            True  for rows that will be included

        closure scope bypasses the need for additional parameters
        to be passed to function, eg
            starts_with_criteria(_row_, criteria_a, criteria_b)
        """
        return (_row_.col_a[0] in criteria_a or
                _row_.col_b[0] in criteria_b)
    # endregion

    flux_a = flux.copy()
    flux_b = flux.copy()

    flux_a.label_row_indices()
    flux_b.label_row_indices()

    # in-place modifications
    flux_b.sort('col_b')
    flux_b.sort('col_a', 'col_b', 'col_c', reverse=[False, True, False])

    flux_b.filter(starts_with_a)
    flux_b.filter(starts_with_criteria)
    flux_b.filter_by_unique('col_a', 'col_b')

    # methodnames ending in -ed are not in-place, like python's sorted() and sort()
    # flux.sort(),   flux.filter()
    # flux.sorted(), flux.filtered()

    # return new flux_cls
    flux_b = flux_a.sorted('col_b')
    flux_b = flux_a.sorted('col_a', 'col_b', 'col_c', reverse=[True, False, True])

    flux_b = flux_a.filtered(starts_with_a)
    flux_b = flux_a.filtered(starts_with_criteria)
    flux_b = flux_a.filtered_by_unique('col_a', 'col_b')

    pass


def flux_row_methods(flux):
    flux_a = flux.copy()
    flux_b = flux.copy()

    hdrs = __random_matrix(0, num_cols=flux.num_cols)[0]
    hdrs = [h + '_new' for h in hdrs]
    rows = [['new' for _ in range(flux.num_cols)]
                   for _ in range(10)]

    # insert / append rows from another raw lists
    flux_a.append_rows(rows)
    flux_a.insert_rows(5, rows[:3])

    # inserting rows at index 0 will overwrite existing headers
    a = flux_a.header_names
    flux_a.insert_rows(0, [hdrs] + rows)
    b = flux_a.header_names

    assert a != b

    # insert / append rows from another flux_cls
    flux_b.insert_rows(1, flux_a)
    flux_b.append_rows(flux_a.matrix[10:15])

    flux_a = flux.copy()
    flux_b = flux.copy()

    # append rows from flux_a and flux_b
    flux_c = flux_a + flux_b

    # delete all but first 10 rows
    del flux_a.matrix[11:]

    # inplace add
    flux_a += flux_b.matrix[-5:]
    flux_a += flux_b.matrix[10:15]
    flux_a += [['a', 'b', 'c']] * 10

    pass


def flux_jagged_rows(flux):
    flux = flux.copy()

    # check repr
    flux_repr_a = repr(flux)
    row_repr_a  = repr(flux.matrix[1])

    # make some jagged rows
    flux.matrix[1].values[0] = '#err'
    del flux.matrix[1].values[1:]
    flux.matrix[2].values.extend(['#err', '#err'])

    # check repr again with jagged rows
    flux_repr_b = repr(flux)
    row_repr_b  = repr(flux.matrix[1])

    assert '🗲jagged🗲' not in flux_repr_a
    assert '🗲jagged🗲' not in row_repr_a

    assert '🗲jagged🗲' in flux_repr_b
    assert '🗲jagged🗲' in row_repr_b

    if flux.is_jagged():
        c_1 = flux.num_cols
        c_2 = flux.min_num_cols
        c_3 = flux.max_num_cols
        a = list(flux.identify_jagged_rows())


def flux_column_methods(flux):
    flux = flux.copy()
    # flux = flux.copy(deep=True)

    flux.rename_columns({'col_a': 'renamed_a',
                         'col_b': 'renamed_b'})

    flux.insert_columns((0, 'inserted_a'),
                        (0, 'inserted_b'),
                        (0, 'inserted_c'),
                        ('col_c', 'inserted_d'))

    flux.append_columns('append_a',
                        'append_b',
                        'append_c')

    flux.delete_columns('inserted_a',
                        'inserted_b',
                        'inserted_c',
                        'inserted_d')

    flux.rename_columns({'renamed_a': 'col_a',
                         'renamed_b': 'col_b'})

    # encapsulate insertion, deletion and renaming of columns within single function
    flux.matrix_by_headers('col_c',
                           'col_b',
                           {'col_a': 'renamed_a'},
                           {'col_a': 'renamed_a_dup'},
                           '(inserted_a)',
                           '(inserted_b)',
                           '(inserted_c)')

    # return new flux_cls from matrix_by_headers()
    flux_b = flux.copy().matrix_by_headers({'col_c': 'renamed_c'},
                                           {'col_c': 'renamed_d'},
                                           '(inserted_a)')

    pass


def flux_column_values(flux):
    flux = flux.copy()

    assert 'col_a' in flux.headers
    assert 'col_b' in flux.headers
    assert 'col_c' in flux.headers

    # single column
    col = [row.col_b for row in flux]
    col = flux['col_b']
    col = flux.columns('col_b')
    col = flux[-1]
    col = list(col)

    # multiple columns
    cols = flux.columns('col_a', 'col_b', 'col_c')
    cols = flux.columns(0, -2, -1)
    cols = flux[1:3]

    a, b, c = flux.columns('col_a', 'col_b', 'col_c')

    # set existing values from another column
    flux['col_a'] = flux['col_b']
    # append to a new column
    flux['col_new'] = flux['col_b']
    # combine column values
    flux['col_new'] = [(row.col_a, row.col_b, row.col_c) for row in flux]

    # apply function to column
    flux['col_c'] = [v.lower() for v in flux['col_c']]

    # convert datatypes in column
    # flux['col_c'] = [int(v) for v in flux['col_c']]
    # flux['col_c'] = [float(v) for v in flux['col_c']]
    # flux['col_c'] = [str(v) for v in flux['col_c']]
    # flux['col_c'] = [set(v) for v in flux['col_c']]
    # flux['col_c'] = [to_datetime(v, '%Y-%m-%d') for v in flux['col_c']]
    #   etc...

    # shorthand to apply a single value to all rows in column
    flux['col_zz'] = ['blah'] * len(flux)
    flux['col_zz'] = [{'zz': [4, 5, 6]}] * len(flux)
    flux['col_zz'] = [[1, 2, 3] for _ in range(flux.num_rows)]

    flux['r_i'] = range(1, len(flux.matrix))

    flux['col_a'] = flux['col_b']
    flux['col_a'] = [['a'] for _ in range(flux.num_rows)]

    # append a new column
    flux['append_d'] = [['new'] for _ in range(flux.num_rows)]

    # insert a new column
    # flux[(0, 'insert_a')] = [['a'] for _ in range(flux.num_rows)]


def flux_join():

    flux_a = flux_cls([['other_name', 'col_b', 'col_c'],
                       *[['a', 'b', 1.11] for _ in range(10)],
                       *[['c', 'd', 2.22] for _ in range(10)],
                       *[['e', 'f', 3.33] for _ in range(10)]])
    flux_b = flux_cls([['name', 'id', 'cost', 'weight', 'amount'],
                       ['a', '#6151-165', 50.10, 33.33, 4],
                       ['e', '#8979-154', 100.50, 50.50, 6],
                       ['g', '#6654-810', 130.00, 100.33, 10]])

    mapped_rows = flux_b.map_rows('name')

    flux_a.append_columns('id',
                          'cost',
                          'weight')

    for row_a in flux_a:
        row_b = mapped_rows.get(row_a.other_name)
        if row_b is None:
            continue

        # copy values from row_b
        row_a.weight = row_b.weight

        # or copy all column values in common with row_b
        row_a.join_values(row_b)
        assert row_a.id     == row_b.id
        assert row_a.cost   == row_b.cost
        assert row_a.weight == row_b.weight

    # .join method
    for row_a, row_b in flux_a.join(flux_b, {'other_name': 'name'}):
        row_a.cost   = row_b.cost
        row_a.weight = row_b.weight


def write_to_file(flux):
    flux.to_csv(share.files_dir + 'flux_file.csv')
    flux.to_json(share.files_dir + 'flux_file.json')
    flux.serialize(share.files_dir + 'flux_file.flux')

    # .to_file()
    # flux.to_file(share.files_dir + 'flux_file.csv')
    # flux.to_file(share.files_dir + 'flux_file.json')
    # flux.to_file(share.files_dir + 'flux_file.flux')

    # specify encoding
    # flux.to_csv(share.files_dir + 'flux_file.csv', 'utf-8-sig')
    # flux.to_json(share.files_dir + 'flux_file.json', 'utf-8-sig')

    pass


def read_from_file():
    """ class methods (flux_cls, not flux) """

    flux = flux_cls.from_csv(share.files_dir + 'flux_file.csv')
    flux = flux_cls.from_json(share.files_dir + 'flux_file.json')
    flux = flux_cls.deserialize(share.files_dir + 'flux_file.flux')

    # .from_file()
    # flux = flux_cls.from_file(share.files_dir + 'flux_file.csv')
    # flux = flux_cls.from_file(share.files_dir + 'flux_file.json')
    # flux = flux_cls.from_file(share.files_dir + 'flux_file.flux')

    # specify encoding
    # flux = flux_cls.from_csv(share.files_dir + 'flux_file.csv', 'utf-8-sig')
    # flux = flux_cls.from_json(share.files_dir + 'flux_file.json', 'utf-8-sig')

    # fkwargs: used to specifty arguments to how file is read, such as: strict, lineterminator, ensure_ascii, etc
    # flux = flux_cls.from_csv(share.files_dir + 'flux_file.csv', fkwargs={})
    # nrows: reads a restricted number of rows from csv file
    # flux = flux_cls.from_csv(share.files_dir + 'flux_file.csv', fkwargs={'nrows': 50})

    pass


def read_from_excel():
    if ven.loads_excel_module is False:
        print('excel module excluded for platform compatibility')
        return

    flux = share.worksheet_to_flux('sheet1')
    flux = share.worksheet_to_flux('sheet1', c_1='col_a', c_2='col_a')
    flux = share.worksheet_to_flux('subsections', c_1='<sect_2>', c_2='</sect_2>')

    pass


def write_to_excel(flux):
    if ven.loads_excel_module is False:
        print('excel module excluded for platform compatibility')
        return

    share.write_to_worksheet('sheet2', flux)
    share.write_to_worksheet('sheet2', flux.matrix[:4])
    share.write_to_worksheet('sheet1', flux, c_1='F')

    pass


def flux_subclass():
    """
    the transformation idioms in pandas DataFrames can be difficult to interpret, such as
        df['diff'] = np.sign(df.column1.diff().fillna(0)).shift(-1).fillna(0)

    it helps to encapsulate a series of complex state transformations
    in a separate class, where each transformation is given a meaningful
    method name and is responsible for one, and only one action

    the transformation definitions can be controlled by the .commands
    class variable, which provides a high-level description of its intended
    behaviors, without the need to look into any function bodies.
    controlling its behavior through discrete transformations also
    makes each state more explicit, modular and easier to maintain
    """
    m = [['transaction_id', 'name', 'apples_sold', 'apples_bought', 'date'],
         ['id-001', 'alice', 2, 0, '2019-01-13'],
         ['id-002', 'alice', 0, 1, '2018-03-01'],
         ['id-003', 'bob',   2, 5, '2019-07-22'],
         ['id-004', 'chris', 2, 1, '2019-06-28'],
         ['id-005',  None,   7, 1,  None]]
    flux = flux_custom_cls(m)

    # print(flux_custom_cls.commands)
    # a = repr(flux)

    flux.execute_commands(flux.commands)

    # profiler: useful for helping to debug any profile_methods issues
    # flux.execute_commands(flux.commands, profiler=True)
    # flux.execute_commands(flux.commands, profiler='line_profiler')
    # flux.execute_commands(flux.commands, profiler='print_runtime')

    pass


class flux_custom_cls(flux_cls):

    # high-level summary of state transformations
    commands = ['_sort',
                '_replace_null_names',
                '_convert_dates',
                '_count_unique_names',
                '_filter_apples_sold',
                ('append_columns', ('commission',       # append_columns is a super() class method
                                    'apple_brand',
                                    'revenue',
                                    'apple_bonus'))
                ]

    def __init__(self, matrix):
        super().__init__(matrix)
        self.num_unique_names = None

    def _sort(self):
        self.sort('apples_sold', 'apples_bought')
    
    def _replace_null_names(self):
        for row in self:
            if row.name is None:
                row.name = 'unknown'

    def _convert_dates(self):
        # if no errors are expected
        # self['date'] = [to_datetime(o) for o in self['date']]

        # trap rowtype errors
        for i, row in enumerate(self, 1):
            is_valid, row.date = is_date(row.date)
            # if not is_valid:
            #     print("invalid date: '{}', row {:,}".format(row.date, o))

    def _count_unique_names(self):
        self.num_unique_names = len(self.unique('name'))

    def _filter_apples_sold(self):
        def by_apples_sold(_row_):
            return _row_.apples_sold >= 2

        self.filter(by_apples_sold)

    def __repr__(self):
        return '{} ({:,})'.format(self.__class__.__name__, self.num_rows)


# @print_runtime
# @print_performance(repeat=10)
def attribute_access_performance(flux):
    # from vengeance.classes.flux_row_cls import flux_row_cls

    # flux.matrix_to_namedrows()

    # flux_row_cls.__getattr__ = profiler(flux_row_cls.__getattr__)
    # flux_row_cls.__setattr__ = profiler(flux_row_cls.__setattr__)

    for row in flux:
        #   read row values
        # a = row.col_a
        # b = row.col_b
        # c = row.col_c

        #   modify row values
        # row.col_a = 'a'
        # row.col_b = 'b'
        # row.col_c = 'c'

        #   read and modify row values
        row.col_a = row.col_a
        row.col_b = row.col_b
        row.col_c = row.col_c

        # row.values = [None] * len(row)


def __random_matrix(num_rows=100,
                    num_cols=3,
                    len_values=3):

    # region {closure functions}
    def col_letter(col_int):
        """ convert column numbers to character representation """
        if isinstance(col_int, str):
            return col_int

        col_str = ''
        while col_int > 0:
            c = (col_int - 1) % 26
            col_str = chr(c + 65) + col_str
            col_int = (col_int - c) // 26

        return col_str

    def column_name(i):
        c = col_letter(i + 1).lower()
        return 'col_{}'.format(c)

    def random_chars():
        return ''.join(choices(ascii_lowercase, k=len_values))
    # endregion

    m = [[column_name(i) for i in range(num_cols)]]             # header
    m.extend([[random_chars() for _ in range(num_cols)]         # data
                              for _ in range(num_rows)])
    return m


if __name__ == '__main__':
    main()

    # if profiler.functions:
    #     profiler.print_stats()
