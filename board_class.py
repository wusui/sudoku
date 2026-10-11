# Copyright (C) 2026 Warren Usui, MIT License
"""
Define immutable Board and Cell objects
Read string data into a Board object
"""
from dataclasses import dataclass
from itertools import chain

@dataclass(frozen=True)
class Cell:
    """
    Immutable representation of a square
    """
    sq_value: int
    orig_ind: bool
    possible_v: list

@dataclass(frozen=True)
class Board:
    """
    Immutable representation of the 9x9 board
    """
    orows: list
    journal: str
    delay: int

def set_board(in_string):
    """
    Given an initial setup string, return a list of rows with board cells set
    """
    def elim_poss(pt_info):
        def elim_pts(foundx):
            return list(filter(lambda a: a not in foundx, range(1, 10)))
        def ep_row():
            def ep_row2(col_v):
                if col_v not in pt_info['points'][pt_info['row']]:
                    return -1
                return pt_info['points'][pt_info['row']][col_v]
            return list(map(ep_row2, range(9)))
        def ep_col():
            def ep_col2(row_v):
                if pt_info['col'] not in pt_info['points'][row_v]:
                    return -1
                return pt_info['points'][row_v][pt_info['col']]
            return list(map(ep_col2, range(9)))
        def ep_box():
            def ep_box_calc(ranges):
                def ebc_1(rowr):
                    def ebc_2(colr):
                        if colr not in pt_info['points'][rowr]:
                            return -1
                        return pt_info['points'][rowr][colr]
                    return list(map(ebc_2, ranges[1]))
                return list(chain.from_iterable(list(map(ebc_1, ranges[0]))))
            def ep_box_r(row_st):
                def ep_box_c(col_st):
                    def epb_r(r_rng):
                        def epb_c(c_rng):
                            return ep_box_calc([r_rng, c_rng])
                        return epb_c(range(col_st, col_st + 3))
                    return epb_r(range(row_st, row_st + 3))
                return ep_box_c((pt_info['col'] // 3) * 3)
            return ep_box_r((pt_info['row'] // 3) * 3)
        return elim_pts(ep_row() + ep_col() + ep_box())
    def sb_hrows(arow):
        def sb_setn(cell_vals):
            def sb_setc(cell_row):
                def sb_xform(vchar):
                    return [vchar[0], int(vchar[1])]
                return (cell_vals[0], list(map(sb_xform, cell_row)))
            return sb_setc(list(filter(lambda a: a[1] != '.',
                                       enumerate(cell_vals[1]))))
        def sb_get_init(pdata):
            def sb_mk_cells(start_data):
                def sbc_row(row_num):
                    def sbc_col(col_num):
                        if col_num in start_data[row_num]:
                            return Cell(start_data[row_num][col_num], True, [])
                        return Cell(0, False, elim_poss({'points': start_data,
                                                  'row': row_num,
                                                  'col': col_num}))
                    return list(map(sbc_col, range(9)))
                return list(map(sbc_row, range(9)))
            return sb_mk_cells(dict(enumerate(
                    list(map(lambda a: dict(a[1]), pdata)))))
        return sb_get_init(list(map(sb_setn, enumerate(arow))))
    return sb_hrows(list(zip(*[iter(in_string)] * 9)))

def mk_board(in_string):
    """
    Create a board from the initial setup string
    """
    return Board(orows=set_board(in_string), journal='', delay=0)
