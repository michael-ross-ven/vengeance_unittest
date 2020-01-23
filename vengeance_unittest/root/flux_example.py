
"""
why vengeance developed?
    1) allow dynamic column names to be applied to rows (rows act as objects, columns act as object attributes)
    2) provide some convenience methods (map rows to dict, rename columns, sort, filter, etc)

simple
    straightforward, intuitive, row-major loops
        for row in flux:
            # ...
    straightforward, intuitive, attribute access
        row.col_a = 'blah'
        row.col_b = row.col_a
    attribute access doesn't require any mental abstraction
        syntax is clear and self-documenting
        (eg, row.theta = atan(row.w_2 - row.w_1))

performant
    does not use wasteful copies of instance dicts
        column modifications applied instantanuously, without updating columns on each individual row
        about half the memory of a DataFrame for same matrix
    iteration speed is limited only by python itself
        python's native list structure underlies the flux_cls, no specialized data structures
        or numpy arrays

a complimentary library to pandas
    flux_cls:  fill role for small and mid-sized datasets (up to a couple million rows)
    DataFrame: large datasets (vectorization)

    until performance becomes the dominant factor, vectorization is not needed, simplicity
    should be valued over performance
    small and mid-sized datasets are far more common
    DataFrame inspection in debugger is noisy, hard to find problematic rows / values
    DataFrame syntax has large learning curve, requires a lot of memorization and time
    looking up references in documentation instead of coding
    DataFrame syntax can sometimes get too complicated, too many ways of accomplishing same thing,
    even for very simple and common operations
        eg:
        df['diff'] = df.groupby('id')['day'].apply(lambda x: x.shift(-1) - x) / np.timedelta64(1, 'h')
        df['diff'] = np.sign(df.column1.diff().fillna(0)).shift(-1).fillna(0)
        df.groupby('subgroup', as_index=False).apply(lambda x: (x['col1'].head(1),
                                                     x.shape[0],
                                                     x['start'].iloc[-1] - x['start'].iloc[0]))

        like, wtf does this even mean anymore??

    mapping rows to dictionary is an extremely useful and flexible operation, but....
        VERY slow in pandas (requires transpose operation)
        doesn't store rows themselves
            makes it difficult to apply values from a smaller dataset (ie, join tables)

combine with Excel
    yes, Excel and VBA get a bad rep for being messy and something that only beginners use
    but to verify and analyze results, spreadsheets beat text editors
        easier to view (extend column widths, freeze panes)
        ability to cut / copy / paste, filter, sort
        apply manual formulas
    excludes Linux / macOS machines (tough cookies)

    vengeance controls the Excel Application itself, not just static Escel files
        handles multiple Excel instances (extends the win32com EnsureDispatch function)
        recalculate formulas
        control formatting
        reference named ranges
        invoke VBA
        invoke add-ins
        save as .pdf, move or copy worksheet, etc
"""
from string import ascii_lowercase
from random import choice

import vengeance
from vengeance import flux_cls
from vengeance import flux_row_cls
from vengeance import to_datetime
from vengeance import is_datetime
from vengeance import print_runtime
from vengeance.util.text import print_performance

from root.examples import excel_shared as share

# from line_profiler import LineProfiler
# profiler = LineProfiler()


@print_runtime
def main():
    version = vengeance.__version__

    # invalid_instantiations()
    flux = instantiate_flux(num_rows=1_000,
                            num_cols=10,
                            len_values=10)
    write_to_file(flux)
    read_from_file()

    # read_from_excel()
    # write_to_excel(flux)

    modify_columns(flux)
    modify_rows(flux)

    iterate_primitive_rows(flux)
    iterate_flux_rows(flux)

    flux_sort_and_filter(flux)
    flux_aggregation_methods()

    flux_subclass()

    # flux = flux.namedtuples()
    attribute_access_performance(flux)

    print()

    # if profiler.functions:
    #     profiler.print_stats()


def invalid_instantiations():
    """
    matrix must not be one-dimensional
    eg
        flux = flux_cls(['a', 'b', 'c'])
    although a blank flux_cls may be instantiated without any arguments

    there are certain reserved column names that cannot appear as
    dynamic header names in matrix

    from vengeance.classes.flux_row_cls import flux_row_cls
    print('invalid header names: {}'.format(flux_row_cls.class_names))
    """

    try:
        flux_cls(['col_a', 'col_b', 'col_c'])
    except IndexError as e:
        print(e)

    try:
        flux_cls([['_headers', 'values', 'names', 'col_a']])
    except NameError as e:
        print(e)

    print()


