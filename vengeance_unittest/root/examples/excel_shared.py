
import os

from vengeance import open_workbook
from vengeance import close_workbook
from vengeance import get_worksheet
from vengeance import flux_cls
from vengeance import excel_levity_cls

wb   = None
levs = {}
proj_dir = os.getcwd() + '\\files\\'


def set_project_workbook(excel_app='any',
                         read_only=False,
                         update_links=True):
    global wb

    print()
    wb = open_workbook(proj_dir + 'example.xlsm',
                       excel_app,
                       read_only=read_only,
                       update_links=update_links)
    print()


def close_project_workbook(save=True):
    global wb

    if wb is None:
        return

    close_workbook(wb, save)
    wb = None


def worksheet_to_lev(ws,
                     *,
                     meta_r=1,
                     header_r=2,
                     c_1=None,
                     c_2=None):
    global wb
    global levs

    # region {closure functions}
    def worksheet_name():
        """ convert ws variable type to hashable value """
        if isinstance(ws, str):
            return ws.lower()
        if hasattr(ws, 'Name'):
            return ws.Name.lower()      # _Worksheet win32com type

        return ws

    def columns_to_excel_address():
        """ convert c_1, c_2 to address by indexing header row and meta row in worksheet """
        headers = {}
        if (c_1 or c_2) and header_r:
            headers.update(excel_levity_cls.index_headers(ws, header_r))
        if (c_1 or c_2) and meta_r:
            headers.update(excel_levity_cls.index_headers(ws, meta_r))

        return headers.get(c_1, c_1), headers.get(c_2, c_2)
    # endregion

    if isinstance(ws, excel_levity_cls):
        return ws

    if isinstance(ws, str) and (ws.lower() in ('sheet1', 'empty sheet')):
        header_r = 1
        meta_r   = 0
    elif c_1 is None:
        c_1 = 'B'

    if levs is not None:
        k = (worksheet_name(), meta_r, header_r, c_1, c_2)
        if k in levs:
            return levs[k]
    else:
        k = None

    ws = get_worksheet(wb, ws)
    c_1, c_2 = columns_to_excel_address()

    lev = excel_levity_cls(ws,
                           meta_r=meta_r,
                           header_r=header_r,
                           first_c=c_1,
                           last_c=c_2)

    if levs is not None:
        levs[k] = lev

    return lev


def worksheet_to_flux(ws,
                      *,
                      meta_r=1,
                      header_r=2,
                      c_1=None,
                      c_2=None):

    lev = worksheet_to_lev(ws,
                           meta_r=meta_r,
                           header_r=header_r,
                           c_1=c_1,
                           c_2=c_2)
    return flux_cls(lev)


def write_to_worksheet(ws,
                       m,
                       r_1='*h',
                       c_1='B',
                       c_2=None):

    lev = worksheet_to_lev(ws, c_1=c_1, c_2=c_2)
    lev.activate()

    was_filtered = lev.has_filter

    if r_1 != '*a':
        lev.clear('*f %s:*l *l' % r_1)

    lev['*f %s' % r_1] = m

    if was_filtered:
        lev.reapply_filter()






