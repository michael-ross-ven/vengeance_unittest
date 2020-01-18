
"""
why vengeance developed?
    1) allow dynamic column names to be applied to rows (rows act as objects, columns act as object attributes)
    2) provide some convenience methods (map rows to dict, rename columns, sort, filter, etc)

simple
    straightforward, intuitive, row-major loops
        for row in flux:
    straightforward, intuitive, attribute access
        row.col_a = 'blah'
        row.col_b = row.col_a
    attribute access doesn't require any mental abstraction
        syntax is clear and self-documenting
        (eg, row.theta = degrees(atan(row.w_2 - row.w_1)))

performant
    does not use wasteful copies of instance dicts
        about half the memory of a DataFrame for same data
        columns modifications applied instantanuously without updating rows one-by-one
    iteration speed is limited only by python itself
        flux_cls does not use specialized data structures (only lists in native python)

a complimentary library to pandas
    flux_cls:  fill role for small and mid-sized (a couple million rows) datasets
    DataFrame: large datasets

    small and mid-sized datasets are far more common
    until performance becomes the dominant factor, vectorization is not needed, simplicity
    should be valued over performance
    DataFrame is hard to inspect in debugger, hard to find problematic rows / values
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

from line_profiler import LineProfiler
profiler = LineProfiler()


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

    if profiler.functions:
        profiler.print_stats()


def instantiate_flux(num_rows=100,
                     num_cols=3,
                     len_values=3):

    m = random_matrix(num_rows, num_cols, len_values)
    flux = flux_cls(m)

    a = flux.is_empty
    a = flux.is_jagged

    a = flux.headers
    a = flux.header_values
    a = flux.first_five_rows

    a = flux.num_rows
    a = flux.num_cols
    a = flux.max_num_cols

    return flux


def random_matrix(num_rows=1_000,
                  num_cols=3,
                  len_values=3):
    m = [[]]
    for i in range(num_cols):
        m[0].append('col_{}'.format(chr(i + 97)))

    alc = ascii_lowercase
    for _ in range(num_rows):
        row = [''.join(choice(alc) for _ in range(len_values))
                                   for _ in range(num_cols)]
        m.append(row)

    return m


def invalid_instantiations():
    """
    matrix must have exactly 2-dimensions
    although a blank flux_cls may be instantiated without any arguments
    eg
        flux = flux_cls()
        but not
        flux = flux_cls([])

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

    # encapsulate insertion, deletion and rename within single function
    flux.matrix_by_headers('col_c',
                           'col_b',
                           '(inserted_a)',
                           {'col_a': 'renamed_a'},
                           '(inserted_b)',
                           '(inserted_c)')

    # assign values to column
    flux['renamed_a'] = [None] * flux.num_rows

    # assign values to a new column
    flux['new_col'] = ['new'] * flux.num_rows

    # read values from column
    col = flux['col_b']
    cols = flux.columns('col_b', 'col_c')

    pass


def modify_rows(flux):
    flux_e = flux_cls()
    flux_e.append_rows([['a', 'b', 'c']] * 25)

    flux_a = flux.copy()
    flux_b = flux.copy()

    flux_b.append_rows([['a', 'b', 'c']] * 25)
    a = flux_a.num_rows
    b = flux_b.num_rows

    flux_b.insert_rows(5, [['blah', 'blah', 'blah']] * 10)

    # inserting rows at index 0 will overwrite existing headers
    flux_b.insert_rows(0, [['col_d', 'col_e', 'col_f']] +
                          [['d', 'e', 'f']] * 3)
    a = flux_a.header_values
    b = flux_b.header_values

    # add rows from another flux_cls
    flux_c = flux_a + flux_b
    flux_a += flux_b
    flux_a += [['a', 'b', 'c']] * 25
    
    flux_b.insert_rows(0, flux_a)
    flux_b.append_rows(flux_a.matrix[10:15])

    pass


