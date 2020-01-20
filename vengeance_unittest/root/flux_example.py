
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

    DataFrame insert / append rows operation is O^2
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

    flux_sort_filter(flux)
    flux_aggregation_methods()

    flux_subclass()

    # flux = flux.namedtuples()
    attribute_access_performance(flux)

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

    m = random_matrix(num_rows, num_cols, len_values)
    flux = flux_cls(m)

    a = flux.headers
    a = flux.header_values
    a = flux.first_five_rows

    a = flux.is_empty
    a = flux.is_jagged

    a = flux.num_rows
    a = flux.num_cols
    a = flux.max_num_cols       # this will differ from self.num_cols when matrix is jagged

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
    """ class methods (flux_cls) """
    flux = flux_cls.from_csv(share.proj_dir + 'flux_file.csv')
    flux = flux_cls.from_json(share.proj_dir + 'flux_file.json')
    flux = flux_cls.deserialize(share.proj_dir + 'flux_file.flux')

    pass


def read_from_excel():
    if share.wb is None:
        share.set_project_workbook(read_only=True)

    flux = share.worksheet_to_flux('Sheet2')


def write_to_excel(flux):
    if share.wb is None:
        share.set_project_workbook(read_only=True)

    share.write_to_worksheet('Sheet2', flux)


def modify_columns(flux):
    flux = flux.copy()
    # flux = flux.copy(deep=True)

    # make rows jagged
    del flux.matrix[3].values[2]
    del flux.matrix[4].values[2]
    del flux.matrix[5].values[2]

    if flux.is_jagged:
        a = flux.identify_jagged_rows()

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

    # read values from column
    col = flux['col_b']
    cols = flux.columns('col_b', 'col_c')

    col = flux[1]
    cols = flux[2:3]

    pass


def modify_rows(flux):
    flux_a = flux_cls()
    flux_a.append_rows([['a', 'b', 'c']] * 25)

    flux_a = flux.copy()
    flux_b = flux.copy()

    flux_b.append_rows([['a', 'b', 'c']] * 25)
    flux_a += [['a', 'b', 'c']] * 25

    a = flux_a.num_rows
    b = flux_b.num_rows

    flux_b.insert_rows(5, [['blah', 'blah', 'blah']] * 10)

    # inserting rows at index 0 will overwrite existing headers
    flux_b.insert_rows(0, [['col_d', 'col_e', 'col_f']] +
                          [['d', 'e', 'f']] * 3)
    a = flux_a.header_values
    b = flux_b.header_values

    # insert / append another flux_cls
    flux_b.insert_rows(0, flux_a)
    flux_b.append_rows(flux_a.matrix[10:15])

    flux_c = flux_a + flux_b
    flux_a += flux_b
    flux_a += flux_b.matrix[10:15]

    pass


def iterate_primitive_rows(flux):
    """ iterate rows as a list of primitive values

    .rows(r_1=0, r_2='*l'):
        * r_1, r_2 are the start and end rows of iteration
          the default values are the specialized anchor references
          starting at header row, ending at last row
        * r_1, r_2 can also be integers
    """
    a = flux.matrix[3].values

    for row in flux.rows(5, 6):
        a = row[0]

    m = list(flux.rows())
    m = [row.values for row in flux]
    m = [row.values for row in flux.matrix[5:10]]

    # alternatives primitive list values from rows
    m = [row.dict() for row in flux]
    m = [row.namedtuple() for row in flux.matrix[5:10]]

    # build new primitive matrix
    m = [flux.header_values]
    for r, row in enumerate(flux, 1):
        if r % 2 == 0:
            m.append(row.values)

    # extract single column values
    col = [row.values[-1] for row in flux]
    col = [row.col_b for row in flux]
    col = flux['col_b']
    col = flux.columns('col_b')

    # multiple columns
    cols = flux[1:3]
    cols = flux.columns('col_a', 'col_b', 'col_c')
    a, b, c = flux.columns('col_c', 'col_b', 'col_a')
    cols_dict = flux.columns('col_a', 'col_b', 'col_c', mapped=True)

    pass


def iterate_flux_rows(flux):
    """ iterate rows as flux_row_cls objects

    .flux_rows(r_1=0, r_2='*l'):
        * r_1, r_2 are the start and end rows of iteration
          the default values are the specialized anchor references
          starting at header row, ending at last row
        * r_1, r_2 can also be integers

    for row in flux:
        * preferred iteration syntax
        * begins at first row, not header row
    """
    flux = flux.copy()

    a = flux.matrix[3]

    for row in flux:
        # a = row._view_as_array      # to help with debugging; triggers a special view in PyCharm
        # a = row._headers
        # a = row.is_header_row()

        a = row.names
        a = row.values

        # a = row.dict()
        # a = row.namedtuples()

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

    flux.label_row_indices()            # to help with debugging; modifies row's __repr__

    # slice
    for row in flux.matrix[5:-5]:
        a = row.i                       # added by label_row_indices()

    # stride
    for row in flux.matrix[::3]:
        a = row.i                       # added by label_row_indices()

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

    # primitive matrix
    m = [row.values for row in flux]
    m = list(flux.rows())

    # vertical comparisions
    row_prev = flux.matrix[1]
    for row in flux.matrix[2:]:
        if row.col_a == row_prev.col_b:
            pass

        row_prev = row

    pass


