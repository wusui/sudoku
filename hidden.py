# Copyright (C) 2026 Warren Usui, MIT License
"""
Handle hidden pairs/trips/quads.  If there are pairs/trips/quads in cells
with other numbers listed, those numbers can be removed.
"""
from collections import Counter
from itertools import chain, combinations
from direct_sets import mk_fs_grps
from board_class import Board, Cell

def hid_chk(board):
    """
    Step through possible combinations.
    """
    def hid_combos(cdata):
        def gen_combo(csize):
            def cb_hset(c_cand):
                def cb_chk(combs):
                    def cb_indv_comb(acomb):
                        def cb_comp(combo):
                            def chk_chk(pvals):
                                if pvals == []:
                                    return []
                                if len(list(set(pvals) & set(combo))) > 0:
                                    return pvals
                                return []
                            def scheck(pos_sol):
                                def chk_red(fres):
                                    if len(fres) > csize:
                                        return []
                                    if len(list(set(chain.from_iterable(
                                                    fres)))) == csize:
                                        return []
                                    return [combo, fres]
                                return chk_red(list(filter(None, pos_sol)))
                            return scheck(list(map(chk_chk, cdata['cells'])))
                        return cb_comp(list(map(lambda a: a[0], acomb)))
                    return list(map(cb_indv_comb, combs))
                if len(c_cand) < csize:
                    return []
                return cb_chk(list(combinations(c_cand, csize)))
            return cb_hset(list(filter(lambda a: a[1] <= csize,
                                       cdata['histo'])))
        return list(map(gen_combo, [2, 3, 4]))
    def gen_answer(solution):
        def get_ans(squares):
            def ga_2(rdata):
                return list(zip(squares, rdata))
            return ga_2(list(map(lambda a: list(set(a) - set(solution[0][0])),
                                 solution[0][1])))
        return get_ans(list(filter(lambda a: set(solution[0][0]).issubset(
                        board.orows[a[0]][a[1]].possible_v), solution[1])))
    def process(results):
        def stp_g1(fs_data):
            def stp_g2(fs_info):
                def stp_all(all_of_em):
                    def stp_first(first):
                        def stp_issol(solution):
                            def fpoints():
                                def fp_1(grps):
                                    def fp_2(rpairs):
                                        def fp_3(combed):
                                            return list(filter(lambda a: a[0],
                                                               combed))
                                        return fp_3(list(zip(rpairs[0],
                                                    rpairs[1])))
                                    return fp_2([list(chain.from_iterable(
                                            results)), list(
                                            chain.from_iterable(grps))])
                                return fp_1(list(map(lambda a: a[1],
                                            list(mk_fs_grps().items()))))
                            if solution == []:
                                return []
                            return [fpoints(), gen_answer(solution[0])]
                        return stp_issol(list(filter(lambda a: a[0], first)))
                    return stp_first(list(chain.from_iterable(all_of_em)))
                return stp_all(list(map(lambda a: list(zip(results[a],
                                    fs_info[a])), range(3))))
            return stp_g2(list(map(lambda a: fs_data[a][1], range(3))))
        return stp_g1(list(mk_fs_grps().items()))
    def hid_grp(group):
        def indv_grp(grp_vec):
            def hg_ninesome(a_group):
                def hg_cvals(g_cells):
                    def hg_numbs(anumbs):
                        def hg_crunch(result):
                            return list(chain.from_iterable(
                                        chain.from_iterable(result)))
                        return hg_crunch(hid_combos({'cells': g_cells,
                                    'histo': list(Counter(anumbs).items())}))
                    return hg_numbs(list(
                                    chain.from_iterable(g_cells)))
                return hg_cvals(list(map(lambda a:
                            board.orows[a[0]][a[1]].possible_v,
                                         a_group)))
            return list(map(hg_ninesome, grp_vec))
        return process(list(map(lambda a: indv_grp(group[a]),
                                ['row', 'col', 'box'])))
    return hid_grp

def hidden(board):
    """
    Main entry point and all of the executable code outside of the combination
    handling code.
    """
    def do_make(pdata):
        def g_rows(binfo):
            def chk_row(row_info):
                def new_cells(colv):
                    def new_cell(cval):
                        def nc_h(xvals):
                            def nc_nc(odata):
                                def modf(olist):
                                    return list(filter(lambda a:
                                            a not in xvals[0][1], olist))
                                return Cell(sq_value=odata.sq_value,
                                            orig_ind=odata.orig_ind,
                                            possible_v=modf(odata.possible_v))
                            return nc_nc(board.orows[cval[0]][cval[1]])
                        return nc_h(list(filter(lambda a: a[0] == cval,
                                         pdata['changes'])))
                    if [binfo[0], colv] in list(map(lambda a: a[0],
                                                pdata['changes'])):
                        return new_cell([binfo[0], colv])
                    return board.orows[binfo[0]][colv]
                if binfo[0] not in row_info:
                    return list(board.orows[binfo[0]])
                return list(map(new_cells, range(9)))
            return chk_row(list(map(lambda a: a[0][0], pdata['changes'])))
        def write_journal(brd):
            def eval_gmsg(pdata):
                def reduce_change(pdc):
                    def ofmt(anumb):
                        return str([anumb[0] + 1, anumb[1] + 1])
                    return list(map(ofmt, list(map(lambda a: a[0], pdc))))
                def lnumb(pdata):
                    if pdata['location'] == 'row':
                        return pdata['changes'][0][0][0] + 1
                    if pdata['location'] == 'col':
                        return pdata['changes'][0][0][1] + 1
                    return 3 * (pdata['changes'][0][0][0] // 3) + \
                            (pdata['changes'][0][0][1] // 3) + 1
                return f"The numbers {pdata['hidden_group']} " + \
                                "appear in only " + \
                                f"{reduce_change(pdata['changes'])} " + \
                                f"in {pdata['location']} {lnumb(pdata)}\n" + \
                                "Therefore, these locations cannot " + \
                                "any other numbers\n"
            def mk_rem_lines(pdata):
                def fix_chg(achg):
                    def gstr(numb):
                        return f'[{str(achg[0][0] + 1)}, ' + \
                                f'{str(achg[0][1] + 1)}] ' + \
                                f'cannot contain {str(numb)}'
                    return list(map(gstr, achg[1]))
                def fc_s1(indv_c):
                    return '\n'.join(list(chain.from_iterable(indv_c))) + '\n'
                return fc_s1(list(map(fix_chg, pdata['changes'])))
            def njourn(text):
                return '\n'.join([text, 'HIDDEN PAIR, TRIPS, OR QUADS\n',
                                  eval_gmsg(pdata), mk_rem_lines(pdata)])
            return njourn(brd.journal)
        def gen_new_board_maybe(row_lists):
            def changedq(chkv):
                if chkv:
                    return Board(orows=row_lists, journal=write_journal(board),
                             delay=0)
                return board
            return changedq(list(filter(lambda a: board.orows[a] !=
                            row_lists[a], range(9))))
        return gen_new_board_maybe(list(map(g_rows, enumerate(board.orows))))
    def mk_brd(binfo):
        def eval_loc(cells):
            return {0: 'row', 2: 'box', 8: 'col'}[cells[-1][0] - cells[0][0]]
        if not binfo:
            return board
        return do_make({'hidden_group': binfo[0][0][0][0],
                          'location': eval_loc(binfo[0][0][1]),
                          'changes': binfo[1]})
    return mk_brd(hid_chk(board)(mk_fs_grps()))
