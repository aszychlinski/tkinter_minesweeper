# tkinter_minesweeper
COMPLETE - minesweeper port done in tkinter. Pretty happy with how it came out.

## Description
After completing my tkinter_bingo I wanted to do something a bit more complex... but not *too* complex.

Minesweeper seemed like a great concept to implement using OOP (and indeed it was).

Some key points on how this project compares to the previous one or what have I learned.

* in bingo I used the .grid geometry manager and it seemed like the only logical choice. I thought .pack was going to be worthless.
Still, I decided to use pack for this project out of - let's call it "academic curiosity" - and I'm glad I did. Now that I have a decent handle on how to align widgets on a canvas with
it, I think it's slightly better than grid. :persevere:
* slightly more complex parent / child tree for the widgets (not by much though) :family:
* `import tkinter as tk` instead of `from tkinter import *` and I think I'm gonna stay like that. The only one who is allowed to muck up
my global namespace is **me**. :smiling_imp:
* use of the `threading` module to make a timer :watch:. It was my first contact with multithreading and I'm surprised with how well that went. 
* My comment and docstring formatting is now much closer to what `PEP 8` and `PEP 257` prescribe. Full, capitalised sentences, double spaces, triple-double quotes, the whole shtick. :blue_book:
* fully realized


## Compiling to .exe

`pyinstaller` works for this project, however it would not add tkinter.tkx to the package on its own.
To get a working .exe I ended up using:

`pyinstaller --add-data "tix8.4.3;tix8.4.3" -F -y -w --clean main.py`

Where "tix8.4.3" is a folder taken from my main Python installation with all of its contents and pasted into the same folder as main.py.
