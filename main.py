import tkinter as tk
import tkinter.font as tkf
import tkinter.tix as tkx
import threading as th
from random import shuffle
from time import sleep
from webbrowser import open_new_tab


# Creates the highest-level tkinter widget, a canvas of sorts.
root = tkx.Tk()
# Immediately places focus on the application, as if it were leftclicked.
# Added to fix an issue with tkinter.tix.Balloon, so it wouldn't be necessary if using only the default tkinter.
root.focus()
# Title bar text.
root.title('F1 for help  █  hover for tooltips  █  ←↑→↓, SPACE, CTRL/ALT')
# Creates a copy of the default font, difference being that all text written in this font will also be underlined.
# This font will be used for hyperlinks in the About popup.
default_underlined = tkf.Font(font='TkDefaultFont')
default_underlined.configure(underline=True)
# Establishes a handle on the default background colour, so that it can be used to "revert to default" a widget's bg.
defaultbg = root.cget('bg')
# Stores rows / columns / mines amounts for use with the Restart button.
previous_board_info = []


def close_popup_delete_reference():
    """Destroy About widget and delete its reference from the global namespace dictionary."""
    about.destroy()
    del globals()['about']

# event_info_which_is_not_used is something you'll see plenty of here.  When using the .bind method of a widget,
# in addition to launching the specified function, .bind also forces some event info onto that function as a positional
# argument. If not handled (received), there would be a TypeError caused by too many positional arguments.


def toggle_about(event_info_which_is_not_used):
    """Initiate destruction of About widget if one is present, otherwise generate one."""
    global about
    if 'about' in globals().keys():
        close_popup_delete_reference()
    else:
        def open_github(event_info_which_is_not_used):
            open_new_tab('https://github.com/aszychlinski/tkinter_minesweeper')

        def open_issues(event_info_which_is_not_used):
            open_new_tab('https://github.com/aszychlinski/tkinter_minesweeper/issues')

        about = tk.Toplevel(root)
        about.title('F1 to close help')
        about.bind('<F1>', toggle_about)
        about_main = tk.Label(
            about, justify='left', padx=10, pady=10,
            text='Left click a field to reveal it. Right click a field to flag it as containing a mine.'
                 '\n\nA revealed field may display a number. This number describes the amount of adjacent mines.'
                 '\nIf there is no number, there are no mines adjacent to this field; a chain reaction will occur.'
                 '\n\nYou win if every remaining unrevealed field contains a mine (they do not have to be flagged).'
                 '\n\nYou lose if you reveal a field containing a mine.'
                 '\n\nThe "Free first move!" button is available only if no field has been revealed yet.'
                 '\nIt reveals a randomly chosen field from among those containing the least adjacent mines.'
                 '\n\nThe yellow button above the game board generates a new board with the previously used values.'
                 '\n\n\nYou can also use the arrow keys to play! Once a board is generated, keyboard focus is on the'
                 '\n"Free first move!" button. Press Space to use the button, then use the down arrow to get down '
                 '\nfrom there onto the playing field. Spacebar to reveal a field, left CTRL or any ALT to flag.'
                 '\nFrom the top row of the minefield you can also get up onto the Restart and first move buttons.\n')
        about_main.pack(side='top')
        about_visit = tk.Label(about, text='Visit my GitHub!')
        about_visit.pack(side='top')
        link1_frame, link2_frame = tk.Frame(about), tk.Frame(about)
        link1_frame.pack(side='top', fill='x')
        link2_frame.pack(side='top', fill='x')

        # This is the first line containing a hyperlink.
        about_github_link = tk.Label(link1_frame, font=default_underlined, fg='blue',
                                     text='https://github.com/aszychlinski/tkinter_minesweeper')
        about_github_link.pack(side='left')
        about_github_link.bind("<Button-1>", open_github)
        about_github_link_desc = tk.Label(link1_frame, text='- view the repo page and sourcecode files')
        about_github_link_desc.pack(side='left')

        # This is the second line containing a hyperlink.
        about_issues_link = tk.Label(link2_frame, font=default_underlined, fg='blue',
                                     text='https://github.com/aszychlinski/tkinter_minesweeper/issues')
        about_issues_link.pack(side='left')
        about_issues_link.bind("<Button-1>", open_issues)
        about_issues_link_desc = tk.Label(link2_frame, text='- issues, suggestions, feedback')
        about_issues_link_desc.pack(side='left')

        # Defines a function to use when user clicks X button in top-right of About widget.
        # Tkinter provides a default window-closing mechanism, but I also needed to delete from globals().
        about.protocol("WM_DELETE_WINDOW", close_popup_delete_reference)


