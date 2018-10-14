import tkinter as tk
import tkinter.font as tkf
import threading as th
from random import shuffle
from time import sleep
from webbrowser import open_new_tab


root = tk.Tk()
root.focus()
root.title('F1 for help  █  ←↑→↓, SPACE, CTRL/ALT')
default_underlined = tkf.Font(font='TkDefaultFont')
default_underlined.configure(underline=True)
defaultbg = root.cget('bg')
previous_board_info = []


def close_popup_delete_reference():
    about.destroy()
    del globals()['about']


def toggle_about(event_info_which_is_not_used):
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

        about_github_link = tk.Label(link1_frame, font=default_underlined, fg='blue',
                                     text='https://github.com/aszychlinski/tkinter_minesweeper')
        about_github_link.pack(side='left')
        about_github_link.bind("<Button-1>", open_github)
        about_github_link_desc = tk.Label(link1_frame, text='- view the repo page and sourcecode files')
        about_github_link_desc.pack(side='left')

        about_issues_link = tk.Label(link2_frame, font=default_underlined, fg='blue',
                                     text='https://github.com/aszychlinski/tkinter_minesweeper/issues')
        about_issues_link.pack(side='left')
        about_issues_link.bind("<Button-1>", open_issues)
        about_issues_link_desc = tk.Label(link2_frame, text='- issues, suggestions, feedback')
        about_issues_link_desc.pack(side='left')

        about.protocol("WM_DELETE_WINDOW", close_popup_delete_reference)


root.bind('<F1>', toggle_about)


class TimerThread(th.Thread):
    def __init__(self):
        th.Thread.__init__(self)
        self.value = 0
        self.restart = False

    def run(self):
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
    def __init__(self, master, text):
        self.label = tk.Label(master, text=text)
        self.label.pack(side='left')


class ConfigEntry:
    def __init__(self, master):
        self.entry = tk.Entry(master, justify='right')
        self.entry.pack(side='left')
        self.entry.insert(0, '0')


class ConfigConfirm:

    def __init__(self, master, text, preset, *args):
        self.button = tk.Button(master, command=self.forward_values, text=text)
        self.button.pack(side='left')
        self.bound_entries = args
        self.preset = preset

    def forward_values(self):
        global board
        global previous_board_info

        if 'board' in globals().keys():
            for x in board.buttons:
                x.button.destroy()
            for y in board.rows:
                y.frame.destroy()
            board.timer.restart = True
            board.start_helper.destroy()
            board.status_frame.destroy()
            board.gameframe.destroy()

        if self.preset:
            row_entry.entry.delete(0, 'end')
            row_entry.entry.insert(0, self.bound_entries[0])
            column_entry.entry.delete(0, 'end')
            column_entry.entry.insert(0, self.bound_entries[1])
            mines_entry.entry.delete(0, 'end')
            mines_entry.entry.insert(0, self.bound_entries[2])
            previous_board_info = [self.bound_entries[0], self.bound_entries[1], self.bound_entries[2]]
            FieldButton.game_over, FieldButton.revealed_buttons = False, 0
            board = BoardFactory(self.bound_entries[0], self.bound_entries[1], self.bound_entries[2])
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
                if int(self.bound_entries[0].entry.get()) > 18 or int(self.bound_entries[1].entry.get()) > 34:
                    errormessage = 'Argument exceeds maximum.'
                    raise ValueError
            except ValueError:
                error_label.label.config(text=errormessage, bg='red')
            else:
                values = []
                for x in self.bound_entries:
                    values.append(x.entry.get())
                rows, columns, mines = values
                previous_board_info = [rows, columns, mines]
                FieldButton.game_over, FieldButton.revealed_buttons = False, 0
                board = BoardFactory(rows, columns, mines)


class GameFrame(tk.Frame):
    def __repr__(self):
        return 'GameFrame'


class GameRow:
    def __init__(self, master, name):
        self.frame = tk.Frame(master=master, name=name)
        self.frame.pack(side='top')
        self.mybuttons = []
        self.rownum = 0

    def __str__(self):
        return f'GameRow {self.rownum}'

    def __repr__(self):
        return f'GameRow {self.rownum}'


