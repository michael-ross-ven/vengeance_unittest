
"""
    Working with Excel can be tedious.

    It's extremely easy to build bad worksheets and there is no enforcement
    to schemas or standards -- anyone can just paste in data where ever
    they feel like.
    ...
        build in awkward, asymmetrical sections
        multiple, inconsistent section in each ws
        instead of square, continuous ranges on each ws
    ...

    This usually results people treating workbooks like
    as the software equivalent of a dirty laundry hamper; no thought
    is given to how they are organized, even if values are dangling over
    the rim, that tends to be good enough.

    This goes hand-in-hand with insanely complicated
    Excel formulas and VBA that looks like

    ...
        viscous data
        data fluidity
    ...

    https://imgs.xkcd.com/comics/algorithms.png
    https://www.teampay.co/insights/biggest-excel-mistakes-of-all-time/

    To begin doing any kind of iteration over the data, you'll spend a large amount of time
    just finding range boundaries in the worksheets, determining where the last row
    or last column is. It's also dangerous to references values by the arbitrary
    alphanumerical addresses (eg, Range("H23")), leaving you vulnerable
    whenever columns in the sheet are shifted or reordered.
    ...
        instead of more meaningful header names,
    ...

    ...
        and yet many companies are hopelessly dependent on Excel, or have legacy infrastructure
        that would be too time-consuming to replace, especially banks.
        sometimes extracting this data through Excel is unavoidable
    ....

    Other python libraries like xlrd, xlwt, and openpyxl will allow you to read static
    Excel files, but don't grant control over the application itself, limiting many
    abilities that may be critical to have at your disposal like formula recalculation,
    invoking add-ins / VBA, etc

    The excel_levity_cls in vengeance is meant to
    provide some artillery when
    grant maximum control over Excel,
    and dramatically increase the data-fluidity of worksheets, even poorly designed
    ones
    soften up targets
    ...
        allowing the developer more effortlesss
        design stable and flexible processes
        that is stable and can effectively withstand code-hostile environments people have
        created with their workbooks,
        to do whatever transformations necessary

        operate as commando for legacy workbooks
        target awkward, asymmetrical sections

        for new workbooks, to combine the phenomenal prototyping cababilities Excel provides
        with a language that is more worthy than VBA
    ...


"""

from time import sleep

import vengeance
from vengeance import print_runtime
from vengeance import excel_levity_cls
from vengeance import flux_cls
from vengeance.excel_com.excel_constants import (xlPasteColumnWidths,
                                                 xlCalculationManual,
                                                 xlCalculationAutomatic,
                                                 xlNone)

from root.examples import excel_shared as share

xlYellow = 65535
xlBlue   = 15773696
xlPink   = 9856255


def exper():
    share.set_project_workbook(excel_app=None,
                               read_only=True,
                               update_links=True)

    lev_1 = share.worksheet_to_lev('empty sheet')
    lev_2 = share.worksheet_to_lev('Sheet5')

    a = lev_1.first_empty_row
    b = lev_2.first_empty_row

    a = lev_1.first_empty_column
    b = lev_2.first_empty_column

    a = lev_1['*f *a'].Address
    b = lev_2['*f *a'].Address

    pass



@print_runtime
def main():
    version = vengeance.__version__

    share.set_project_workbook(excel_app=None,
                               read_only=True,
                               update_links=True)

    instantiate_lev('sheet1')
    instantiate_lev('sheet2')
    instantiate_lev('empty sheet')
    instantiate_lev('jagged rows')

    lev_subsections()

    iterate_primitive_rows()
    iterate_flux_rows()
    iterate_excel_errors()

    convert_to_flux()

    write_values()
    write_values_from_lev()
    append_values()
    write_formulas()

    modify_range_values(iteration='slow')
    modify_range_values(iteration='fast')

    excel_object_model()
    # allow_focus()

    # share.close_project_workbook(save=False)


