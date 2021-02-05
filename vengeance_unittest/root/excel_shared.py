
import os

from typing import Any
import vengeance as vgc
# from vengeance import open_workbook
# from vengeance import close_workbook
# from vengeance import excel_levity_cls
from vengeance import flux_cls

''' :types: '''
wb:      Any
wb_levs: (None, dict)

wb        = None
# wb_levs   = None
wb_levs   = {}
files_dir = os.path.split(os.path.realpath(__file__))[0] + '\\files\\'

if not os.path.exists(files_dir):
    raise FileExistsError('whoops, need to modify files_dir')


# noinspection PyTypeChecker,DuplicatedCode
def random_matrix(num_rows=100,
                  num_cols=3,
                  len_values=3):

    from string import ascii_lowercase
    from random import choices
    from random import uniform

    # region {closure functions}
    def header_name(ci):
        cs = ''
        while ci > 0:
            ci_2 = (ci - 1) % 26
            cs   = chr(ci_2 + 97) + cs
            ci   = (ci - ci_2) // 26

        return 'col_{}'.format(cs)

    def random_chars():
        return ''.join(choices(ascii_lowercase, k=len_values))

    def string(i):
        return ''.join(chr(i + 97) * len_values)

    def random_numbers():
        return round(uniform(0, 9), len_values)
    # endregion

    # a = header_name(100)

    # m = [[header_name(i + 1) for i in range(num_cols)]] + \
    #     [[random_chars() for _ in range(num_cols)]
    #                      for _ in range(num_rows)]

    # m = [[header_name(i + 1) for i in range(num_cols)]] + \
    #     [[random_numbers() for _ in range(num_cols)]
    #                        for _ in range(num_rows)]

    # m = [[header_name(i + 1) for i in range(num_cols)]] + \
    #     [[string(i) for i in range(num_cols)]
    #                 for _ in range(num_rows)]

    m = [[header_name(i + 1)           for i in range(num_cols)]] + \
        [[random_numbers()] * num_cols for _ in range(num_rows)]

    # m = tuple(tuple(row) for row in m)

    return m


def set_project_workbook(excel_app='any',
                         read_only=False,
                         update_links=True):
    global wb

    print()
    wb = vgc.open_workbook(files_dir + 'example.xlsm',
                           excel_app,
                           read_only=read_only,
                           update_links=update_links)
    return wb


def close_project_workbook(save=True):
    global wb

    if wb is None:
        return

    vgc.close_workbook(wb, save)
    wb = None


def worksheet_to_lev(ws, *,
                     m_r=1,
                     h_r=2,
                     c_1=None,
                     c_2=None):

    from vengeance import excel_levity_cls

    if isinstance(ws, excel_levity_cls):
        return ws

    # region {closure functions}
    def worksheet_name():
        """ convert ws variable type to hashable value """
        if isinstance(ws, str):
            return ws.lower()
        if hasattr(ws, 'Name'):
            return ws.Name.lower()      # _Worksheet win32com type

        return ws

    def worksheet_headers():
        headers = {}
        if h_r:
            headers.update(excel_levity_cls.index_headers(ws, h_r))
        if m_r:
            headers.update(excel_levity_cls.index_headers(ws, m_r))

        return headers
    # endregion

    global wb
    global wb_levs

    ws_name = worksheet_name()
    if ws_name in ('sheet1', 'empty sheet'):
        h_r = 1
        m_r = 0
    elif c_1 is None:
        c_1 = 'B'

    lev_key = (ws_name,
               m_r, h_r,
               c_1, c_2)
    is_cached = isinstance(wb_levs, dict)

    if is_cached and lev_key in wb_levs:
        return wb_levs[lev_key]

    if wb is None:
        wb = set_project_workbook(read_only=True)

    ws   = wb.Sheets[ws_name]
    ws_h = worksheet_headers()
    c_1  = ws_h.get(c_1, c_1)
    c_2  = ws_h.get(c_2, c_2)

    lev = excel_levity_cls(ws,
                           meta_r=m_r,
                           header_r=h_r,
                           first_c=c_1,
                           last_c=c_2)

    if is_cached:
        wb_levs[lev_key] = lev

    return lev


def worksheet_to_flux(ws, *,
                      m_r=1,
                      h_r=2,
                      c_1=None,
                      c_2=None) -> flux_cls:

    lev = worksheet_to_lev(ws, m_r=m_r, h_r=h_r,
                               c_1=c_1, c_2=c_2)
    return flux_cls(lev)


def write_to_worksheet(ws, m, *,
                       r_1='*h',
                       c_1=None,
                       c_2=None):

    from vengeance.util.iter import is_header_row

    lev = worksheet_to_lev(ws, c_1=c_1, c_2=c_2)
    lev.activate()

    if r_1 == '*a' and not lev.is_empty:
        m = tuple(m)
        if is_header_row(m[0], lev.header_names()):
            m = m[1:]
    else:
        lev.clear('*f %s:*l *l' % r_1)

    lev['*f %s' % r_1] = m