class BoardFactory:
    def __init__(self, rows, columns, mines):
        self.target_rows = int(rows)
        self.target_columns, self.undistributed_columns = int(columns), int(columns)
        self.target_mines, self.undistributed_mines = int(mines), int(mines)
        self.target_buttons = self.target_rows * self.target_columns
        self.rows = []
        self.buttons, self.undistributed_buttons = [], []
        self.buttons_xy = {}
        self.flagged_buttons = 0
        self.button_uids = [*reversed(list(range(1, self.target_rows * self.target_columns + 1)))]
        self.generate_status_frame()
        self.gameframe = GameFrame(root)
        self.gameframe.pack(side='top')
        self.fieldbutton_under_restart_button = None
        self.make_rows()
        self.make_columns()
        self.distribute_mines()
        self.count_neighbours()
        self.map_buttons_xy()
        self.any_leftclicked = False
        self.start_helper = tk.Button(preset_frame, text='Free first move!', bg='green', command=self.free_first_move)
        self.start_helper.pack(side='left')
        self.start_helper.bind('<Down>', self.down_from_start_helper)
        error_label.label.config(text='', bg=defaultbg)
        self.start_helper.focus_set()

    def down_from_start_helper(self, event_info_which_could_be_used_but_isnt_because_were_handling_only_one_input):
        self.restart_button.button.focus_set()

    def arrows_from_restart(self, event_info_which_surprisingly_is_used):
        event_info = str(event_info_which_surprisingly_is_used).split(' ')
        direction = [x.replace('keysym=', '') for x in event_info if 'keysym=' in x][0]
        if direction == 'Up':
            self.start_helper.focus_set()
        elif direction == 'Down':
            self.fieldbutton_under_restart_button.button.focus_set()

    def generate_status_frame(self):
        self.status_frame = tk.Frame(root)
        self.remaining_mines_var = tk.IntVar()
        self.remaining_mines_var.set(self.target_mines - self.flagged_buttons)
        self.remaining_mines_txt = ConfigLabel(self.status_frame, 'Remaining mines: ')
        self.remaining_mines_amt = ConfigLabel(self.status_frame, '')
        self.remaining_mines_amt.label.config(textvariable=self.remaining_mines_var)

        self.timer = TimerThread()
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

        self.restart_button.button.bind('<Up>', self.arrows_from_restart)
        self.restart_button.button.bind('<Down>', self.arrows_from_restart)

        self.status_frame.pack(side='top', fill='x')

    def make_rows(self):
        for x in range(self.target_rows):
            name = 'r' + str(len(self.rows) + 1)
            self.rows.append(GameRow(self.gameframe, name))
            self.rows[-1].rownum = len(self.rows) - 1
            self.rows[-1].frame.pack(side='top')

    def make_columns(self):
        while self.undistributed_columns > 0:
            for x in self.rows:
                y = FieldButton(x, self.button_uids.pop())
                self.buttons.append(y)
                x.mybuttons.append(y.uid)
                y.button.pack(side='left')
            self.undistributed_columns -= 1
        for x in self.buttons:
            x.get_xpos()
        fieldbutton_under_restart_button_uid = self.rows[0].mybuttons[self.target_columns // 2]
        for x in self.buttons:
            if x.uid == fieldbutton_under_restart_button_uid:
                self.fieldbutton_under_restart_button = x

    def distribute_mines(self):
        shuffle(self.buttons)
        self.undistributed_buttons = self.buttons[:]
        while self.undistributed_mines > 0:
            temp = self.undistributed_buttons.pop()
            temp.contains_mine = True
            self.undistributed_mines -= 1

    def count_neighbours(self):
        for x in self.buttons:
            if x.contains_mine:
                pass
            else:
                none_above, none_below, none_left, none_right = False, False, False, False
                neighbours = []

                if x.x == 0:
                    none_left = True
                if x.x == self.target_columns - 1:
                    none_right = True
                if x.y == 0:
                    none_above = True
                if x.y == len(self.rows) - 1:
                    none_below = True

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

                for z in neighbours:
                    for a in self.buttons:
                        if a.uid == z:
                            x.neighbour_buttons.append(a)
                            if a.contains_mine:
                                x.neighbour_mines += 1

    def map_buttons_xy(self):
        for a in self.buttons:
            self.buttons_xy[str(a.x) + ',' + str(a.y)] = a

    def free_first_move(self):
        if not self.any_leftclicked:
            for x in sorted(self.buttons, key=lambda button: button.neighbour_mines):
                if x.contains_mine or x.clicks % 3 == 1:
                    continue
                else:
                    x.leftclick('dummy_event_info')
                    break

    def lose(self):
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
        FieldButton.game_over = True
        for x in self.buttons:
            if not x.revealed:
                x.button.config(text='P', bg='lawn green')
        self.remaining_mines_var.set(0)
        board.restart_button.button.config(text='C')


class FieldButton:

    game_over = False
    revealed_buttons = 0

    def __init__(self, master, uid):
        self.uid = 'b' + str(uid)
        self.revealed = False
        self.contains_mine = False
        self.clicks = 0
        self.neighbour_mines = 0
        self.neighbour_buttons = []
        self.neighbour_colours = {0: ['', 'gray85'], 1: [u'\u278A', 'steelblue1'], 2: [u'\u278B', 'palegreen'],
                                  3: [u'\u278C', 'salmon'], 4: [u'\u278D', 'navy'], 5: [u'\u278E', 'red4'],
                                  6: [u'\u278F', 'turquoise'], 7: [u'\u2790', 'black'], 8: [u'\u2791', 'gold']}
        self.master = master
        self.y = master.rownum
        self.x = 0
        self.click_pending = False
        self.click_aborted = False
        self.button = tk.Button(master.frame, height=1, width=2, bg='gray90', font='Wingdings', name=self.uid)
        self.button.pack()
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
        event_info = str(event_info_which_surprisingly_is_used).split(' ')
        direction = [x.replace('keysym=', '') for x in event_info if 'keysym=' in x]
        assert len(direction) == 1, 'Multiple directions in Fieldbutton.move_focus'  # not necessary but strangely fun
        direction = direction[0]
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
        if not self.game_over:
            self.click_pending = True
            board.restart_button.button.config(text='K')

    def abort_click(self, event_info_which_is_not_used):
        if self.click_pending and not self.game_over:
            self.click_aborted = True
            board.restart_button.button.config(text='J')

    def resolve_click(self, event_info_which_is_not_used):
        if self.click_pending and not self.click_aborted:
            self.leftclick('dummy_event_info')
            if not self.game_over:
                board.restart_button.button.config(text='J')
        else:
            self.click_pending, self.click_aborted = False, False

    def leftclick(self, event_info_which_is_not_used):
        border_set = set()
        if self.clicks % 3 == 1 or self.game_over or self.revealed:
            pass
        elif self.contains_mine:
            self.button.config(bg='red')
            board.lose()
        else:
            self.revealed = True
            self.__class__.revealed_buttons += 1
            self.button.config(relief='groove', state='disabled', text=self.neighbour_colours[self.neighbour_mines][0],
                               bg=self.neighbour_colours[self.neighbour_mines][1])
            if self.neighbour_mines == 0:
                for x in self.neighbour_buttons:
                    if x.neighbour_mines == 0 and not x.contains_mine and not x.revealed:
                        x.leftclick('dummy_event_info')
                    elif not x.contains_mine and not x.revealed:
                        border_set.add(x)
            for y in border_set:
                if not y.revealed:
                    y.leftclick('dummy_event_info')
            if not board.any_leftclicked:
                board.any_leftclicked = True
                board.timer.start()
                board.start_helper.config(relief='sunken', bg=defaultbg)
            if board.target_buttons - FieldButton.revealed_buttons == board.target_mines:
                board.win()

    def rightclick(self, event_info_which_is_not_used):
        if self.revealed or self.game_over:
            pass
        else:
            self.clicks += 1
            if self.clicks % 3 == 0:
                self.button.config(text='')
            if self.clicks % 3 == 1:
                board.flagged_buttons += 1
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
        self.x = self.master.mybuttons.index(self.uid)


preset_frame = tk.Frame(root)
preset_sizes = ConfigLabel(preset_frame, 'Preset sizes: ')
demo_size = ConfigConfirm(preset_frame, 'Demo', True, 10, 10, 5)
beginner_size = ConfigConfirm(preset_frame, 'Beginner', True, 9, 9, 10)
intermediate_size = ConfigConfirm(preset_frame, 'Intermediate', True, 16, 16, 40)
expert_size = ConfigConfirm(preset_frame, 'Expert', True, 16, 30, 99)
error_label = ConfigLabel(preset_frame, '')
error_label.label.pack(side='right')
preset_frame.pack(side='top', fill='x')

config_frame = tk.Frame(root)
row_label, row_entry = ConfigLabel(config_frame, 'Rows: '), ConfigEntry(config_frame)
column_label, column_entry = ConfigLabel(config_frame, 'Columns: '), ConfigEntry(config_frame)
mines_label, mines_entry = ConfigLabel(config_frame, 'Mines: '), ConfigEntry(config_frame)
config_confirm = ConfigConfirm(config_frame, 'Generate', False, row_entry, column_entry, mines_entry)
config_frame.pack(side='top', fill='x')


root.mainloop()
