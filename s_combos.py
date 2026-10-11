# Copyright (C) 2026 Warren Usui, MIT License
"""
Find pairs, triples, and quad combinations that only have 2, 3, or 4 of
the same numbers as possible values.  Use these to eliminate possible values
from other cells in the same row, column, or box.
"""
from itertools import chain, combinations
from direct_sets import mk_fs_grps
from board_class import Board, Cell

def boxn(coord):
    """
    Return box number from the coordinates of a member of the box
    """
    return (3 * (coord[0] // 3) + coord[1] // 3) + 1

def chg_keys(kvals):
    """
    Change list containing a set of coordinates to a dict that is keyed
    off of a unique int value corresponding to the coordinates
    """
    def conv(kval):
        return kval[0] * 9 + kval[1]
    return dict(list(map(lambda a: [conv(a[0]), a[1]], kvals)))

def keyto_pt(keyn):
    """
    Reverse chg_keys
    """
    return [keyn // 9 + 1, keyn % 9 + 1]

def make_chg_pkt(pkt):
    """
    Assemble the packet of data used to generate a new board and the
    corresponding journal.
    """
    def get_isqs(isqs):
        def get_sq_chg(sq_chg):
            def get_remv(remv):
                def get_ptmap(ptmap):
                    def get_chgs0(chgs0):
                        def get_chgs1(chgs1):
                            if chgs1:
                                return {'xdir': pkt['rcb'],
                                        'idata': pkt['idata'],
                                        'info': chg_keys(chgs1)}
                            return []
                        return get_chgs1(list(filter(lambda a: len(a[1]) >0,
                                                     chgs0)))
                    return get_chgs0(list(zip(list(map(lambda a: a[0],
                                                       sq_chg)), ptmap)))
                return get_ptmap(list(map(lambda a:
                                    list(set(a[1]) & set(remv)), sq_chg)))
            return get_remv(list(chain.from_iterable(
                            list(map(lambda a: a[1], pkt['idata'])))))
        return get_sq_chg(list(filter(lambda a: a[0] not in isqs,
                                              pkt['cells'])))
    return get_isqs(list(map(lambda a: a[0], pkt['idata'])))

def comb_update(board):
    """
    Main rountine.  Curry the number of elements in the combinations that
    we are searching for.
    """
    def cu_numb(xsize):
        def cu_boto(sdata):
            def mk_brd(chvall):
                def mk_brdin(chval):
                    def get_rbc_numb():
                        return {'row': chval['idata'][0][0][0] + 1,
                                'col': chval['idata'][0][0][1] + 1,
                                'box': boxn(chval['idata'][0][0])}[
                                                    chval['xdir']]
                    def drow():
                        return f"{chval['xdir'].capitalize()} " \
                                   f"{get_rbc_numb()}"
                    def tfmt():
                        return list(map(lambda a: [a[0] + 1, a[1] + 1],
                                    list(map(lambda a: a[0], chval['idata']))))
                    def svals():
                        def svla(all_s):
                            return sorted(list(set(
                                        chain.from_iterable(all_s))))
                        return svla(list(map(lambda a: a[1], chval['idata'])))
                    def fixcell(acell):
                        def vfix():
                            return list(filter(lambda a:
                                    a not in chval['info'][acell[0]],
                                    acell[1].possible_v))
                        if acell[0] not in list(chval['info'].keys()):
                            return acell[1]
                        return Cell(sq_value=acell[1].sq_value,
                                    orig_ind=acell[1].orig_ind,
                                    possible_v=vfix())
                    def new_row(arow):
                        def nrow2(erows):
                            def gp_erange(erange):
                                def gp_matches(matches):
                                    def gp_ocells(ocells):
                                        def gp_fix(ipairs):
                                            return list(map(fixcell, ipairs))
                                        return gp_fix(list(zip(erange,
                                                               ocells)))
                                    if len(matches) == 0:
                                        return list(map(lambda a: a[1],
                                                        erows[1]))
                                    return gp_ocells(list(map(lambda a: a[1],
                                                    erows[1])))
                                return gp_matches(list(set(erange) &
                                          set(chval['info'].keys())))
                            return gp_erange(list(range(erows[0] * 9,
                                            erows[0] * 9 + 9)))
                        return nrow2([arow[0], list(enumerate(arow[1]))])
                    def njourn(text):
                        def explan():
                            return f"NAKED PAIR, TRIPLE, OR QUAD\n" \
                                   f"In {drow()}, " \
                                   f"{tfmt()} are squares that only contain " \
                                   f"{svals()}.\n" \
                                   f"Therefore other squares in {drow()} " \
                                   "cannot contain these values."
                        def dispindv(chval):
                            def lst_rem(rdata):
                                def lr_v(datum):
                                    return f"Square {keyto_pt(datum[0])} " \
                                           f"cannot contain {datum[1]}"
                                return '\n'.join(list(map(lr_v, rdata))) + '\n'
                            return lst_rem(list(chval['info'].items()))
                        return '\n'.join([text, explan(), dispindv(chval)])
                    return Board(orows=list(map(new_row,
                                enumerate(board.orows))),
                                journal=njourn(board.journal), delay=0)
                return mk_brdin(chvall[0])
            def cu_scells(cells):
                def cu_allv(vlist):
                    def all_chk(chvalst):
                        if not list(filter(None, chvalst)):
                            return analyze(sdata[1:])
                        return mk_brd(list(filter(None, chvalst)))
                    def fgrp(ogrp):
                        def hv_psol(idata):
                            if len(idata) == xsize:
                                return make_chg_pkt({'idata': idata,
                                        'rcb': sdata[0][0][0],
                                        'cells': cells})
                            return []
                        return hv_psol(list(filter(lambda a:
                                    set(a[1]).issubset(ogrp), cells)))
                    return all_chk(list(map(fgrp, combinations(vlist,
                                            xsize))))
                return cu_allv(list(set(chain.from_iterable(list(map(
                        lambda a: a[-1], cells))))))
            return cu_scells(list(filter(lambda a: a[-1],
                            list(zip(sdata[0][0][1], sdata[0][1])))))
        def analyze(sdata):
            if not sdata:
                return board
            return cu_boto(sdata)
        def sgroups(group):
            return list(map(lambda a: [group, a], mk_fs_grps()[group]))
        def find_chg(glist):
            def fc_inn(alist):
                return list(map(lambda a:
                            board.orows[a[0]][a[1]].possible_v,
                            alist[1]))
            return list(zip(glist, list(map(fc_inn, glist))))
        return analyze(find_chg(list(chain.from_iterable(list(map(sgroups,
                                    ['row', 'col', 'box']))))))
    return cu_numb

def two_combo(board):
    """
    Wrapper for two square combinations
    """
    return comb_update(board)(2)

def three_combo(board):
    """
    Wrapper for three square combinations
    """
    return comb_update(board)(3)

def four_combo(board):
    """
    Wrapper for two square combinations
    """
    return comb_update(board)(4)