def instantiate_lev(tab_name):
    """
    excel_levity_cls range reference:
        lev['<col><row>:<col><row>']
        :returns a win32com reference to Excel range

        anchor reference mnemonics:
            '*h': header
            '*f': first
            '*l': last
            '*a': append

    Instantiating a new excel_levity_cls will ALWAYS clear the Autofilter
    of target worksheet so that range boundaries can be set correctly;
    make sure nothing is dependent on having data filtered in the worksheet
    """
    # help(excel_levity_cls)

    lev = share.worksheet_to_lev(tab_name)

    a = repr(lev)

    a = lev.is_empty
    a = lev.has_filter

    a = lev.num_cols
    a = lev.num_rows

    a = lev.header_r
    a = lev.first_c
    a = lev.last_c
    a = lev.first_r
    a = lev.last_r
    a = lev.first_empty_row
    a = lev.first_empty_column

    a = lev.has_headers
    a = lev.headers
    a = lev.header_values

    a = lev.named_ranges
    a = lev['some_named_range_1'].Value
    a = lev['some_named_range_2'].Value
    a = lev['excel_date'].Value

    # examples of excel_levity_cls reference syntax
    if 'col_b' in lev.headers:
        a = lev['col_b first_r : col_b last_r'].Address

    a = lev['first_c header_r : last_c last_r'].Address
    a = lev['*f *h:*l *l'].Address
    a = lev['A*h:E*l'].Address

    # or lev.sheet.Range('...') for literal addresses
    a = lev['A1'].Value
    a = lev['A1:C10'].Value

    lev['*f *h:*l *l'].Interior.Color = xlPink
    lev['*f *f:*l *l'].Interior.Color = xlBlue

    lev.clear_filter()
    lev.remove_filter()
    lev.reapply_filter()

    return lev


def lev_subsections():
    """
    row 1 (called the meta_row) in the Excel worksheets can be used
    to label subsections within a worksheet

    any other column reference will work, however

    eg:
        by meta names
            share.worksheet_to_lev('subsections', c_1='<sect_2>', c_2='</sect_2>')
        by header names
            share.worksheet_to_lev('subsections', c_1='col_d', c_2='col_h')
        by Excel column address
            share.worksheet_to_lev('subsections', c_1='F', c_2='H')
    """
    lev_1 = share.worksheet_to_lev('subsections', c_1='<sect_1>', c_2='</sect_1>')
    lev_2 = share.worksheet_to_lev('subsections', c_1='<sect_2>', c_2='</sect_2>')
    lev_3 = share.worksheet_to_lev('subsections', c_1='<sect_3/>', c_2='<sect_3/>')

    a = lev_1.meta_headers
    a = lev_1.meta_header_values

    a = lev_1.last_r
    b = lev_2.last_r
    c = lev_3.last_r

    lev_1['*f *h:*l *l'].Interior.Color = xlYellow
    lev_2['*f *h:*l *l'].Interior.Color = xlBlue
    lev_3['*f *h:*l *l'].Interior.Color = xlPink

    lev_1.clear('*f *f:*l *l', clear_colors=True)
    lev_2.clear('*f *f:*l *l', clear_colors=True)
    lev_3.clear('*f *f:*l *l', clear_colors=True)

    lev = share.worksheet_to_lev('subsections')
    lev['*f *h:*l *l'].Interior.Color = xlNone
    lev.reapply_filter()


def iterate_primitive_rows():
    """ iterate rows as a list of primitive values

    .rows(r_1='*h', r_2='*l'):
        * r_1, r_2 are the start and end rows of iteration
          the default values are the specialized anchor references
          starting at header row, ending at last row
        * r_1, r_2 can also be integers corresponding to the rows in the Excel range

    m = list(lev.rows())
        * as full matrix, includes header row

    m = list(lev.rows('*f'))
        * as full matrix, excludes header row

    m = lev['*f *f:*l *l'].Value2
        * returns values directly from Excel range
        * however, there may be reasons you don't want to do this,
          potentially because the matrix returns as read-only tuples,
          and because Excel's error values are not recognized (see iterate_excel_errors())
    """
    lev = share.worksheet_to_lev('Sheet1')
    # lev = share.tab_to_lev('errors')
    # lev = share.tab_to_lev('empty sheet')

    # see docstring for caveats to this
    # m = lev['*f *f:*l *l'].Value2

    for row in lev.rows():
        a = row[0]

    m = list(lev.rows('*f', 10))

    # build new matrix from filtered rows
    m = [lev.header_values]
    for r, row in enumerate(lev.rows('*f')):
        if r % 2 == 0:
            m.append(row)


