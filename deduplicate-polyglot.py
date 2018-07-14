#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Removes duplicated positions from a polyglot file"""

import chess
import chess.polyglot
import argparse



def write_polyglot_bin(f, entries):
    entries = sorted(entries, key=lambda entry: entry.key)
    for entry in entries:
        f.write(chess.polyglot.ENTRY_STRUCT.pack(*entry))


def deduplicate(board, book, outfile, visited, towrite, level=0, maxdepth=1000, printtree=True):
    """
    deduplication procedure
    0. if no moves in input for this position, return
    1. add highest-weight move in current position to outfile
    2. enumerate legal moves in position
    3. call on each legal move
    """
    if(level > maxdepth):
        return

    zobrist_hash = chess.polyglot.zobrist_hash(args.board)
    if zobrist_hash in visited:
        return
    visited.add(zobrist_hash)

    moves = list(book.find_all(zobrist_hash))
    if(len(moves) > 0):
        moves.sort(key=lambda x: x.weight, reverse=True)
        entry = moves[0]
        towrite.append(entry)
        if(printtree):
            print("{}├─ \033[1m{}\033[0m (weight: {}, learn: {})".format(
                "|  " * level,
                args.board.san(entry.move()),
                entry.weight,
                entry.learn))
    else:
        return

    legalmoves = board.legal_moves
    for move in legalmoves:
        board.push(move)
        deduplicate(board, book, outfile, visited, written, level + 1, printtree)
        board.pop()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("book", type=chess.polyglot.open_reader)
    parser.add_argument("outfile", metavar="PATH")
    parser.add_argument("--print-tree", action="store_true",
                        help="Print the book tree upon each probing. (May print lots of text.)")
    parser.add_argument("--depth", type=int, default=1000)
    parser.add_argument("--fen", type=chess.Board, default=chess.Board(), dest="board")
    args = parser.parse_args()
    written = []
    deduplicate(args.board, args.book, open(args.outfile, "wb"), set(), written, args.depth, printtree=args.print_tree)
    write_polyglot_bin(open(args.outfile, "wb"), written)
    print("Wrote ", len(written), " positions")
