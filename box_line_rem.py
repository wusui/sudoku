# Copyright (C) 2026 Warren Usui, MIT License
"""
Handle cases where, inside a box, it can be determined that certain numbers
need to appear in a certain row or column.  If this is the case, then those
numbers cannot appear elsewhere in the box.
"""
from collections import Counter
from itertools import chain
from direct_sets import mk_fs_grps
from board_class import Board, Cell

def get_poss_hist(board):
    """
    Given a board, return a histogram of the number of values in each row
    and column.  Returned as two entries in a dict indexed by 'row' and 'col'
    """
    def gph_inn(rcvals):
        def get_poss(pts):
            def gpi(res):
                return dict(Counter(list(chain.from_iterable(res))))
            return gpi(list(map(lambda a: board.orows[a[0]][a[1]].possible_v,
                                pts)))
        return list(map(get_poss, rcvals))
    return {'row': gph_inn(mk_fs_grps()['row']),
            'col': gph_inn(mk_fs_grps()['col'])}

def eval_rc(pkt):
    """
    Bulk of calculations needed for box line removal.
    Fields in pkt:
        boxv -- Box we are concerned with
        brd -- Copy of the board
        rptr -- Tuple (row or col number, list of all possible values)
        rct -- row or col indicator and row or col number value
    """
    def ninb(rpossv):
        def set_idx(idx):
            def set_looks(looks):
                def set_others(others):
                    def set_grp(grp):
                        def set_grp1(grp1):
                            def set_fvals(fvals):
                                return list(map(lambda a: a[1], fvals))
                            return set_fvals(list(filter(lambda a: rpossv
                                                         in a[0], grp1)))
                        return set_grp1( list(filter(lambda a: a[0], grp)))
                    return set_grp(list(zip(others, looks)))
                return set_others(list(map(
                            lambda a: pkt['brd'].orows[a[0]][a[1]].possible_v,
                            looks)))
            return set_looks(list(filter(lambda a: a[idx] != pkt['rct'][1],
                                         pkt['boxv'])))
        return set_idx({'row': 0, 'col': 1}[pkt['rct'][0]])
    def have_box_only_val(fnd_bov):
        def set_dvalue(dvalue):
            def set_sqs_fix(sqz_fix):
                return (dvalue, pkt['rct'], sqz_fix)
            return set_sqs_fix(list(map(ninb,dvalue)))
        if fnd_bov:
            return set_dvalue(list(map(lambda a: a[0], fnd_bov)))
        return []
    def set_fline(fline):
        def set_fcomp(fcomp):
            if 0 in fcomp:
                return have_box_only_val(list(filter(lambda a: a[1] == 0,
                                list(zip(pkt['rptr'][1].keys(), fcomp)))))
            return []
        return set_fcomp(list(map(lambda a: pkt['rptr'][1][a] - fline[a],
                                  pkt['rptr'][1].keys())))
    return set_fline(get_poss_hist(pkt['brd'])[pkt['rct'][0]][pkt['rct'][1]])

def write_board(board):
    """
    Write a changed board.  All change data is extracted from the info
    parameter.
    """
    def wb_inn(info):
        def g_rows(lb_row):
            def g_cell(lb_cell):
                def chk_it(ccells):
                    def hv_cell(ocell):
                        if [lb_row[0], lb_cell[0]] not in ccells:
                            return ocell
                        return Cell(sq_value=ocell.sq_value,
                                    orig_ind=ocell.orig_ind,
                                    possible_v=list(filter(lambda a:
                                                a not in info[0],
                                                ocell.possible_v)))
                    return hv_cell(lb_row[1][lb_cell[0]])
                return chk_it(list(chain.from_iterable(info[-1])))
            return list(map(g_cell, enumerate(lb_row[1])))
        def write_journal(info):
            def blr_exp():
                def bpos(bposi):
                    def bpos1(sqv):
                        return (sqv[0] // 3) * 3 + (sqv[1] // 3) + 1
                    return f"box {bpos1(list(chain.from_iterable(bposi))[0])} "
                def nval(numvs):
                    if len(numvs) == 1:
                        return str(numvs[0])
                    if len(numvs) == 2:
                        return f'{numvs[0]} and {numvs[1]}'
                    return f'{numvs[0]}, {numvs[1]}, and {numvs[2]}'
                def rcin(ldata):
                    return {'row': 'Row', 'col': 'Column'}[ldata[0]] + \
                            f" {str(ldata[1] + 1)}"
                def further_exp(info):
                    def fe_inn(msg_inf):
                        def fe_inn2(parts):
                            def fepls(sqre):
                                return [sqre[0] + 1, sqre[1] + 1]
                            if parts[1] == []:
                                return ''
                            return f'{parts[0]} cannot be in ' + \
                                    f'{str(list(map(fepls, parts[1])))}'
                        return list(map(fe_inn2, msg_inf))
                    return '\n'.join(fe_inn(list(zip(info[0], info[2]))))
                return ' '.join([f"In {rcin(info[1])}, {nval(info[0])}",
                            f"can only exist in {bpos(info[2])}\n",
                            f"Therefore, no other squares in {bpos(info[2])}",
                            f"can contain {nval(info[0])}\n",
                            further_exp(info)])
            return board.journal + "BOX LINE REMOVAL\n" + blr_exp()
        return Board(orows=list(map(g_rows, enumerate(board.orows))),
                     journal=write_journal(info), delay=0)
    return wb_inn

def blr_scan(board):
    """
    Recursively scan for successive instances where box line removal can
    be done.
    """
    def blr_box(boxp):
        def blr_recur(bnumb):
            def chk_rc(rcdirs):
                def cuptrs(plist):
                    return dict(list(filter(lambda a: a[1] > 1, plist)))
                def mptrs(possvs):
                    return list(Counter(list(chain.from_iterable(possvs))
                                         ).items())
                def chk_one(rptr):
                    def chk1_wrc():
                        def chk_rct(rct):
                            return eval_rc({'boxv': boxp[bnumb], 'brd': board,
                                            'rptr': rptr, 'rct': rct})
                        if not rptr[1]:
                            return []
                        return chk_rct([['row', boxp[bnumb][0][0] + rptr[0]],
                                        ['col', boxp[bnumb][0][1] +
                                        rptr[0] % 3]][rptr[0] // 3])
                    def tst_for_chg(sol_data):
                        if sol_data:
                            if sol_data[-1][-1]:
                                return write_board(board)(sol_data)
                        return []
                    return tst_for_chg(chk1_wrc())
                def eswitch(board_info):
                    if board_info:
                        return board_info[0]
                    return blr_recur(bnumb + 1)
                return eswitch(list(filter(None, list(map(chk_one,
                                            enumerate(list(map(cuptrs,
                                            list(map(mptrs, rcdirs))))))))))
            def get_rc(pts):
                return list(map(lambda a: board.orows[a[0]][a[1]].possible_v,
                                 list(map(lambda a: boxp[bnumb][a], pts))))
            if bnumb == 9:
                return board
            return chk_rc(list(map(get_rc, [[0, 1, 2], [3, 4, 5], [6, 7, 8],
                                     [0, 3, 6], [1, 4, 7], [2, 5, 8]])))
        return blr_recur(0)
    return blr_box

def box_line_rem(board):
    """
    Entry point wrapper to get all box data locations entered.
    """
    return blr_scan(board)(mk_fs_grps()['box'])