root.bind('<F1>', toggle_about)


class TimerThread(th.Thread):
    """A thread which counts seconds starting with 0 and until interrupted."""
    def __init__(self):
        th.Thread.__init__(self)
        # Amount of elapsed seconds.
        self.value = 0
        # The restart flag is set to True when the Restart button is pressed and terminates thread on next iteration.
        self.restart = False

    def run(self):
        """Count elapsed seconds and push the value to a tk.IntVar in the main thread."""
        while not FieldButton.game_over and not self.restart:
            sleep(1)
            if not FieldButton.game_over and not self.restart:
                self.value += 1
                try:
                    board.time_elapsed_var.set(self.value)
                except RuntimeError:
                    return None
        return None


class ConfigLabel:
    """A wrapper for tk.Label, which was meant to save me some typing."""
    def __init__(self, master, text):
        self.label = tk.Label(master, text=text)
        self.label.pack(side='left')


class ConfigEntry:
    """Another wrapper, this time for the text Entry fields. Inserts 0 by default."""
    def __init__(self, master):
        self.entry = tk.Entry(master, justify='right')
        self.entry.pack(side='left')
        self.entry.insert(0, '0')


class ConfigConfirm:
    """Wrapper for tk.Button which also passes row, column and mine amounts to BoardFactory."""

    def __init__(self, master, text, preset, *args):
        self.button = tk.Button(master, command=self.forward_values, text=text)
        self.button.pack(side='left')
        # Tuple of values taken from the three Entry fields.
        self.bound_entries = args
        # Boolean flag which controls flow based on whether values come from Entry fields or one of the preset buttons.
        self.preset = preset

    def forward_values(self):
        global board
        global previous_board_info

        # Cleans up after the previous board.  The two 'for' loops are likely unneeded as 'board.gameframe.destroy()'
        # should delete all of its children down through the master / slave hierarchy.  But I wanted to be sure.
        if 'board' in globals().keys():
            for x in board.buttons:
                x.button.destroy()
            for y in board.rows:
                y.frame.destroy()
            board.timer.restart = True
            board.start_helper.destroy()
            board.status_frame.destroy()
            board.gameframe.destroy()

        # If one of the preset buttons was pressed, delete whatever was written in the Entry fields, insert the preset
        # values, then immediately pass those values to BoardFactory (kinda like if Generate was pressed).
        if self.preset:
            row_entry.entry.delete(0, 'end')
            row_entry.entry.insert(0, self.bound_entries[0])
            column_entry.entry.delete(0, 'end')
            column_entry.entry.insert(0, self.bound_entries[1])
            mines_entry.entry.delete(0, 'end')
            mines_entry.entry.insert(0, self.bound_entries[2])
            previous_board_info = [self.bound_entries[0], self.bound_entries[1], self.bound_entries[2]]
            # Resets some class attributes of FieldButton to their initial states in preparation for a new game.
            FieldButton.game_over, FieldButton.revealed_buttons = False, 0
            board = BoardFactory(self.bound_entries[0], self.bound_entries[1], self.bound_entries[2])
        # If Generate was pressed...
        else:
            try:
                for x in self.bound_entries:
                    errormessage = 'Non-integer argument.'
                    int(x.entry.get())
                    if int(x.entry.get()) < 0:
                        errormessage = 'Negative argument.'
                        raise ValueError
                if int(self.bound_entries[0].entry.get())\
                        * int(self.bound_entries[1].entry.get())\
                        < int(self.bound_entries[2].entry.get()):
                    errormessage = 'More mines than fields.'
                    raise ValueError
                # These maximums are derived from how the game displayed on my 1920x1080 screen. :)
                # They represent the safe maximums under which the whole game board can always be displayed on screen.
                if int(self.bound_entries[0].entry.get()) > 18 or int(self.bound_entries[1].entry.get()) > 34:
                    errormessage = 'Argument exceeds maximum.'
                    raise ValueError
            # If any of the tests failed, pushes errormessage to error_label and does not proceed to Board generation.
            except ValueError:
                error_label.label.config(text=errormessage, bg='red')
            # Board creation approved!
            else:
                values = []
                for x in self.bound_entries:
                    values.append(x.entry.get())
                rows, columns, mines = values
                # Saves values of board about to be created, to use with Restart button.
                previous_board_info = [rows, columns, mines]
                # Resets some class attributes of FieldButton to their initial states in preparation for a new game.
                FieldButton.game_over, FieldButton.revealed_buttons = False, 0
                # Instances BoardFactory, which creates a new game board.
                board = BoardFactory(rows, columns, mines)


