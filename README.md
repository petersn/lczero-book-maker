# book-maker

A tool for creating a Polyglot .bin opening book using lc0.
The gist is that it simply runs lc0 in `go infinite` mode, periodically examines the tree, and writes an entry into the opening book for any position that has a sufficient number of visits to be considered sufficiently converged.

## Usage

You must first apply a patch to lc0 that adds a UCI command `dumpnode` that book-maker.py uses to probe the tree.
To do this, checkout the `dumpnode` branch of [my fork of leela-chess](https://github.com/petersn/leela-chess/tree/dumpnode), and build lc0.
(The single commit that implements the patch is [here](https://github.com/petersn/leela-chess/commit/cc56c49cc676d8f7a75b0c174124988774da4bc2), if that's easier for you to apply.)

TODO: Maybe something like `dumpnode` can be merged into the main distribution so this step isn't necessary?

One you have that compiled you can invoke book-maker.py.
The options are relatively obvious:

```
usage: book-maker.py [-h] --command CMD --output PATH --visit-threshold INT
                     [--dump-interval SECONDS] [--dump-tree]

optional arguments:
  -h, --help            show this help message and exit
  --command CMD         Command to run lc0. (Split via shlex.split, and
                        executed.)
  --output PATH         Output path to dump a .bin to.
  --visit-threshold INT
                        Only write moves into the book if their parent has at
                        least this many visits.
  --dump-interval SECONDS
                        Dump a .bin every this many seconds.
  --dump-tree           Dump the book tree upon each probing.

```

An example usage:

```
$ ./book-maker.py --command "/path/to/leela-chess/lc0/build/lc0 -w /tmp/some-network-file --cpuct=100.0" --output opening-book.bin --dump-interval=60 --visit-threshold=100000
```

This will launch lc0 with the given weights file and Cpuct value, and every minute write a book to opening-book.bin containing the most visited move of every position with at least 100k visits.
By default lc0 tends towards exploring extremely deeply, and not very broadly, so here we increased the Cpuct to get a broader book with fewer stupidly long lines.

TODO: Evaluate how much increasing the Cpuct changes the moves selected at extremely high visit counts.

## License

Because this code uses `python-chess`, it is required to be released under the terms of the GPL3.
However, I [*additionally*](https://opensource.stackexchange.com/questions/4137/can-public-domain-use-gpl-licensed-library-program) release the code into the public domain, and under CC0 (for users outside of the US) as well.

