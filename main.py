import tkinter as tk
from random import shuffle


root = tk.Tk()
root.title('mine')  # TODO: add proper title
previous_board_info = []


class ConfigLabel:
    def __init__(self, master, text):
        self.label = tk.Label(master, text=text)
        self.label.pack(side='left')


class ConfigEntry:
    def __init__(self, master):
        self.entry = tk.Entry(master, justify='right')
        self.entry.pack(side='left')
        self.entry.insert(0, '0')
        ConfigConfirm.start_items.append(self)


class ConfigConfirm:

    start_items = []  # TODO: revert in preparation for reset and destroy

    def __init__(self, master, text, preset, *args):
        self.button = tk.Button(master, command=self.forward_values, text=text)
        self.button.pack(side='left')
        self.bound_entries = args
        self.preset = preset
        self.__class__.start_items.append(self)

    def forward_values(self):
        global board
        global previous_board_info

        # def disable_all_start_buttons():
        #     for y in ConfigConfirm.start_items:
        #         try:
        #             y.button.config(state='disabled')
        #         except AttributeError:
        #             y.entry.config(state='disabled')
        if 'board' in globals().keys():
            for x in board.buttons:
                x.button.destroy()
            for y in board.rows:
                y.destroy()
            board.status_frame.destroy()
            board.gameframe.destroy()
            del board

        if self.preset:
            row_entry.entry.delete(0, 'end')  # TODO: is it necessary to keep it in an if when I am forwarding to entry?
            row_entry.entry.insert(0, self.bound_entries[0])
            column_entry.entry.delete(0, 'end')
            column_entry.entry.insert(0, self.bound_entries[1])
            mines_entry.entry.delete(0, 'end')
            mines_entry.entry.insert(0, self.bound_entries[2])
            # disable_all_start_buttons()
            previous_board_info = [self.bound_entries[0], self.bound_entries[1], self.bound_entries[2]]
            board = BoardFactory(self.bound_entries[0], self.bound_entries[1], self.bound_entries[2])
        else:
            try:
                for x in self.bound_entries:
                    int(x.entry.get())
            except ValueError:
                pass
            else:
                # disable_all_start_buttons()
                values = []
                for x in self.bound_entries:
                    values.append(x.entry.get())
                rows, columns, mines = values
                previous_board_info = [rows, columns, mines]
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
        self.rows = []
        self.columns = []  # not used?
        self.buttons, self.undistributed_buttons, self.lethal_buttons = [], [], []
        self.flagged_buttons = 0
        self.button_uids = [*reversed(list(range(1, self.target_rows * self.target_columns + 1)))]
        self.gameframe = GameFrame(root)
        self.generate_status_frame()
        self.make_rows()
        self.make_columns()
        self.distribute_mines()
        self.count_neighbours()
        # debug
        print(self.button_uids, '<- ok if empty')
        # for x in self.buttons: print(x.y)
        for x in self.rows: print (x.mybuttons)
        # print(self.target_columns)

    def generate_status_frame(self):
        self.status_frame = tk.Frame(root)
        self.remaining_mines_var = tk.IntVar()
        self.remaining_mines_var.set(self.target_mines - self.flagged_buttons)
        self.remaining_mines_txt = ConfigLabel(self.status_frame, 'Remaining mines: ')
        self.remaining_mines_amt = ConfigLabel(self.status_frame, '')
        self.remaining_mines_amt.label.config(textvariable=self.remaining_mines_var)

        self.time_elapsed_amt = ConfigLabel(self.status_frame, '99')
        self.time_elapsed_amt.label.pack(side='right')
        self.time_elapsed_txt = ConfigLabel(self.status_frame, 'Time elapsed: ')
        self.time_elapsed_txt.label.pack(side='right')

        self.restart_button = ConfigConfirm(self.status_frame, '\u263A', True, *previous_board_info)
        self.restart_button.button.config(font='Wingdings')
        self.restart_button.button.pack(side='top')

        self.status_frame.pack(side='top',  fill='x')

    def make_rows(self):
        for x in range(self.target_rows):
            self.rows.append(GameRow(self.gameframe))
            self.rows[-1].rownum = len(self.rows) - 1
            self.rows[-1].pack(side='top')
        # self.gameframe.pack(side='left')  # TODO: this does nothing!

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


class FieldButton:
    def __init__(self, master, uid):
        self.uid = 'b' + str(uid)
        self.revealed = False
        self.lethal = False
        self.clicks = 0
        self.neighbour_mines = 0
        self.neighbour_buttons = []
        self.block_recursion = False
        self.glyphs = ['', u'\u278A', u'\u278B', u'\u278C', u'\u278D', u'\u278E', u'\u278F', u'\u2790', u'\u2791']
        self.master = master
        self.y = master.rownum
        self.x = 0
        self.button = tk.Button(master, height=1, width=2, font='Wingdings')
        self.button.pack()  # TODO: figure if this should be outside the class; 26.08 - probably not?
        self.button.bind("<Button-1>", self.leftclick)
        self.button.bind("<Button-3>", self.rightclick)

    def __repr__(self):
        return self.uid

    def leftclick(self, event_info_which_is_not_used):
        border_list = []
        if self.clicks % 3 == 1:
            pass
        elif self.lethal:
            # TODO: def die()
            self.button.config(bg='red', text='M')  # TODO: does Wingdings work on non-Win OS's?
        else:
            self.revealed = True
            self.block_recursion = True
            self.button.config(relief='groove', state='disabled', text=self.glyphs[self.neighbour_mines])
            if self.neighbour_mines == 0:
                for x in self.neighbour_buttons:
                    if x.neighbour_mines == 0 and not x.lethal and not x.block_recursion:
                        x.leftclick('')
                    elif not x.lethal and not x.block_recursion:
                        border_list.append(x)
            for y in border_list:
                y.leftclick('')
            print(self.uid, self.x, self.y, print(self.neighbour_buttons), self.neighbour_mines)

    def rightclick(self, event_info_which_is_not_used):
        if self.revealed:
            pass
        else:
            self.clicks += 1
            if self.clicks % 3 == 0:
                self.button.config(text='')
            if self.clicks % 3 == 1:
                self.button.config(text='P')
                board.flagged_buttons += 1
                board.remaining_mines_var.set(board.target_mines - board.flagged_buttons)
            if self.clicks % 3 == 2:
                board.flagged_buttons -= 1
                board.remaining_mines_var.set(board.target_mines - board.flagged_buttons)
                self.button.config(text=u'\u2BD1')

    def get_xpos(self):
        self.x = self.master.mybuttons.index(self.uid)


# top-of-screen config area TODO: move it somewhere else?
preset_frame = tk.Frame(root)
preset_sizes = ConfigLabel(preset_frame, 'Preset sizes: ')
beginner_size = ConfigConfirm(preset_frame, 'Beginner', True, 9, 9, 10)
intermediate_size = ConfigConfirm(preset_frame, 'Intermediate', True, 16, 16, 40)
expert_size = ConfigConfirm(preset_frame, 'Expert', True, 16, 30, 99)
preset_frame.pack(side='top', fill='x')

config_frame = tk.Frame(root)
row_label, row_entry = ConfigLabel(config_frame, 'Rows: '), ConfigEntry(config_frame)
column_label, column_entry = ConfigLabel(config_frame, 'Columns: '), ConfigEntry(config_frame)
mines_label, mines_entry = ConfigLabel(config_frame, 'Mines: '), ConfigEntry(config_frame)
config_confirm = ConfigConfirm(config_frame, 'Generate', False, row_entry, column_entry, mines_entry)
config_frame.pack(side='top', fill='x')

root.mainloop()
