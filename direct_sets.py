# Copyright (C) 2026 Warren Usui, MIT License
"""
Solve squares where process of elimination leaves only one value, and squares
that can be only one number because it is the last possible square to have
that number in a certain row, column, or box.
"""
from functools import lru_cache
from itertools import chain
from collections import Counter
from board_class import Board, Cell
from display import display

def chain_result(binfo):
    """
    Chain lists of lists and filter out empty entries
    """
    return list(filter(None, list(chain.from_iterable(binfo))))

def change_board(old_data):
    """
    Loop through a board and create new cells for the values that change
    """
    def set_chg(chg_info):
        def cb_arow(one_row):
            def cb_acell(one_cell):
                def in_same_box():
                    return ((one_row[0] // 3 == chg_info['row'] // 3) and
                            (one_cell[0] // 3 == chg_info['col'] // 3))
                if one_row[0] == chg_info['row']:
                    if one_cell[0] == chg_info['col']:
                        return Cell(sq_value=chg_info['value'],
                                    orig_ind=False, possible_v=[])
                if chg_info['value'] not in one_cell[1].possible_v:
                    return one_cell[1]
                if one_row[0] == chg_info['row'] or \
                        one_cell[0] == chg_info['col'] or \
                        in_same_box():
                    return Cell(sq_value=0, orig_ind=False,
                                possible_v=list(filter(lambda a:
                                        a != chg_info['value'],
                                        one_cell[1].possible_v)))
                return one_cell[1]
            return list(map(cb_acell, enumerate(one_row[1])))
        return list(map(cb_arow, enumerate(old_data['last'].orows)))
    return set_chg(old_data['found'][0])

def rep_update(packet):
    """
    Called from rep template to loop through all 'found' packet entries
    """
    def repu_inner(bdata):
        def gen_board():
            return Board(orows=change_board(bdata),
                         journal='BASIC METHOD\n' + write_journal({'header':
                                packet['wfunc'](bdata), 'xdata':
                                bdata}), delay=1000)
        if not bdata['found']:
            return bdata['last']
        return repu_inner({'last': gen_board(),
                          'found': bdata['found'][1:]})
    return repu_inner({'last': packet['board'],
                      'found': packet['func'](packet['board'])})

def rep_template(f_info):
    """
    Wrapper to cause either process of elimination or single value found
    checks to repeatedly execute until nothing changes
    """
    def recurs(aboards):
        def done_display(oboard):
            return Board(orows=oboard.orows, journal=oboard.journal,
                         delay=1000)
        if aboards['old'] == aboards['new']:
            return done_display(aboards['new'])
        display(aboards['new'])
        return recurs({'old': aboards['new'],
                       'new': rep_update({'func': f_info['func'],
                                          'wfunc': f_info['wfunc'],
                                          'board': aboards['new']})})
    return recurs({'old': f_info['board'], 'new':
                   rep_update(f_info)})

def write_journal(jdata):
    """
    Write the 'row #, column #, has the value #' portions of all journal
    entries and append appropriate headers
    """
    def eval_new_sq(ns_info):
        return f"row {ns_info['row'] + 1}, column {ns_info['col'] + 1}, " + \
               f"has the value: {ns_info['value']}\n"
    return ''.join([jdata['xdata']['last'].journal, jdata['header'],
                    eval_new_sq(jdata['xdata']['found'][0])])

def proc_of_elim(board):
    """
    Find all cells that only have one possible number left. Return result
    as a list of dicts with the following values:
        'row': row number
        'col': column number
        'value': only possible value this cell can have
    """
    def find_poe1(orow_data):
        def find_poe2(cell_data):
            if len(cell_data[1].possible_v) == 1:
                return {'row': orow_data[0], 'col': cell_data[0],
                        'value': cell_data[1].possible_v[0]}
            return None
        return list(map(find_poe2, enumerate(orow_data[1])))
    return chain_result(list(map(find_poe1, enumerate(board.orows))))

def poe_head(bdata):
    """
    Header text for wfunc process if elimination
    """
    if 'last' not in bdata:
        return 'Bdata is incorrect: '
    return 'By process of elimination: '

def process_of_elimination(poebrd):
    """
    Wrapper to find single possible value entries and convert them
    into solved cells
    """
    return rep_template({'func': proc_of_elim,
                         'wfunc': poe_head, 'board': poebrd})

@lru_cache(maxsize=1)
def mk_fs_grps():
    """
    Return lists of 9 cell addresses.
    """
    def mfs_row():
        def r_rpts(row_num):
            return list(zip(9 * [row_num], range(9)))
        return list(map(r_rpts, range(9)))
    def mfs_col():
        def c_rpts(col_num):
            return list(zip(range(9), 9 * [col_num]))
        return list(map(c_rpts, range(9)))
    def mfs_box_sp():
        def box_1(rows):
            def box_2(cols):
                return [rows, cols]
            return list(map(box_2, range(0, 9, 3)))
        return list(map(box_1, range(0, 9, 3)))
    def mfs_box():
        def imfs_box(box_sp):
            def box1(row):
                def box2(col):
                    return [box_sp[0] + row, box_sp[1] + col]
                return list(map(box2, range(3)))
            return list(chain.from_iterable(list(map(box1, range(3)))))
        return list(map(imfs_box, list(chain.from_iterable(mfs_box_sp()))))
    return {'row': mfs_row(), 'col': mfs_col(), 'box': mfs_box()}

def find_singles(fs_board):
    """
    Find all cells that only have one possible number left because they are
    the only source for a number in a row, column or box. Return result
    as a list of dicts with the following values:
        'row': row number
        'col': column number
        'value': only possible value this cell can have
        'dir': one of 'row', 'col', or 'box
    """
    def rc_to_n(r_c):
        return list(map(lambda a: a['row'] * 9 + a['col'], r_c))
    def fs_sing_inner(grps_of_9):
        def fss2(gkey):
            def fss3(tmplt):
                def fss4(cell_loc):
                    return fs_board.orows[cell_loc[0]][cell_loc[1]].possible_v
                def fcount(plist):
                    def process(ndict):
                        def proc1(pts):
                            def proc2(numbs):
                                def proc_si(ipts):
                                    def proc_i(a_cell):
                                        return list(map(lambda a:
                                            list(set(a) & set(numbs)),
                                            a_cell))
                                    return proc_i(list(map(lambda a:
                                                a.possible_v, ipts)))
                                return proc_si(list(map(lambda a:
                                            fs_board.orows[a[0]][a[1]],
                                                        tmplt)))
                            def pfmt(found1):
                                def pfmt2(answers):
                                    def pfmt3(answer):
                                        return {'row': tmplt[answer[0]][0],
                                                'col': tmplt[answer[0]][1],
                                                'value': answer[1][0],
                                                'dir': gkey}
                                    return list(map(pfmt3, answers))
                                return pfmt2(list(filter(lambda a:
                                            len(a[1]) > 0,found1)))
                            if len(pts) == 0:
                                return []
                            return pfmt(enumerate(proc2(list(map(
                                        lambda a: a[0], pts)))))
                        return proc1(list(filter(lambda a: a[1] == 1,
                                                 ndict.items())))
                    return process(Counter(plist))
                return fcount(list(chain.from_iterable(list(map(fss4,
                                                                tmplt)))))
            return list(map(fss3, grps_of_9[gkey]))
        return list(map(fss2, grps_of_9.keys()))
    def fix_chg_dups(chgd_cells):
        def fcd_data(cell_dir):
            def fcd_sqz(clist):
                def fcd_work_it(red_cell):
                    return next(filter(lambda x: x[0] == red_cell,
                                       cell_dir))
                return list(map(fcd_work_it, clist))
            return fcd_sqz(list(set(list(map(lambda a: a[0], cell_dir)))))
        def mk_msgs(cd_list):
            def mk_vtable():
                return dict( list(map(lambda a: [a['row'] * 9 + a['col'],
                                           a['value']], chgd_cells)))
            def mk_msg1(vtable):
                def vfix(nval):
                    return {
                        'row': nval[0] // 9,
                        'col': nval[0] % 9,
                        'value': vtable[nval[0]],
                        'dir': nval[1]
                    }
                return list(map(vfix, cd_list))
            return mk_msg1(mk_vtable())
        return mk_msgs(fcd_data(list(zip(rc_to_n(chgd_cells),
                            list(map(lambda a: a['dir'], chgd_cells))))))
    return fix_chg_dups(chain_result(chain_result(
                    fs_sing_inner(mk_fs_grps()))))

def fs_head(bdata):
    """
    Header function for unique values
    """
    return f"Unique value in {bdata['found'][0]['dir']}: "

def find_single_numb_in_grp(fsn_board):
    """
    Wrapper to find single values in rows, columns, and boxes
    """
    return rep_template({'func': find_singles,
                         'wfunc': fs_head, 'board': fsn_board})
