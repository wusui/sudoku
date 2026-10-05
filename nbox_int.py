# Copyright (C) 2026 Warren Usui, MIT License
"""
If a box limits some numbers to certain rows or columns, use that information
to remove possible values from other cell's possible_v lists
"""
from itertools import chain
from direct_sets import mk_fs_grps
from board_class import Board, Cell

def nbox_update(board):
    """
    Produce the next generation of the sudoku board.
    """
    def nbu_inner(updates):
        def ljourn(journ):
            def mk_msg(update):
                def fpoints():
                    #def fptsi():
                    return list(map(lambda a: [a[0] + 1, a[1] + 1],
                                        update['points']))
                    #import pdb; pdb.set_trace()
                    #return f"{fptsi()}"
                return ' '.join([f"Box {update['box'] + 1}",
                                 f"only contains {update['value']} in",
                                 f"{update['line']} {update['indx'] + 1}.",
                                 f"Therefore {fpoints()} cannot be",
                                 f"{update['value']}"])
            return journ + '\n'.join(list(map(mk_msg, updates)))
        def nbu_row(orow):
            def nbu_cell(cell):
                def get_rem(coord):
                    def chkvsup(update):
                        if coord in update['points']:
                            return [update['value']]
                        return []
                    return list(chain.from_iterable(list(map(chkvsup,
                                                             updates))))
                def figure_out(rem_val):
                    def cmod(mcell):
                        return list(filter(lambda a: a not in rem_val,
                                           mcell.possible_v))
                    if not rem_val:
                        return board.orows[orow[0]][cell[0]]
                    return Cell(
                            sq_value=board.orows[orow[0]][cell[0]].sq_value,
                            orig_ind=board.orows[orow[0]][cell[0]].orig_ind,
                            possible_v=cmod(board.orows[orow[0]][cell[0]])
                            )
                return figure_out(get_rem([orow[0], cell[0]]))
            return list(map(nbu_cell, enumerate(orow[1])))
        return Board(orows=list(map(nbu_row, enumerate(board.orows))),
                     journal=ljourn(board.journal), delay=0)
    return nbu_inner

def n1box_int(board):
    """
    Main computing module
    """
    def n_inn(all_27):
        def get_each_box(abox):
            def find_numb(numb):
                def frange(points):
                    def grange(rowcol):
                        return list(set(list(map(lambda a: a[rowcol],
                                                 points))))
                    return list(map(grange, [0, 1]))
                return frange(list(filter(lambda a: numb in
                             board.orows[a[0]][a[1]].possible_v, abox)))
            return list(map(find_numb, range(1, 10)))
        def interpret(entry):
            def ibox(boxn):
                def inum(cell):
                    def rowcol(points):
                        if len(points) == 1:
                            return points[0]
                        return -1
                    return list(map(rowcol, cell))
                return list(enumerate(list(map(inum, boxn))))
            return list(enumerate(list(map(ibox, entry))))
        def collect(box_data):
            def box_fmt(boxno):
                def num_fmt(numb):
                    def figure(pts):
                        def ifig(fdata):
                            return [boxno, numb + 1, fdata[0], pts[fdata[1]]]
                        return [ifig(['row', 0]), ifig(['col', 1])]
                    return figure(box_data[boxno][1][numb][1])
                return list(map(num_fmt, range(9)))
            return list(map(box_fmt, range(9)))

        def rfmt(rdata):
            def rfmt2(rdata2):
                def rfmt3(rdata3):
                    def rfmt4(rdata4):
                        def rfmt5(rdata5):
                            return {'box': rdata5[0], 'value': rdata5[1],
                                    'line': rdata5[2], 'indx': rdata5[3]}
                        return list(map(rfmt5, rdata4))
                    return rfmt4(list(filter(lambda a: a[-1] >= 0, rdata3)))
                return rfmt3(list(chain.from_iterable(rdata2)))
            return rfmt2(list(chain.from_iterable(rdata)))
        def apply(nbox_vals):
            def app_inn(nbox):
                def app_lo27(a_list):
                    def app_pare_list(a_lfv):
                        def app_p(oval):
                            return {'box': nbox['box'],
                                    'value': nbox['value'],
                                    'line': nbox['line'],
                                    'indx': nbox['indx'],
                                    'points': oval}
                        return app_p(list(filter(lambda a: nbox['value'] in
                                  board.orows[a[0]][a[1]].possible_v, a_lfv)))
                    return app_pare_list(filter(lambda a: a not in
                            all_27['box'][nbox['box']], a_list))
                return app_lo27(list(map(list,
                                all_27[nbox['line']][nbox['indx']])))
            return list(map(app_inn, nbox_vals))
        return nbox_update(board)(list(filter(lambda a: a['points'],
                        apply(rfmt(collect(interpret(list(map(
                        get_each_box, all_27['box'])))))))))
    return n_inn

def nbox_int(board):
    """
    Entry point wrapper
    """
    return n1box_int(board)(mk_fs_grps())
