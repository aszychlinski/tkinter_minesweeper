# tkinter_minesweeper
COMPLETE - minesweeper port done in tkinter. Pretty happy with how it came out.

## Contents
:one: main.py - the main release version

:two: main_no_comments.py - same as `main` but without comments or docstrings

:three: main_no_tkx.py - same as the no_comments version but also without the tkinter.tkx extension (and thus without tooltips)

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
* fully realized :arrow_left::arrow_up::arrow_right::arrow_down::ok: support for the gameplay!
* this was arguably the weirdest thing, but... Most of the development was done on the basic version of tkinter, right? And very late in the project I randomly stumbled upon the .tkx extension. And it had tooltips! And they were incredibly shiny!!! I managed to resist the thought for about a day and a half. :see_no_evil: Then I swapped out the `root` from basic tk to a root instanced from tk.tkx. But all of the original widgets are still tk... assigned to a tk.tkx parent. Apparently they are compatible enough that it's not causing problems, but I was scared at first.

There are also shortcomings that I'm aware of. :weary:

* the overall architecture is not nice in the sense that I assume it doesn't lend itself well to importing this as a module. Because a lot of stuff is just instanced or defined in the root of the module. And I know it should be wrapped in classes and launched with `if __name__ == '__main__'` etc.
* use of `global`. I understand why it's frowned upon, but I never intended this game as something someone would import and use in tandem with anything else, so... Still, maybe I should make more of an effort to avoid `global`.
* I try to use only Standard Library modules to make sure this will run on any installation of Python. However, ingame display is based on use of the Wingdings font. Not sure if that's gonna work on every os. And if it doesn't, do let me know. :satisfied:

But overall I am *really* happy with the result! I already have more plans for tkinter... :heart:

## Compiling to .exe

`pyinstaller` works for this project, however it would not add tkinter.tkx to the package on its own.
To get a working .exe I ended up using:

`pyinstaller --add-data "tix8.4.3;tix8.4.3" -F -y -w --clean main.py`

Where "tix8.4.3" is a folder taken from my main Python installation with all of its contents and pasted into the same folder as main.py.