def instantiate_flux(num_rows=100,
                     num_cols=3,
                     len_values=3):

    # matrix organized like csv data, column names are provided in first row
    m = random_matrix(num_rows, num_cols, len_values)
    flux = flux_cls(m)

    a = flux.headers
    a = flux.header_names
    a = flux.preview

    a = flux.is_empty
    a = flux.num_rows
    a = flux.num_cols

    # flux.min_num_cols will differ from flux.min_num_cols when matrix is jagged
    a = flux.is_jagged
    a = flux.min_num_cols
    a = flux.max_num_cols

    return flux


def random_matrix(num_rows=1_000,
                  num_cols=3,
                  len_values=3):
    m = [[]]
    for i in range(num_cols):
        m[0].append('col_{}'.format(chr(i + 97)))

    lc = ascii_lowercase
    for _ in range(num_rows):
        row = [''.join(choice(lc) for _ in range(len_values))
                                  for _ in range(num_cols)]
        m.append(row)

    return m


def write_to_file(flux):
    flux.to_csv(share.proj_dir + 'flux_file.csv')
    flux.to_json(share.proj_dir + 'flux_file.json')
    flux.serialize(share.proj_dir + 'flux_file.flux')

    pass


def read_from_file():
    """ class methods (flux_cls, not flux) """
    flux = flux_cls.from_csv(share.proj_dir + 'flux_file.csv')
    flux = flux_cls.from_json(share.proj_dir + 'flux_file.json')
    flux = flux_cls.deserialize(share.proj_dir + 'flux_file.flux')

    pass


def read_from_excel():
    if share.wb is None:
        share.set_project_workbook(read_only=True)

    flux = share.worksheet_to_flux('sheet1')
    flux = share.worksheet_to_flux('sheet1', c_1='col_a', c_2='col_a')
    flux = share.worksheet_to_flux('subsections', c_1='<sect_2>', c_2='</sect_2>')

    pass


def write_to_excel(flux):
    if share.wb is None:
        share.set_project_workbook(read_only=True)

    share.write_to_worksheet('sheet2', flux)
    share.write_to_worksheet('sheet2', flux.matrix[:4])
    share.write_to_worksheet('sheet1', flux, c_1='F')

    pass


def modify_columns(flux):
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
                           '(inserted_a)',
                           '(inserted_b)',
                           '(inserted_c)')

    # assign values to column
    flux['renamed_a'] = flux['col_b']
    flux['renamed_a'] = ['a'] * flux.num_rows

    # append a new column
    flux['append_d'] = ['new'] * flux.num_rows

    # make rows jagged
    del flux.matrix[3].values[1:]
    flux.matrix[4].values.extend(['jagged', 'jagged'])

    if flux.is_jagged:
        c_1 = flux.num_cols
        c_2 = flux.min_num_cols
        c_3 = flux.max_num_cols
        a = flux.identify_jagged_rows()

    pass


def modify_rows(flux):
    flux_a = flux.copy()
    flux_b = flux.copy()

    flux_b.append_rows([['a', 'b', 'c']] * 25)
    flux_a += [['a', 'b', 'c']] * 25

    a = flux_a.num_rows
    b = flux_b.num_rows

    flux_a = flux_cls()
    flux_a.append_rows([['a', 'b', 'c']] * 25)

    flux_b.insert_rows(5, [['blah', 'blah', 'blah']] * 10)

    # inserting rows at index 0 will overwrite existing headers
    flux_b.insert_rows(0, [['col_d', 'col_e', 'col_f']] +
                          [['d', 'e', 'f']] * 3)
    a = flux_a.header_names
    b = flux_b.header_names

    # insert / append another flux_cls
    flux_b.insert_rows(0, flux_a)
    flux_b.append_rows(flux_a.matrix[10:15])

    flux_c = flux_a + flux_b
    flux_a += flux_b
    flux_a += flux_b.matrix[10:15]

    pass


def iterate_primitive_rows(flux):
    """ rows as primitive values """
    flux = flux.copy()

    # individual rows
    row = flux.matrix[0].values
    row = flux.matrix[3].values

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
    m = [row.namedtuple() for row in flux.matrix[5:10]]

    # build new matrix of primitive values
    m = [flux.header_names]
    for r, row in enumerate(flux, 1):
        if r % 2 == 0 and row[0].startswith('a'):
            m.append(row.values)

    # single column
    col = [row.values[-1] for row in flux]
    col = [row.col_b for row in flux]
    col = flux['col_b']
    col = flux.columns('col_b')

    # multiple columns
    cols = flux[1:3]
    cols = flux.columns('col_a', 'col_b', 'col_c')
    a, b, c = flux.columns('col_c', 'col_b', 'col_a')
    cols_dict = flux.columns('col_a', 'col_b', 'col_c', mapped=True)

    # copy values from another column
    flux['col_a'] = flux['col_b']
    # append new column
    flux['col_new'] = flux['col_b']

    # convert values in column
    flux['col_c'] = [v.lower() for v in flux['col_c']]
    # and if we had appropriate datatypes this column...
    # flux['col_c'] = [int(v) for v in flux['col_c']]
    # flux['col_c'] = [float(v) for v in flux['col_c']]
    # flux['col_c'] = [to_datetime(v, '%Y-%m-%d') for v in flux['col_c']]
    # flux['col_c'] = [custom_function(v) for v in flux['col_c']]
    # etc...

    # filter values
    col = [v for v in flux['col_a']
             if v == 'blah']

    # "primitive" row values can also be more complex
    flux['col_z'] = [tuple(row) for row in flux['col_b']]
    flux['col_z'] = [{'a': [1, 2, 3]} for _ in range(flux.num_rows)]

    pass


