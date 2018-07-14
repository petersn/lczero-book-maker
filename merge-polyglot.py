#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Print a polyglot opening book in tree form."""

import chess
import chess.polyglot
import argparse
import shlex
from os import listdir
from os.path import isfile, join
"""
merge
call the deduplicate procedure on both (since they may start from different position)
but in each call check both files to determine highest-weight move (but not to determine if there are any moves)
and generate a set of positions that have already had a move written for them and have it persist between calling 
on file1 and file2
NOTE: 
    deduplicate won't function if called on a book produced by merging two disconnected, nondeduplicated books!
    always deduplicate before merging!
ALSO NOTE:
    merge won't work if one of the arguments was already the result of merging disconnected books
    so make merge take a list of books, and always call once on all the books you want to merge rather than trying to 
    do it iteratively (unless your construction method ensures that each intermediate book is connected)
"""
def write_polyglot_bin(f, entries):
    entries = sorted(entries, key=lambda entry: entry.key)
    for entry in entries:
        f.write(chess.polyglot.ENTRY_STRUCT.pack(*entry))


def merge(board, books, visited, towrite, level=0, maxdepth=1000, printtree=True):
    if(level > maxdepth):
        return

    zobrist_hash = chess.polyglot.zobrist_hash(board)
    if zobrist_hash in visited:
        return
    visited.add(zobrist_hash)

    moves = []
    for book in books:
        moves += list(book.find_all(zobrist_hash))
    if(len(moves) > 0):
        moves.sort(key=lambda x: x.weight, reverse=True)
        entry = moves[0]
        towrite.append(entry)
        if(printtree):
            print("{}├─ \033[1m{}\033[0m (weight: {}, learn: {})".format(
                "|  " * level,
                board.san(entry.move()),
                entry.weight,
                entry.learn))
    else:
        return

    legalmoves = board.legal_moves
    for move in legalmoves:
        board.push(move)
        merge(board, books, visited, towrite, level + 1, maxdepth, printtree)
        board.pop()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputdir", metavar="PATH", help="path to directory where all books to merge are located")
    parser.add_argument("outfile", metavar="PATH", help="path to .bin file to output")
    parser.add_argument("--print-tree", action="store_true",
                        help="Print the book tree (May print lots of text.)")
    parser.add_argument("--depth", type=int, default=1000)
    parser.add_argument("--fens", default="\"" + str(chess.STARTING_FEN) + "\"", dest="boards",
                        help="list of FENs representing the root positions of the books (doesn't need to be ordered).")
    args = parser.parse_args()
    fens = shlex.split(args.boards)
    bookpaths = [args.inputdir + "/" + f for f in listdir(args.inputdir) if isfile(join(args.inputdir, f))]
    books = [chess.polyglot.open_reader(f) for f in bookpaths]

    written = []
    visited = set()
    for fen in fens:
        board = chess.Board()
        board.set_fen(fen)
        merge(board, books, visited, written, 0, args.depth, printtree=args.print_tree)
    write_polyglot_bin(open(args.outfile, "wb"), written)
    print("Wrote ", len(written), " positions")