def iterate_primitive_rows(flux):
    """ iterate rows as a list of primitive values

    .rows(r_1=0, r_2='*l'):
        * r_1, r_2 are the start and end rows of iteration
          the default values are the specialized anchor references
          starting at header row, ending at last row
        * r_1, r_2 can also be integers

    m = list(flux.rows())
        * as full matrix, includes header row

    m = list(flux.rows(1))
        * as full matrix, excludes header row
    """
    for row in flux.rows(5, 6):
        a = row[0]

    m = list(flux.rows())
    m = [row.values for row in flux]
    m = [row.values for row in flux.matrix[5:10]]

    # build new matrix
    m = [flux.header_values]
    for r, row in enumerate(flux, 1):
        if r % 2 == 0:
            m.append(row.values)

    # extract column values
    a = [row.values[0] for row in flux]
    a = flux[0]
    a = flux['col_a']
    a = flux.columns('col_a', 'col_b')

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

    m = list(flux.flux_rows())
        * as full matrix, includes header row

    m = list(flux)
        * as full matrix, excludes header row
    """
    flux = flux.copy()

    for row in flux:
        # a = row._view_as_array      # to help with debugging; triggers a special view in PyCharm
        # a = row._headers

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
        # row.values[2:] = ['blah'] * (flux.num_cols - 2)

    # slice
    for row in flux.matrix[5:]:
        pass

    m = flux.matrix[10:-10]

    # extract single column
    col = [row.values[1] for row in flux]
    col = [row.col_b for row in flux]
    col = flux['col_b']
    col = flux.columns('col_b')

    # multiple columns
    cols = flux.columns('col_a', 'col_b', 'col_c')
    cols = flux[1:3]

    # extract primitive values
    m = [row.values for row in flux]

    flux.label_row_indices()         # to help with debugging; modifies row's __repr__

    # build new matrix from even number rows
    m_1 = [flux.matrix[0]]
    for r, row in enumerate(flux, 1):
        if r % 2 == 0:
            m_1.append(row)

    # build new matrix from even number rows
    m_2 = flux.matrix[::2]

    # offset comparisions can easily be achieved by:
    rows     = iter(flux)
    row_prev = next(rows)

    for row in rows:
        if row.col_a == row_prev.col_b:      # some comparison
            pass

    pass


def flux_sort_filter(flux):
    def starts_with_a(_row_):
        """ first-class filter function """
        return (_row_.col_a.startswith('a')
                or _row_.col_b.startswith('a')
                or _row_.col_c.startswith('a'))

    flux = flux.copy()

    # modifications return as new flux_cls
    flux_b = flux.sorted('col_a', 'col_b', 'col_c', reverse=[True, True, True])
    flux_b = flux.filtered(starts_with_a)
    flux_b = flux.filtered_by_unique('col_a', 'col_b')

    # in-place modifications
    flux.sort('col_a', 'col_b', 'col_c', reverse=[False, True])
    flux.filter(starts_with_a)
    flux.filter_by_unique('col_a', 'col_b')

    pass


def flux_aggregation_methods():
    m = [['name_a', 'name_b', 'val']]
    m.extend([['a', 'b', 10]] * 10)
    m.extend([['c', 'd', 20]] * 10)
    m.extend([['e', 'f', 30]] * 10)

    flux = flux_cls(m)

    a = flux.unique_values('name_a')
    a = flux.unique_values('name_a', 'name_b')

    a = flux.namedtuples()

    # .index_row() ("row" singular) and .index_rows() ("rows" plural)
    d_1 = flux.index_row('name_a', 'name_b')
    d_2 = flux.index_rows('name_a', 'name_b')

    k = ('a', 'b')
    a = d_1[k]      # .index_row  (non-unique values are overwritten)
    b = d_2[k]      # .index_rows (non-unique values are stored as list; effectively a groupby statement)

    # .index_rows() can also act as a sumif
    for k, rows in d_2.items():
        v = sum([row.val for row in rows])

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