def iterate_flux_rows(flux):
    """ rows as flux_row_cls objects

    for row in flux:
        * preferred iteration syntax
        * skips header row, begins at flux.matrix[1]
    """
    flux = flux.copy()

    # individual rows
    row = flux.matrix[0]
    row = flux.matrix[5]
    row = flux.matrix[6]

    flux.label_row_indices()            # to help with debugging; modifies row's __repr__ and adds .i attribute
    row = flux.matrix[0]
    row = flux.matrix[5]
    row = flux.matrix[6]

    pass

    # *** preferred iteration syntax
    for row in flux:
        # a = row._view_as_array        # to help with debugging; triggers a special view in PyCharm
        # a = row._headers
        # a = row.is_header_row()

        i = row.i                       # added by .label_row_indices()
        a = row.names
        a = row.values

        # a = row.dict()
        # a = row.namedtuple()

        # read row values
        a = row.col_a
        a = row['col_a']
        a = row[0]
        a = row.values[0]

        # assign row values
        row.col_a     = a
        row['col_a']  = a
        row[0]        = a
        row.values[0] = a

        # assign multiple row values
        # row.values = ['blah'] * flux.num_cols
        # row.values[2:] = ['blah blah'] * (flux.num_cols - 2)

    # slice
    for row in flux.matrix[5:-5]:
        i = row.i                       # .i added by .label_row_indices()

    # stride
    for row in flux.matrix[::3]:
        i = row.i                       # .i added by .label_row_indices()

    # map, filter rows
    flux['sum_ord'] = [sum(ord(c) for c in s) for s in flux['col_a']]
    rows = [row for row in flux
                if row.sum_ord >= 1150]

    pass

    # vertical comparisions involving multiple columns
    row_prev = flux.matrix[1]
    for row in flux.matrix[2:]:
        if row.col_c is None:
            # exclude bad conditions...
            continue

        if row.col_a == row_prev.col_b:
            # take some action...
            pass

        row_prev = row

    pass


def flux_sort_and_filter(flux):

    # region {filter functions}
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

    flux = flux.copy()

    criteria_a = {'c', 'd', 'e', 'f', 'z'}
    criteria_b = {'a', 'b', 'm'}

    flux.label_row_indices()

    # in-place modifications
    flux.sort('col_a', 'col_b', 'col_c', reverse=[False, True, False])
    # flux.filter(starts_with_a)
    flux.filter(starts_with_criteria)
    flux.filter_by_unique('col_a', 'col_b')

    # *-ed methods return new flux_cls
    flux_b = flux.sorted('col_a', 'col_b', 'col_c', reverse=[True, False, True])
    flux_b = flux.filtered(starts_with_a)
    flux_b = flux.filtered(starts_with_criteria)
    flux_b = flux.filtered_by_unique('col_a', 'col_b')

    pass