def flux_sort_filter(flux):
    def starts_with_a(_row_):
        """ first-class filter function """
        return (_row_.col_a.startswith('a') or
                _row_.col_b.startswith('a') or
                _row_.col_c.startswith('a'))

    flux = flux.copy()

    # in-place modifications
    flux.sort('col_a', 'col_b', 'col_c', reverse=[False, True])
    flux.filter(starts_with_a)
    flux.filter_by_unique('col_a', 'col_b')

    # -ed methods return new flux_cls
    flux_b = flux.sorted('col_a', 'col_b', 'col_c', reverse=[True, False, True])
    flux_b = flux.filtered(starts_with_a)
    flux_b = flux.filtered_by_unique('col_a', 'col_b')

    pass


def flux_aggregation_methods():
    m = [['name_a', 'name_b', 'val']]
    m.extend([['a', 'b', 10] for _ in range(10)])
    m.extend([['c', 'd', 20] for _ in range(10)])
    m.extend([['e', 'f', 30] for _ in range(10)])

    flux = flux_cls(m)

    a = flux.unique_values('name_a')
    a = flux.unique_values('name_a', 'name_b')

    # .index_row() and .index_rows() have slightly different behavior
    d_1 = flux.index_row('name_a', 'name_b')        # (row singular) non-unique rows are overwritten
    d_2 = flux.index_rows('name_a', 'name_b')       # (rows plural)  add non-unique rows to list

    k = ('a', 'b')
    a = d_1[k]          # .index_row():  only ever stores a single row
    b = d_2[k]          # .index_rows(): appends rows to list; effectively, a groupby statement

    pass

    # .index_rows() can be used as a sumif
    sumifs = {}
    for k, rows in d_2.items():
        sumifs[k] = sum([row.val for row in rows])

    # .index_row() can be used as a join
    flux_ref = flux_cls([['name', 'id',       'cost'],
                         ['a',    '#6151-165', 5.10],
                         ['e',    '#8979-154', 10.50],
                         ['g',    '#6654-810', 13.00]])
    refs = flux_ref.index_row('name')

    flux.append_columns('id', 'cost')
    for row in flux:
        _row_ref_ = refs.get(row.name_a)
        if _row_ref_:
            row.id   = _row_ref_.id
            row.cost = _row_ref_.cost

    # convert rows to namedtuples, which are read-only and have faster attribute lookups than flux_row_cls
    d = {k: row.namedtuple() for k, row in flux.index_row('name_a').items()}

    # segments of identical values
    a = flux.contiguous_indices('name_a', 'name_b')

    pass


def flux_subclass():
    """
    the flux_custom_cls.commands variable is intended to provide a high-level description
    of the behaviors of this class, making its state transformations more explicit and modular

    flux.execute_commands(flux.commands, profile=True)
        outputs performance metrics for each command
        very useful for debugging any performance issues for custom flux methods
    """
    m = [['transaction_id', 'name', 'apples_sold', 'apples_bought'],
         ['id-001', 'alice', 2, 0],
         ['id-002', 'alice', 0, 1],
         ['id-003', 'bob',   2, 5],
         ['id-004', 'chris', 2, 1],
         ['id-005',  None,   7, 1]]

    flux = flux_custom_cls(m)

    flux.execute_commands(flux.commands)
    # flux.execute_commands(flux.commands, profile=True)
    # flux.execute_commands(flux.commands, profile='line_profiler')
    # flux.execute_commands(flux.commands, profile='print_runtime')

    a = repr(flux)

    pass


class flux_custom_cls(flux_cls):

    # high-level summarization of flux_custom_cls
    commands = [('sort', ('transaction_id', 'apples_sold')),
                '_replace_nones',
                '_count_unique_names',
                '_filter_apples_sold',
                ('append_columns', 'commission')]

    def __init__(self, matrix):
        super().__init__(matrix)
        self.num_unique_names = 0

    def _replace_nones(self):
        for row in self:
            if row.name is None:
                row.name = 'unknown'

    def _count_unique_names(self):
        self.num_unique_names = len(self.unique_values('name'))

    def _filter_apples_sold(self):
        def by_apples_sold(_row_):
            return _row_.apples_sold >= 2

        self.filter(by_apples_sold)

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

