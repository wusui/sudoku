# Copyright (C) 2026 Warren Usui, MIT License
"""
Sudoku Solver: in_func is a copy of op_list_func() results where first the
lowest ranking tactic is run until no changes are possible, then the second
lowest and lowest ranking tactics are run until no changes are possible, then
the third lowest, second lowest, and lowest ranking tactics are run until no
changes are possible...
"""
import sys
from functools import lru_cache
from itertools import chain
from board_class import mk_board, Board
from direct_sets import process_of_elimination, find_single_numb_in_grp
from nbox_int import nbox_int
from s_combos import two_combo, three_combo, four_combo
from box_line_rem import box_line_rem
from hidden import hidden
from display import display

@lru_cache(maxsize=1)
def op_list_func():
    """
    Set up a table of the order to execute various solution finding / square
    reduction techniques
    """
    return dict(enumerate([process_of_elimination, find_single_numb_in_grp,
                           nbox_int, box_line_rem, two_combo, three_combo,
                           four_combo, hidden]))

def check_all(in_func):
    """
    Repeat one tactic as long as it is making changes to a grid
    """
    def ca_inner(o_grid):
        def ca_inn2(n_grid):
            if isinstance(n_grid, list):
                print('Bad News')
                sys.exit()
            if n_grid.journal == o_grid.journal:
                return n_grid
            return ca_inner(in_func(n_grid))
        return ca_inn2(in_func(o_grid))
    return ca_inner

def clean_journal(board):
    def cj_inner(jtext):
        def cj_no_blanks(dstring):
            def cjnb_inner(tgrps):
                return '\n'.join(tgrps)
            return cjnb_inner(dstring.split('\n\n'))
        def cj_split(split_text):
            def cj_strip(clean_lines):
                return cj_no_blanks('\n'.join(clean_lines))
            return cj_strip(list(map(lambda a: a.strip(), split_text)))
        return cj_split(jtext.split('\n'))
    return Board(orows=board.orows, journal=cj_inner(board.journal),
                 delay=board.delay)

def main_routine(board):
    """
    Repeat execution of different tactics to insure that all possible
    changes using that set of tactics works
    """
    def top_wrapper(sud_funcs):
        def oloop(grids):
            if grids['new'].journal == grids['old'].journal:
                return grids['new']
            return oloop({'new': do_operation(grids['new'])(0),
                          'old': grids['new']})
        def do_operation(o_grid):
            def doop_inner(indx):
                def do_recur(n_grid):
                    return do_operation(n_grid)(indx + 1)
                if indx >= len(sud_funcs):
                    return o_grid
                return do_recur(check_all(sud_funcs[indx])(o_grid))
            return doop_inner
        return oloop({'new': do_operation(board)(0), 'old': board})
    return top_wrapper(op_list_func())

def sudoku(layout):
    """
    Given a layout, return a solution
    """
    return clean_journal(main_routine(mk_board(layout)))

def ascii_result(solution):
    """
    Print solution as an 81 character string
    """
    def conv_row(sorow):
        def conv_cell(socell):
            if socell.sq_value == 0:
                return '.'
            return str(socell.sq_value)
        return ''.join(list(map(conv_cell, sorow)))
    return ''.join(list(chain.from_iterable(list(map(conv_row,
                                                     solution.orows)))))

if __name__ == "__main__":
    #FIGURE = '9...5..1....3..9...4...8..6..8965.........3....51...8.....1..7.61.....2.7...34..9'
    ##FIGURE = '7.4..6.8.6....85.4.9........1..........2.54...3....1562..57........2.......9...47'
    #FIGURE = '5..6..7..38.....4.1..3.4..5.6.8..2..45.2..........157.6...1............8....4.137'
    #FIGURE = '5...634.....7.....1...5.83.....18..7..69......43...9...............7..2.32.64.5..'
    #FIGURE = '..........7658...2.2..3..6.6.9.....4.3.6.9...2.73..9.....4.1.......6..23......485'
    #FIGURE = '3.....1..5..9...3.98..14.6.835.9.2..61..........67........8...44...2.6.5.........'
    #FIGURE = '.......7..1.9.4..8..9........5..17....3..96..1...67..9........4.82.46...3...8....'
    #FIGURE = '.....7.8...962.3.........146...4.....47..36...1.....935...6....9....4......89....'
    #FIGURE = '6...5.1.2.5......3..87........67........4.815.8......6.7.3.9.4..4..8..3...5...6..'
    #This Figure needs box line removal
    FIGURE = '7.4....6..........6..8..3.5.7........2.95......54.2..1.67.........3.52..3...4..19'
    #FIGURE = '.....3.64....52..9..39.7.8.............615..8..2..9...7.......15...2...71.6...24.'
    nboard = sudoku(FIGURE)
    print(nboard.journal)
    display(nboard)