def flux_aggregation_methods():
    m = [['name_a', 'name_b', 'val']]
    m.extend([['a', 'b', 1] for _ in range(10)])
    m.extend([['c', 'd', 2] for _ in range(15)])
    m.extend([['e', 'f', 3] for _ in range(10)])

    flux = flux_cls(m)

    flux.label_row_indices()

    a = flux.unique_values('name_a')
    a = flux.unique_values('name_a', 'name_b')

    # mapping of {column(s): row(s)}
    d = flux.index_row('name_a')
    d = flux.index_row('name_a', 'name_b')
    d = flux.index_row(1, 2)

    # .index_row() and .index_rows() have slightly different behavior
    d_1 = flux.index_row('name_a', 'name_b')        # (row singular)  non-unique rows are overwritten
    d_2 = flux.index_rows('name_a', 'name_b')       # (row*s* plural) non-unique rows appended to list

    k = ('a', 'b')
    a = d_1[k]          # .index_row():  only ever stores a single row
    b = d_2[k]          # .index_rows(): list of rows; effectively, a groupby statement

    pass

    # .index_row() can be used as a join against another flux_cls
    flux_join = flux_cls([['name', 'id', 'cost'],
                          ['a', '#6151-165', 5.10],
                          ['e', '#8979-154', 10.50],
                          ['g', '#6654-810', 13.00]])
    join = flux_join.index_row('name')

    flux.append_columns('id', 'cost')
    for row in flux:
        _row_join_ = join.get(row.name_a)
        if _row_join_:
            row.id   = _row_join_.id
            row.cost = _row_join_.cost

    pass

    # .index_rows() can be used as a countif / sumif
    countifs = {k: len(rows) for k, rows in d_2.items()}
    sumifs   = {k: sum(r.val for r in rows)
                for k, rows in d_2.items()}

    pass

    # (performance enhancement)
    # if mapped row values only need to be referenced, not modified,
    # attribute lookups on a namedtuple will be slightly faster than the attribute lookups on a flux_row_cls
    # this time savings can add up if several million lookups need to be performed
    d = flux.index_row('name_a', 'name_b', as_namedtuples=True)
    d = flux.index_rows('name_a', 'name_b', as_namedtuples=True)

    # conversion to namedtuples can also be done this way, but this is MUCH slower
    # the time saved from faster attribute lookups is probably lost from time need to do conversion
    # d = {k: row.namedtuple() for k, row in flux.index_row('name_b').items()}

    # segments where adjacent rows have identical values
    a = flux.contiguous_indices('name_a')
    a = flux.contiguous_indices('name_a', 'name_b')

    pass


def flux_subclass():
    """
    the transformation idioms in pandas DataFrames can be difficult to interpret, such as
        df['diff'] = np.sign(df.column1.diff().fillna(0)).shift(-1).fillna(0)

    it helps to encapsulate a series of complex state transformations
    in a separate class, where each state transformation is given a meaningful
    method name and is responsible for one, and only one state

    the transformation definitions can be controlled by the .commands
    class variable, which provides a high-level description of its intended
    behaviors, without the need to look into any function bodies.
    controlling its behavior through discrete transformations also
    makes each state more explicit, modular and easier to maintain

    (internal transformations meant to be called by .execute_commands() are prefixed with '_'
     to denote that they are not called by client, and to distinguish them from super()
     methods)
    """
    m = [['transaction_id', 'name', 'apples_sold', 'apples_bought', 'date'],
         ['id-001', 'alice', 2, 0, '2019-01-13'],
         ['id-002', 'alice', 0, 1, '2018-03-01'],
         ['id-003', 'bob',   2, 5, '2019-07-22'],
         ['id-004', 'chris', 2, 1, '2019-06-28'],
         ['id-005',  None,   7, 1,  None]]
    flux = flux_custom_cls(m)

    # print(flux_custom_cls.commands)
    flux.execute_commands(flux.commands)

    # profile argument: useful for helping to debug any performance issues
    # flux.execute_commands(flux.commands, profile=True)
    # flux.execute_commands(flux.commands, profile='line_profiler')
    # flux.execute_commands(flux.commands, profile='print_runtime')

    a = repr(flux)

    pass


class flux_custom_cls(flux_cls):

    # high-level state-transformation sequence
    commands = ['_sort',
                '_replace_null_names',
                '_convert_dates',
                '_count_unique_names',
                '_filter_apples_sold',
                ('append_columns', ('commission',       # append_columns is a super class method
                                    'apple_brand',
                                    'revenue',
                                    'apple_bonus')),
                '__private_method']

    def __init__(self, matrix):
        super().__init__(matrix)
        self.num_unique_names = None

    def _sort(self):
        self.sort('apples_sold', 'apples_bought')
    
    def _replace_null_names(self):
        # just use an explicit loop for replacement
        for row in self:
            if row.name is None:
                row.name = 'unknown'

    def _convert_dates(self):
        # if no errors are expected
        # self['date'] = [to_datetime(v) for v in self['date']]

        # if there could be errors in conversion
        for i, row in enumerate(self, 1):
            is_date, row.date = is_datetime(row.date)
            if not is_date:
                print("invalid date: '{}', row {:,}".format(row.date, i))

    def _count_unique_names(self):
        self.num_unique_names = len(self.unique_values('name'))

    def _filter_apples_sold(self):
        def by_apples_sold(_row_):
            """ first-class function """
            return _row_.apples_sold >= 2

        self.filter(by_apples_sold)

    def __private_method(self):
        # blah ...
        pass

    def __repr__(self):
        return '{} ({:,})'.format(self.__class__.__name__, self.num_rows)


# @print_performance(repeat=10)
# @profiler
def attribute_access_performance(flux):
    # flux = flux.namedtuples()

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


main()
# exper()

