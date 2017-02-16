# -*- coding: utf-8 -*-

# PAINT-IT
# A console clone of 'flood-it' written in Python.
# Copyright (C) 2017 by Giovanni Nunes <giovanni.nunes@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
from __future__ import print_function
import curses
import random

__author__ = 'Giovanni Nunes'
__version__ = '1'

COLORS = 6
WINDOW = 24

class Game:
    arena = []
    arena_size = 0
    max_moves = 0
    moves = 0
    moves_position=[]
    offset_x=0
    offset_y=0
    status = 'play'
    title="PAINT-IT"
    window_size = [24, 80]

    helper=[ "*** HELP ***",
             "----------------------",
             "Use: (B)lue, (C)yan,",
             "(G)reen, (M)agenta,",
             "(R)ed or (Y)ellow.",
             "<CTRL>+<X> to exit",
             "----------------------",
             "<ESC> to return" ]

    def __init__(self, arena_size):
        self.arena_size = arena_size
        self.max_moves = int(25*(2*arena_size*COLORS)/(28*6))
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        try:
            curses.curs_set(False)
        except curses.error:
            pass
        self.screen.nodelay(True)
        self.window_size = self.screen.getmaxyx()

        if self.window_size[0] < self.arena_size+4 or self.window_size[1] < self.arena_size*2:
            print('Your screen is too short!')
            exit()

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_CYAN)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_YELLOW)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_WHITE)

        self.offset_x = int((self.window_size[1]-2*self.arena_size)/2)
        self.offset_y = int((self.window_size[0]-self.arena_size)/2)
        self.moves_position=[ self.offset_y+self.arena_size+1, self.offset_x+self.arena_size-5 ]

        self.arena_initialize()

        self.screen.addstr( self.offset_y-2, self.offset_x, self.title, curses.color_pair(0))
        self.screen.addstr( self.offset_y-2, self.offset_x+2*self.arena_size-17, "Press '?' to help", curses.color_pair(0))

    def arena_initialize(self):
        for y in range(self.arena_size):
            self.arena.append([])
            for x in range(self.arena_size):
                self.arena[y].append( random.randint(1,6) )

    def check_game(self):
        if self.moves > self.max_moves:
            self.status='lose'
            self.screen.addstr( self.moves_position[0], self.offset_x, "YOU LOSE!", curses.color_pair(4))
        else:
            self.status='win'
            color = self.arena[0][0]
            for y in range(self.arena_size):
                for x in range(self.arena_size):
                    if self.arena[y][x] != color:
                        self.status='play'
                        break;
        if self.status=='win' and self.moves<=self.max_moves:
            self.screen.addstr( self.moves_position[0], self.offset_x, "YOU WIN!", curses.color_pair(2))

    def display_help(self):
        for y in range(len(self.helper)):
            x = int((self.arena_size*2-WINDOW)/2)
            self.screen.addstr( self.offset_y + 1 + y, self.offset_x + x, " "*WINDOW, curses.color_pair(0))
            x = int((self.arena_size*2-len(self.helper[y]))/2)
            self.screen.addstr( self.offset_y + 1 + y, self.offset_x + x, self.helper[y], curses.color_pair(0))
        while self.screen.getch()!=27:
            pass

    def get_key(self):
        input_key = self.screen.getch()
        if input_key == ord('b'):       # blue
            color=1
        elif input_key == ord('g'):     # green
            color=2
        elif input_key == ord('c'):     # cyan
            color=3
        elif input_key == ord('r'):     # red
            color=4
        elif input_key == ord('m'):     # magenta
            color=5
        elif input_key == ord('y'):     # yellow
            color=6
        elif input_key == ord('w'):     # white
            color=7
        elif input_key == ord('?'):     # help, '?'
            color=-1
        elif input_key == 24:           # exit, <CTRL>+<X>
            color=-2
        else:
            color=0
        return color

    def paint(self, home, old_color, new_color):
        '''
            Based on JS code written by Jan Wolter -- http://unixpapa.com/floodit/
        '''
        new_home=[]
        while len(home)>0:
            x = home.pop()
            y = home.pop()

            if self.arena[y][x] == old_color:
                self.arena[y][x] = new_color

                if (x<self.arena_size-1) and (self.arena[y][x+1]==old_color):
                    new_home.extend([y, x+1])

                if (y<self.arena_size-1) and (self.arena[y+1][x]==old_color):
                    new_home.extend([y+1, x])

                if (x>0) and (self.arena[y][x-1]==old_color):
                    new_home.extend([y, x-1])

                if (y>0) and (self.arena[y-1][x]==old_color):
                    new_home.extend([y-1, x])

        if len(new_home)>0:
            self.paint(new_home, old_color, new_color)
        else:
            self.check_game()

    def refresh_screen(self):
        for y in range(self.arena_size):
            for x in range(self.arena_size):
                try:
                    self.screen.addstr( self.offset_y + y, self.offset_x + x*2, "  ", curses.color_pair( self.arena[y][x] ))
                except curses.error:
                    pass
        self.screen.addstr( self.moves_position[0], self.moves_position[1], "Moves {}/{} ".format(self.moves,self.max_moves), curses.color_pair(0))
        self.screen.refresh()

def main():
    game = Game(16)

    while True:
        game.refresh_screen()
        new_color = game.get_key()
        if new_color > 0 and new_color <= COLORS and game.status!='win':
            old_color = game.arena[0][0]
            if new_color != old_color:
                game.moves+=1
                game.paint( [0,0], old_color, new_color)
        elif new_color==-2:
            break
        elif new_color==-1:
            game.display_help()

    game.screen.keypad(False)
    curses.nocbreak()
    curses.echo()
    curses.endwin()

    print('Thanks for playing!')
    exit()

if __name__ == "__main__":
    main()