def iterate_flux_rows():
    """ iterate rows as flux_row_cls objects

    .flux_rows(r_1='*h', r_2='*l'):
        * r_1, r_2 are the start and end rows of iteration
          the default values are the specialized anchor references
          starting at header row, ending at last row
        * r_1, r_2 can also be integers corresponding to the rows in the Excel range

    for row in lev:
        * preferred iteration syntax
        * begins at first row, not header row

    m = list(lev)
        * as full matrix, excludes header row

    m = list(lev.flux_rows())
        * as full matrix, includes header row
    """
    lev = share.worksheet_to_lev('subsections', c_1='<sect_1>', c_2='</sect_1>')

    for row in lev:
        a = row.address
        a = row.names
        a = row.values

        a = row._view_as_array       # meant as a debugging tool in PyCharm

        if 'col_a' in lev.headers:
            a = row.col_a
            a = row['col_a']
            a = row[0]

    m = list(lev.flux_rows(5, 10))

    # extract primitive values
    m = [row.values for row in lev]

    # build new matrix from filtered rows
    m = [lev.header_values]
    for r, row in enumerate(lev):
        if r % 2 == 0:
            m.append(row.values)


def iterate_excel_errors():
    lev = share.worksheet_to_lev('errors')

    # these will return excel's integer error code, be careful
    for row in lev['B3:D6'].Value:
        a = row[-1]

    # reading values with .rows() or .flux_rows() escapes these errors
    for row in lev.rows(3, 3):
        a = row[-1]

    for row in lev.flux_rows(3, 3):
        a = row.col_c


def convert_to_flux():
    """
    lev  = share.worksheet_to_lev('Sheet1')
    flux = flux_cls(lev)
        or
    flux = share.worksheet_to_flux('Sheet1')
    """
    lev  = share.worksheet_to_lev('Sheet1')
    flux = flux_cls(lev)

    for row in flux:
        row.col_a = 'from flux'

    lev['*f *h'] = flux

    pass


def write_values():
    lev = share.worksheet_to_lev('Sheet2')
    lev.clear('*f *f:*l *l')

    # write single value
    lev['*f *f'] = 'hello'

    # write single row
    lev['*f *f'] = ['hello', 'hello', 'hello']

    # write single column
    lev['*f *f'] = [['hello'], ['hello'], ['hello'], ['hello'], ['hello'], ['hello']]

    # write rows and columns
    m = [['col_a', 'col_b', 'col_c']]
    m.extend([['blah', 'blah', 'blah']] * 10)

    lev.clear('*f *f:*l *l')
    lev['*f *h'] = m

    # helper function shortcut
    share.write_to_worksheet('Sheet2', m)

    # Excel dates
    a = lev['excel_date'].Value
    a = lev['excel_date'].Value2

    # convert Excel eopoch float value into datetime
    b = vengeance.to_datetime(a)

    # Excel only accepts datetime.datetime, not datetime.date
    try:
        lev['excel_date'].Value = b.date()
    except TypeError as e:
        print(e)

    # the excel_levity_cls.__setitem__ protects against this issue
    lev['excel_date'] = b.date()


def write_values_from_lev():
    lev_1 = share.worksheet_to_lev('Sheet1')
    lev_2 = share.worksheet_to_lev('Sheet2')

    lev_2.clear('*f *f:*l *l')
    lev_2['*f 5'] = lev_1.rows(5, 10)

    lev_2.clear('*f *f:*l *l')
    lev_2['*f *h'] = lev_1

    # helper function
    share.write_to_worksheet(lev_2, lev_1)


def append_values():
    lev = share.worksheet_to_lev('Sheet2')

    lev.clear('*f *f:*l *l')
    a = lev.first_empty_row

    # if sheet is empty: append_r = first_r
    m = [['a', 'a', 'a']] * 10
    lev['*f *a'] = m

    # if data is already present: append_r = last_r + 1
    a = lev.first_empty_row

    m = [['a', 'a', 'a']] * 10
    lev['*f *a'] = m

    # or use helper function
    share.write_to_worksheet(lev, ['d', 'd', 'd'], r_1='*a')


