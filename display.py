# Copyright (C) 2026 Warren Usui, MIT License
"""
Tcl display interface
"""
import tkinter as tk
from functools import wraps

def be_quiet():
    """
    Return False if you want to see boards
    """
    return False


def skip_if(condition: bool):
    """
    Do not display boards if be_quiet is true
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if condition:
                return False
            return func(*args, **kwargs)
        return wrapper
    return decorator

@skip_if(be_quiet())
def display(board):
    """
    Display the board locally
    """
    def disp_root(root):
        def disp_canv(canvas):
            def set_brow(brow):
                def set_bcol(bcol):
                    canvas.create_rectangle(30 + 270 * brow,
                                            30 + 270 * bcol,
                                            300 + 270 * brow,
                                            300 + 270 * bcol,
                                            outline="black", width=3)
                list(map(set_bcol, range(3)))
            def set_lit_line(lit_line):
                def sll():
                    return 30 + 90 * lit_line
                if lit_line % 3 != 0:
                    canvas.create_line(sll(), 30, sll(), 840,
                                       fill="green", width=1)
                    canvas.create_line(30, sll(), 840, sll(),
                                       fill="green", width=1)
            canvas.pack(padx=20, pady=20)
            list(map(set_brow, range(3)))
            list(map(set_lit_line, range(9)))
            def disp_rows(rows):
                def disp_cells(cells):
                    def lalign(numb):
                        return 30 + 270 * (numb // 3) + (
                                numb  % 3) * 90 + 45
                    def set_color():
                        if cells[1].orig_ind:
                            return 'black'
                        return 'blue'
                    def set_sm_num(sm_num):
                        canvas.create_text(
                                48 + cells[0] * 90 + (
                                    (sm_num - 1) * 30) % 90,
                                48 + rows[0] * 90 +
                                    (((sm_num - 1) * 30) // 90) * 30,
                                text=str(sm_num),
                                font=("Arial", 18, "bold"),
                                fill="red")
                    if cells[1].sq_value == 0:
                        list(map(set_sm_num, cells[1].possible_v))
                    else:
                        canvas.create_text(
                            lalign(cells[0]),
                            lalign(rows[0]),
                            text=str(cells[1].sq_value),
                            font=("Arial", 60, "bold"),
                            fill=set_color())
                list(map(disp_cells, enumerate(rows[1])))
            list(map(disp_rows, enumerate(board.orows)))
        root.title("Sudoku Solver")
        root.attributes('-topmost', True)
        disp_canv(tk.Canvas(root, width=870, height=870, bg="white"))
        if board.delay > 0:
            root.after(board.delay, root.destroy)
        root.mainloop()
    disp_root(tk.Tk())
