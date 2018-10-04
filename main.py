import tkinter as tk
import threading as th
from random import shuffle
from time import sleep


root = tk.Tk()
root.title('mine')  # TODO: add proper title
defaultbg = root.cget('bg')
previous_board_info = []


class TimerThread(th.Thread):
    def __init__(self):
        th.Thread.__init__(self)
        self.value = 0
        self.exit = False

    def run(self):
        while not FieldButton.game_over and not self.exit:
            sleep(1)
            if not FieldButton.game_over and not self.exit:
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
                y.destroy()
            board.timer.exit = True
            board.start_helper.destroy()
            board.status_frame.destroy()
            board.gameframe.destroy()

        if self.preset:
            row_entry.entry.delete(0, 'end')  # TODO: is it necessary to keep it in an if when I am forwarding to entry?
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
                    int(x.entry.get())
                    if int(x.entry.get()) < 0:
                        raise ValueError
                if int(self.bound_entries[0].entry.get())\
                        * int(self.bound_entries[1].entry.get())\
                        < int(self.bound_entries[2].entry.get()):
                    raise ValueError
            except ValueError:
                pass  # TODO: implement label describing nature of error
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


class GameRow(tk.Frame):
    def __init__(self, master=None, cnf={}, **kw):  # TODO: this is likely wrong :(
        super().__init__()
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
        self.columns = []  # not used?
        self.buttons, self.undistributed_buttons, self.lethal_buttons = [], [], []  # lethal_buttons not used?
        self.flagged_buttons = 0
        self.button_uids = [*reversed(list(range(1, self.target_rows * self.target_columns + 1)))]
        self.gameframe = GameFrame(root)
        self.generate_status_frame()
        self.make_rows()
        self.make_columns()
        self.distribute_mines()
        self.count_neighbours()
        self.any_leftclicked = False
        self.start_helper = tk.Button(preset_frame, text='Free first move!', bg='green', command=self.free_first_move)
        self.start_helper.pack(side='left')

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

        self.status_frame.pack(side='top', fill='x')

    def make_rows(self):
        for x in range(self.target_rows):
            self.rows.append(GameRow(self.gameframe))
            self.rows[-1].rownum = len(self.rows) - 1
            self.rows[-1].pack(side='top')

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

    def distribute_mines(self):
        shuffle(self.buttons)
        self.undistributed_buttons = self.buttons[:]
        while self.undistributed_mines > 0:
            temp = self.undistributed_buttons.pop()
            temp.lethal = True
            self.lethal_buttons.append(temp)
            self.undistributed_mines -= 1

    def count_neighbours(self):
        for x in self.buttons:
            if x.lethal:
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
                            if a.lethal:
                                x.neighbour_mines += 1

    def free_first_move(self):
        if not self.any_leftclicked:
            for x in sorted(self.buttons, key=lambda button: button.neighbour_mines):
                if x.lethal or x.clicks % 3 == 1:
                    continue
                else:
                    x.leftclick()
                    break

    def lose(self):
        FieldButton.game_over = True
        for x in self.buttons:
            if x.lethal:
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
        self.lethal = False
        self.clicks = 0
        self.neighbour_mines = 0
        self.neighbour_buttons = []
        self.block_recursion = False
        self.neighbour_colours = {0: ['', 'gray85'], 1: [u'\u278A', 'steelblue1'], 2: [u'\u278B', 'palegreen'],
                                  3: [u'\u278C', 'salmon'], 4: [u'\u278D', 'navy'], 5: [u'\u278E', 'red4'],
                                  6: [u'\u278F', 'turquoise'], 7: [u'\u2790', 'black'], 8: [u'\u2791', 'gold']}
        self.master = master
        self.y = master.rownum
        self.x = 0
        self.click_pending = False
        self.click_aborted = False
        self.button = tk.Button(master, height=1, width=2, bg='gray90', font='Wingdings')
        self.button.pack()
        self.button.bind("<Button-1>", self.start_click)
        self.button.bind("<Leave>", self.abort_click)
        self.button.bind("<ButtonRelease-1>", self.resolve_click)
        self.button.bind("<Button-3>", self.rightclick)

    def __repr__(self):
        return self.uid

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
            self.leftclick()
            if not self.game_over:
                board.restart_button.button.config(text='J')
        else:
            self.click_pending, self.click_aborted = False, False

    def leftclick(self):
        border_set = set()
        if self.clicks % 3 == 1 or self.game_over or self.revealed:
            pass
        elif self.lethal:
            self.button.config(bg='red')
            board.lose()
        else:
            self.revealed = True
            self.__class__.revealed_buttons += 1
            self.block_recursion = True  # TODO: investigate if this is still needed
            self.button.config(relief='groove', state='disabled', text=self.neighbour_colours[self.neighbour_mines][0],
                               bg=self.neighbour_colours[self.neighbour_mines][1])
            if self.neighbour_mines == 0:
                for x in self.neighbour_buttons:
                    if x.neighbour_mines == 0 and not x.lethal and not x.block_recursion:
                        x.leftclick()
                    elif not x.lethal and not x.block_recursion:
                        border_set.add(x)
            for y in border_set:
                if not y.revealed:
                    y.leftclick()
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


# top-of-screen config area
preset_frame = tk.Frame(root)
preset_sizes = ConfigLabel(preset_frame, 'Preset sizes: ')
demo_size = ConfigConfirm(preset_frame, 'Demo', True, 10, 10, 5)
beginner_size = ConfigConfirm(preset_frame, 'Beginner', True, 9, 9, 10)
intermediate_size = ConfigConfirm(preset_frame, 'Intermediate', True, 16, 16, 40)
my_size = ConfigConfirm(preset_frame, '1920x1080 fullscreen', True, 23, 40, 99)
expert_size = ConfigConfirm(preset_frame, 'Expert', True, 16, 30, 99)
preset_frame.pack(side='top', fill='x')

config_frame = tk.Frame(root)
row_label, row_entry = ConfigLabel(config_frame, 'Rows: '), ConfigEntry(config_frame)
column_label, column_entry = ConfigLabel(config_frame, 'Columns: '), ConfigEntry(config_frame)
mines_label, mines_entry = ConfigLabel(config_frame, 'Mines: '), ConfigEntry(config_frame)
config_confirm = ConfigConfirm(config_frame, 'Generate', False, row_entry, column_entry, mines_entry)
config_frame.pack(side='top', fill='x')

root.mainloop()