def write_formulas():
    lev = share.worksheet_to_lev('Sheet2')
    lev.clear('*f *f:*l *l')

    lev.application.Calculation = xlCalculationManual

    # lev['col_a *f'] = '=(1 + 0)'
    # lev['col_b *f'] = '=(1 + 1)'
    # lev['col_c *f'] = '=(1 + 2)'

    # lev['col_a 4'] = '=({}{} + 10)'.format(lev.headers['col_a'], lev.first_r)
    # lev['col_b 4'] = '=({}{} + 20)'.format(lev.headers['col_b'], lev.first_r)
    # lev['col_c 4'] = '=({}{} + 30)'.format(lev.headers['col_c'], lev.first_r)

    lev['*f *h'] = ['col_a', 'col_b', 'col_c', 'col_d', 'col_e', 'col_f', 'col_h', 'col_i', 'col_j']

    lev['col_a *f'] = '=(1 + 0)'
    lev['col_a *f:*l *f'].FillRight()

    lev['col_a 4'] = '=({}{} + 10)'.format(lev.headers['col_a'], lev.first_r)
    lev['col_a 4:*l 4'].FillRight()

    lev.last_r = 20
    lev['col_a 4:*l *l'].FillDown()
    lev.calculate()


@vengeance.print_runtime
def modify_range_values(iteration='slow'):
    """
    although calls like "ws.Range('...').Value" work fine in VBA,
    this is painfully slow for win32com remote procedure calls

    value extraction into flux_cls can also be used for more complex transformations
        flux = share.worksheet_to_flux('Sheet1')
        lev['*f *f'] = flux
    """
    lev = share.worksheet_to_lev('Sheet1')

    if iteration == 'slow':
        ws = lev.worksheet

        # .ScreenUpdating has a huge performance impact
        lev.application.ScreenUpdating = True
        ws.Activate()

        # lev.application.ScreenUpdating = False

        for r in range(2, lev.last_r + 1):
            if r % 100 == 0:
                print('slow iteration, row: {:,}'.format(r))

            ws.Range('C' + str(r)).Value = 'blah'
            if ws.Range('B' + str(r)).Value == 'find':
                ws.Range('B' + str(r)).Value = 'replace'

        lev.application.ScreenUpdating = True

    else:
        m = list(lev)
        for row in m:
            if row.col_b == 'find':
                row.col_b = 'replace'

        lev['*f *f'] = m

    # print()


def excel_object_model():
    from vengeance.excel_com.worksheet import activate_sheet
    from vengeance.excel_com.worksheet import clear_worksheet_filter

    share.wb.Activate()
    ws = vengeance.get_worksheet(share.wb, 'object model')
    activate_sheet(ws)
    ws.Range('B2:D10').Interior.Color = xlNone

    clear_worksheet_filter(ws)

    ws.Range('B2:B10').Interior.Color = xlYellow
    ws.Range('C2:C10').Interior.Color = xlBlue
    ws.Range('D2:D10').Interior.Color = xlPink

    lev_1 = share.worksheet_to_lev('Sheet1')
    lev_2 = share.worksheet_to_lev('object model')

    lev_2.remove_filter()
    lev_2.reapply_filter()

    # special formatting
    lev_2['I *h:K *h'].ColumnWidth = 1

    lev_1['*f *h:*l *h'].Copy()
    lev_2['I *h'].PasteSpecial(Paste=xlPasteColumnWidths,
                               Operation=xlNone,
                               SkipBlanks=False,
                               Transpose=False)

    lev_1.application.CutCopyMode = False

    # invoke macro
    # path = "'{}'".format(share.wb.FullName)
    # macro_name = 'msgbox_test'
    # share.wb.Application.Run(path + '!' + macro_name, 'hello from python')


def allow_focus():
    """
    if excel_levity_cls.allow_focus = False, lev.activate() will have no effect

    setting this value to False allows processes to run without disrupting the user
    """
    print()
    activate_all_sheets()

    print()
    excel_levity_cls.allow_focus = True
    activate_all_sheets()


def activate_all_sheets():
    print('excel_levity_cls.allow_focus = {}'.format(excel_levity_cls.allow_focus))

    for ws in share.wb.Sheets:
        print("activate sheet: '{}'".format(ws.Name))
        lev = share.worksheet_to_lev(ws)
        lev.activate()

        sleep(0.25)


main()
# exper()