class GameFrame(tk.Frame):
    """A tk.Frame containing the minefield buttons that BoardFactory creates."""
    def __repr__(self):
        """This doesn't really do anything, I had it for debug purposes initially and don't want to refactor it."""
        return 'GameFrame'


class GameRow:
    """A tk.Frame representing a horizontal row on the game board."""
    def __init__(self, master, name):
        self.frame = tk.Frame(master=master, name=name)
        self.frame.pack(side='top')
        # A list of buttons in the row, into which - early in development - I decided to pass string id's of instanced
        # FieldButton objects instead of the whole objects themselves.  This was not the greatest idea.
        self.mybuttons = []
        self.rownum = 0

    def __str__(self):
        return f'GameRow {self.rownum}'

    def __repr__(self):
        return f'GameRow {self.rownum}'


class BoardFactory:
    """Create a brand new board."""
    def __init__(self, rows, columns, mines):
        # target_ attributes store the initial values and are meant to remain unchanged (as a reference).
        # undistributed_ attributes are modified in the course of board generation
        self.target_rows = int(rows)
        self.target_columns, self.undistributed_columns = int(columns), int(columns)
        self.target_mines, self.undistributed_mines = int(mines), int(mines)
        self.target_buttons = self.target_rows * self.target_columns
        # Contains GameRow instances.
        self.rows = []
        # Contain FieldButton instances.
        self.buttons, self.undistributed_buttons = [], []
        # Dictionary where comma-separated strings of button coordinates are keys and FieldButton instances are values.
        self.buttons_xy = {}
        self.flagged_buttons = 0
        # List from which Unique IDs of buttons will be taken (starting from 1).
        self.button_uids = [*reversed(list(range(1, self.target_rows * self.target_columns + 1)))]
        # Generates the frame containing Restart button.
        self.generate_status_frame()
        self.gameframe = GameFrame(root)
        self.gameframe.pack(side='top')
        # Will store the button instance which will receive focus after pressing the down arrow on Restart button.
        self.fieldbutton_under_restart_button = None
        self.make_rows()
        self.make_columns()
        self.distribute_mines()
        self.count_neighbours()
        self.map_buttons_xy()
        # Defines whether clicking "Free first move!" does anything.
        self.any_leftclicked = False
        # Generates and configures the "Free first move!" button.
        self.start_helper = tk.Button(preset_frame, text='Free first move!', bg='green', command=self.free_first_move)
        self.start_helper.pack(side='left')
        self.start_helper.bind('<Down>', self.down_from_start_helper)
        tooltip.bind_widget(self.start_helper, balloonmsg='Reveal a randomly chosen field from among those with the '
                                                          'least adjacent mines.\nAvailable only if no fields have been'
                                                          ' revealed yet.')
        error_label.label.config(text='', bg=defaultbg)
        # At very end of board creation places keyboard focus on the "Free first move!" button for user's convenience.
        self.start_helper.focus_set()

    def down_from_start_helper(self, event_info_which_could_be_used_but_isnt_because_were_handling_only_one_input):
        """Give focus to Restart button when down arrow is pressed on "Free first move!" button."""
        self.restart_button.button.focus_set()

    def arrows_from_restart(self, event_info_which_surprisingly_is_used):
        """Handle up / down arrow inputs from Restart button."""
        event_info = str(event_info_which_surprisingly_is_used).split(' ')
        # Parses the event info to extract direction identifier.
        direction = [x.replace('keysym=', '') for x in event_info if 'keysym=' in x][0]
        if direction == 'Up':
            self.start_helper.focus_set()
        elif direction == 'Down':
            self.fieldbutton_under_restart_button.button.focus_set()

    def generate_status_frame(self):
        """Generate horizontal bar with Restart buttton (directly above play area)."""
        self.status_frame = tk.Frame(root)
        # IntVar is a special kind of variable made available by tkinter. It pushes an update onto all widgets
        # displaying it whenever its value changes. This can save a lot of work with manually updating widgets.
        self.remaining_mines_var = tk.IntVar()
        self.remaining_mines_var.set(self.target_mines - self.flagged_buttons)
        self.remaining_mines_txt = ConfigLabel(self.status_frame, 'Remaining mines: ')
        self.remaining_mines_amt = ConfigLabel(self.status_frame, '')
        self.remaining_mines_amt.label.config(textvariable=self.remaining_mines_var)

        # Instances a TimerThread to go with the current board.
        self.timer = TimerThread()
        # TimerThread instance will write to this IntVar every second, which in turn refreshes the displayed value.
        self.time_elapsed_var = tk.IntVar()
        self.time_elapsed_var.set(0)
        self.time_elapsed_amt = ConfigLabel(self.status_frame, '')
        self.time_elapsed_amt.label.config(textvariable=self.time_elapsed_var)
        self.time_elapsed_amt.label.pack(side='right')
        self.time_elapsed_txt = ConfigLabel(self.status_frame, 'Time elapsed: ')
        self.time_elapsed_txt.label.pack(side='right')

        self.restart_button = ConfigConfirm(self.status_frame, 'J', True, *previous_board_info)
        self.restart_button.button.config(font='Wingdings', bg='yellow')
        self.restart_button.button.pack(side='top')
        tooltip.bind_widget(self.restart_button.button, balloonmsg='Restart game using current board attributes.')

        self.restart_button.button.bind('<Up>', self.arrows_from_restart)
        self.restart_button.button.bind('<Down>', self.arrows_from_restart)

        self.status_frame.pack(side='top', fill='x')

    def make_rows(self):
        """Create horizontal GameRow frames and stack them vertically."""
        for x in range(self.target_rows):
            # name serves as a basis for GameRow identifiers (ended up unused)
            name = 'r' + str(len(self.rows) + 1)
            self.rows.append(GameRow(self.gameframe, name))
            self.rows[-1].rownum = len(self.rows) - 1
            self.rows[-1].frame.pack(side='top')

    def make_columns(self):
        """Horizontally slide in buttons into rows, from right to left, making sure amount in each row is even."""
        while self.undistributed_columns > 0:
            for x in self.rows:
                # Here, buttons are instanced.  The 'y' handle is temporary and not preserved past an iteration.
                # Buttons are later referenced by their index in a list or .uid attribute if required.
                y = FieldButton(x, self.button_uids.pop())
                self.buttons.append(y)
                x.mybuttons.append(y.uid)
                y.button.pack(side='left')
            self.undistributed_columns -= 1
        # Defines the x (horizontal) position of each button in the grid by its index in the GameRow.mybuttons list.
        for x in self.buttons:
            x.get_xpos()
        # Finds the button that will take focus when down arrow is pressed from the Restart button.
        # This could've been prettier if I passed objects instead of uid's to GameRow.mybuttons.
        fieldbutton_under_restart_button_uid = self.rows[0].mybuttons[self.target_columns // 2]
        for x in self.buttons:
            if x.uid == fieldbutton_under_restart_button_uid:
                self.fieldbutton_under_restart_button = x

    def distribute_mines(self):
        """Distribute mines to random buttons."""
        shuffle(self.buttons)
        self.undistributed_buttons = self.buttons[:]
        while self.undistributed_mines > 0:
            # The next two lines could be merged and the temporary handle removed, but this form might be clearer.
            temp = self.undistributed_buttons.pop()
            temp.contains_mine = True
            self.undistributed_mines -= 1

    def count_neighbours(self):
        """Determines how many mine-bearing neighbours each button has."""
        for x in self.buttons:
            if x.contains_mine:
                pass
            else:
                none_above, none_below, none_left, none_right = False, False, False, False
                neighbours = []

                # First, based on x,y coordinates it is established if a button lies on any edge of the board.  This is
                # done to avoid exceptions later on.
                if x.x == 0:
                    none_left = True
                if x.x == self.target_columns - 1:
                    none_right = True
                if x.y == 0:
                    none_above = True
                if x.y == len(self.rows) - 1:
                    none_below = True

                # Based on proximity warnings (flags) established above, a "neighbours" list is now being created.
                # Starting from top-left above the button being processed and going left to right in rows, each
                # button.uid attribute is added to this list (not the instance itself).  Because of the flags the app
                # will never attempt to grab a nonexistant button.
                if not none_above and not none_left:
                    neighbours.append(self.rows[x.master.rownum - 1].mybuttons[x.x - 1])

                if not none_above:
                    neighbours.append(self.rows[x.master.rownum - 1].mybuttons[x.x])

                if not none_above and not none_right:
                    neighbours.append(self.rows[x.master.rownum - 1].mybuttons[x.x + 1])

                if not none_left:
                    neighbours.append(x.master.mybuttons[x.x - 1])

                if not none_right:
                    neighbours.append(x.master.mybuttons[x.x + 1])

                if not none_below and not none_left:
                    neighbours.append(self.rows[x.master.rownum + 1].mybuttons[x.x - 1])

                if not none_below:
                    neighbours.append(self.rows[x.master.rownum + 1].mybuttons[x.x])

                if not none_below and not none_right:
                    neighbours.append(self.rows[x.master.rownum + 1].mybuttons[x.x + 1])

                # Once the neighbours list is completed, its elements (button.uids) are compared to those in the
                # BoardFactory.buttons main list of buttons.  When the matched button instance contains a mine, the
                # neighbour_mines attribute of a FieldButton instance is incremented by one.  This is the main thing
                # which could've been more efficient if I passed button instances rather than uids to GameRow.mybuttons.
                for z in neighbours:
                    for a in self.buttons:
                        if a.uid == z:
                            x.neighbour_buttons.append(a)
                            if a.contains_mine:
                                x.neighbour_mines += 1

    def map_buttons_xy(self):
        """Generate a dictionary of x,y coordinates versus FieldButton instances used for arrow key navigation."""
        for a in self.buttons:
            self.buttons_xy[str(a.x) + ',' + str(a.y)] = a

    def free_first_move(self):
        """Click a semi-random field with the lowest possible amount of neighbouring mines."""
        if not self.any_leftclicked:
            for x in sorted(self.buttons, key=lambda button: button.neighbour_mines):
                if x.contains_mine or x.clicks % 3 == 1:
                    continue
                else:
                    x.leftclick('dummy_event_info')
                    break

    def lose(self):
        """Redraw board in reaction to player revealing a mine. Also blocks input to FieldButton instances."""
        # This flag prevents FieldButton.leftclick() and FieldButton.rightclick() from doing anything.
        FieldButton.game_over = True
        for x in self.buttons:
            if x.contains_mine:
                if x.clicks % 3 != 1:
                    x.button.config(text='M')
                else:
                    x.button.config(bg='lawn green')
            elif x.clicks % 3 == 1:
                x.button.config(fg='red', bg='black')
        board.restart_button.button.config(text='L')

    def win(self):
        """Redraw board in reaction to player revealing all safe fields. Also blocks input to FieldButton instances."""
        FieldButton.game_over = True
        for x in self.buttons:
            if not x.revealed:
                x.button.config(text='P', bg='lawn green')
        self.remaining_mines_var.set(0)
        board.restart_button.button.config(text='C')


class FieldButton:
    """Minefield button. Wrapper consisting of a tk.Button instance and a whole bunch of tacked-on attributes."""

    # Blocks leftclicks and rightclicks on FieldButtons once True.
    game_over = False
    # Used for checking if the game has been won.
    revealed_buttons = 0

    def __init__(self, master, uid):
        self.uid = 'b' + str(uid)
        self.revealed = False
        self.contains_mine = False
        # Counts amount of rightclicks performed on instance to determine current flag status.
        self.clicks = 0
        self.neighbour_mines = 0
        self.neighbour_buttons = []
        self.neighbour_colours = {0: ['', 'gray85'], 1: [u'\u278A', 'steelblue1'], 2: [u'\u278B', 'palegreen'],
                                  3: [u'\u278C', 'salmon'], 4: [u'\u278D', 'navy'], 5: [u'\u278E', 'red4'],
                                  6: [u'\u278F', 'turquoise'], 7: [u'\u2790', 'black'], 8: [u'\u2791', 'gold']}
        # The horizontal GameRow containing a FieldButton.
        self.master = master
        self.y = master.rownum
        self.x = 0
        self.click_pending = False
        self.click_aborted = False
        self.button = tk.Button(master.frame, height=1, width=2, bg='gray90', font='Wingdings', name=self.uid)
        self.button.pack()
        # The start -> abort / resolve mechanism allows a player to "back out" of a leftclick if the click is held down
        # and then moved away from the button. The smiley face on the Restart button also changes accordingly.
        self.button.bind("<Button-1>", self.start_click)
        self.button.bind("<Leave>", self.abort_click)
        self.button.bind("<ButtonRelease-1>", self.resolve_click)
        self.button.bind("<Button-3>", self.rightclick)
        self.button.bind("<Left>", self.move_focus)
        self.button.bind("<Up>", self.move_focus)
        self.button.bind("<Right>", self.move_focus)
        self.button.bind("<Down>", self.move_focus)
        self.button.bind("<space>", self.leftclick)
        self.button.bind("<Control_L>", self.rightclick)
        self.button.bind("<Alt_L>", self.rightclick)

    def __repr__(self):
        return self.uid

    def move_focus(self, event_info_which_surprisingly_is_used):
        """Traverse board using arrow keys."""
        event_info = str(event_info_which_surprisingly_is_used).split(' ')
        # Parses the event info to extract direction identifier.
        direction = [x.replace('keysym=', '') for x in event_info if 'keysym=' in x]
        assert len(direction) == 1, 'Multiple directions in Fieldbutton.move_focus'  # not necessary but strangely fun
        direction = direction[0]
        # Gets target button from BoardFactory.buttons_xy.  Exception handling is not required because movement is only
        # initiated if a button with the target coordinates is found.
        if direction == 'Left':
            target = str(self.x - 1) + ',' + str(self.y)
            if target in board.buttons_xy.keys():
                board.buttons_xy[target].button.focus_set()
        if direction == 'Up':
            target = str(self.x) + ',' + str(self.y - 1)
            if self.y == 0:
                board.restart_button.button.focus_set()
            elif target in board.buttons_xy.keys():
                board.buttons_xy[target].button.focus_set()
        if direction == 'Right':
            target = str(self.x + 1) + ',' + str(self.y)
            if target in board.buttons_xy.keys():
                board.buttons_xy[target].button.focus_set()
        if direction == 'Down':
            target = str(self.x) + ',' + str(self.y + 1)
            if target in board.buttons_xy.keys():
                board.buttons_xy[target].button.focus_set()

    def start_click(self, event_info_which_is_not_used):
        """Initiate a leftclick."""
        if not self.game_over:
            self.click_pending = True
            board.restart_button.button.config(text='K')

    def abort_click(self, event_info_which_is_not_used):
        """Abort an incomplete leftclick."""
        if self.click_pending and not self.game_over:
            self.click_aborted = True
            board.restart_button.button.config(text='J')

    def resolve_click(self, event_info_which_is_not_used):
        """Finalise an incomplete leftclick."""
        if self.click_pending and not self.click_aborted:
            self.leftclick('dummy_event_info')
            if not self.game_over:
                board.restart_button.button.config(text='J')
        else:
            self.click_pending, self.click_aborted = False, False

    def leftclick(self, event_info_which_is_not_used):
        """Handle a left mouse button click on a FieldButton instance."""
        # Contains fields which will be revealed at the end of a chain reaction (neighbour_mines != 0).
        border_set = set()
        if self.clicks % 3 == 1 or self.game_over or self.revealed:
            pass
        elif self.contains_mine:
            self.button.config(bg='red')
            board.lose()
        else:
            self.revealed = True
            self.__class__.revealed_buttons += 1
            # Visual configuration of a revealed, nonlethal field.
            self.button.config(relief='groove', state='disabled', text=self.neighbour_colours[self.neighbour_mines][0],
                               bg=self.neighbour_colours[self.neighbour_mines][1])
            # Chain reaction logic for when a button with no neighbouring mines is clicked.
            if self.neighbour_mines == 0:
                for x in self.neighbour_buttons:
                    if x.neighbour_mines == 0 and not x.contains_mine and not x.revealed:
                        x.leftclick('dummy_event_info')
                    elif not x.contains_mine and not x.revealed:
                        border_set.add(x)
            # Finalizes chain reaction.
            for y in border_set:
                if not y.revealed:
                    y.leftclick('dummy_event_info')
            # Starts timer and disables "Free first move!" if leftclick is first-in-game.
            if not board.any_leftclicked:
                board.any_leftclicked = True
                board.timer.start()
                board.start_helper.config(relief='sunken', bg=defaultbg)
            if board.target_buttons - FieldButton.revealed_buttons == board.target_mines:
                board.win()

    def rightclick(self, event_info_which_is_not_used):
        """Handle a right mouse button click on a FieldButton instance."""
        if self.revealed or self.game_over:
            pass
        else:
            self.clicks += 1
            if self.clicks % 3 == 0:
                self.button.config(text='')
            if self.clicks % 3 == 1:
                board.flagged_buttons += 1
                # Updates the "Remaining mines:" counter whenever flag amount changes.
                board.remaining_mines_var.set(board.target_mines - board.flagged_buttons)
                self.button.config(text='P')
                if board.remaining_mines_var.get() < 0:
                    board.remaining_mines_amt.label.config(fg='red')
            if self.clicks % 3 == 2:
                board.flagged_buttons -= 1
                board.remaining_mines_var.set(board.target_mines - board.flagged_buttons)
                self.button.config(text=u'\u2BD1')
                if board.remaining_mines_var.get() >= 0:
                    board.remaining_mines_amt.label.config(fg='black')

    def get_xpos(self):
        """Defines the x (horizontal) position of each button in the grid by its index in the GameRow.mybuttons list."""
        self.x = self.master.mybuttons.index(self.uid)


# Instances the top row of application (the one starting from "Preset sizes:").
preset_frame = tk.Frame(root)
preset_sizes = ConfigLabel(preset_frame, 'Preset sizes: ')
demo_size = ConfigConfirm(preset_frame, 'Demo', True, 10, 10, 5)
beginner_size = ConfigConfirm(preset_frame, 'Beginner', True, 9, 9, 10)
intermediate_size = ConfigConfirm(preset_frame, 'Intermediate', True, 16, 16, 40)
expert_size = ConfigConfirm(preset_frame, 'Expert', True, 16, 30, 99)
error_label = ConfigLabel(preset_frame, '')
error_label.label.pack(side='right')
preset_frame.pack(side='top', fill='x')

# Instances the second row of application (the one starting from "Rows:").
config_frame = tk.Frame(root)
row_label, row_entry = ConfigLabel(config_frame, 'Rows: '), ConfigEntry(config_frame)
column_label, column_entry = ConfigLabel(config_frame, 'Columns: '), ConfigEntry(config_frame)
mines_label, mines_entry = ConfigLabel(config_frame, 'Mines: '), ConfigEntry(config_frame)
config_confirm = ConfigConfirm(config_frame, 'Generate', False, row_entry, column_entry, mines_entry)
config_frame.pack(side='top', fill='x')

# Instances a single Balloon widget from tkinter.tix, which then serves all of the required locations.
# This is possible because the displayed text can be different depending on the bound widget.
tooltip = tkx.Balloon(root, initwait=750, bg=defaultbg)
tooltip.bind_widget(demo_size.button, balloonmsg='Rows: 10, Columns: 10, Mines: 5')
tooltip.bind_widget(beginner_size.button, balloonmsg='Rows: 9, Columns: 9, Mines: 10')
tooltip.bind_widget(intermediate_size.button, balloonmsg='Rows: 16, Columns: 16, Mines: 40')
tooltip.bind_widget(expert_size.button, balloonmsg='Rows: 16, Columns: 30, Mines: 99')
tooltip.bind_widget(row_entry.entry, balloonmsg='Amount of horizontal rows.\nMaximum of 18.')
tooltip.bind_widget(column_entry.entry, balloonmsg='Amount of vertical columns.\nMaximum of 34.')
tooltip.bind_widget(mines_entry.entry, balloonmsg='Amount of mines on the field.\nMaximum of 612.')
tooltip.bind_widget(config_confirm.button, balloonmsg='Generate a new board with the values given.')


root.mainloop()
# Thanks for reading!
