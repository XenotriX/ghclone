#!/usr/bin/env python3
'''
Interactively search GitHub repositories and clone them to the current directory
'''
import os
import curses
import curses.ascii
from threading import Thread
import requests
from sys import exit

''' Constants '''
# Github API url
URL = 'https://api.github.com/search/repositories?q='

# Keys
KEY_BACK = curses.KEY_BACKSPACE
KEY_EXIT = curses.ascii.ctrl(ord('c'))
KEY_DOWN = curses.ascii.ctrl(ord('j'))
KEY_UP = curses.ascii.ctrl(ord('k'))
KEY_CLONE = curses.ascii.ctrl(ord('l'))
KEY_SEARCH = curses.ascii.ctrl(ord('m'))

STATUS_SEARCH = 'Press \'Enter\' to search'
STATUS_NAV = 'Use C-J/C-K to navigate, Press C-L to clone'
STATUS_LOADING = 'Loading...'


def tui(stdscr):
    ''' Main function. This must be called by curses.wrapper() '''
    init_curses(stdscr)
    search_input = create_searchbar(stdscr)
    repolist = create_repolist()
    draw_status(stdscr, STATUS_SEARCH)

    curses.doupdate()

    while True:
        char = stdscr.getch()
        if char is KEY_EXIT:
            exit(1)
        elif char == KEY_CLONE:
            thread = Thread(target=clone, args=(repolist.current(),))
            thread.start()
            break
        elif char == KEY_SEARCH:
            draw_status(stdscr, STATUS_LOADING)
            search(search_input.value(), repolist)
            draw_status(stdscr, STATUS_NAV)
        elif char == KEY_BACK:
            search_input.delete()
        elif char == KEY_DOWN:
            repolist.selection_down()
        elif char == KEY_UP:
            repolist.selection_up()
        else:
            search_input.append(curses.keyname(char).decode('utf-8'))
        search_input.update()
        curses.doupdate()


def init_curses(win):
    ''' Configure curses '''
    curses.raw()
    curses.nonl()
    curses.use_default_colors()
    win.noutrefresh()


def create_searchbar(win):
    ''' Create the searchbar '''
    win.addstr(0, 0, 'Search: ', curses.A_BOLD | curses.A_REVERSE)
    searchwin = curses.newwin(1, curses.COLS, 0, 8)
    search_input = SearchInput(searchwin)
    return search_input


def create_repolist():
    ''' Create the repo list '''
    repolistwin = curses.newwin(curses.LINES-4, curses.COLS - 2, 2, 1)
    repos = RepoList(repolistwin)
    return repos


def draw_status(win, string):
    ''' Update the status in the bottom line '''
    cursor_pos = curses.getsyx()
    win.move(curses.LINES-1, 0)
    win.clrtoeol()
    win.addstr(curses.LINES-1, 0, string)
    win.noutrefresh()
    curses.setsyx(*cursor_pos)
    curses.doupdate()


def search(query, repos):
    ''' Query the api and show the results '''
    query = '+'.join(query.split())
    data = requests.get(URL + query).json()
    repolist = [repo['full_name'] for repo in data['items']]
    repos.set_repos(repolist)
    curses.doupdate()


def clone(repo):
    ''' Clone the given repository '''
    os.system('git clone https://github.com/' + repo)


def main():
    curses.wrapper(tui)


class RepoList:
    ''' Repository list widget '''

    def __init__(self, win):
        self.win = win
        self.selected = 0
        self.repos = []

    def set_repos(self, repos):
        ''' Set the list of repositories to display '''
        self.repos = repos
        self.selected = 0
        self.update()

    def update(self):
        ''' Update the TUI '''
        self.win.clear()
        if self.repos:
            for index, repo in enumerate(self.repos):
                if index > self.win.getmaxyx()[0] - 2:
                    break
                self.win.addstr(index, 0, repo)
            self.win.addstr(self.selected, curses.COLS-3, '>')
            self.win.chgat(self.selected, 0, -1, curses.A_REVERSE)
        else:
            self.win.addstr(0, 0, "No results")
        self.win.noutrefresh()

    def selection_up(self):
        ''' Move the selection up '''
        self.win.chgat(self.selected, 0, -1, curses.A_NORMAL)
        self.selected = max(self.selected - 1, 0)
        self.update()

    def selection_down(self):
        ''' Move the selection down '''
        self.win.chgat(self.selected, 0, -1, curses.A_NORMAL)
        self.selected = min(self.selected + 1, len(self.repos))
        self.update()

    def current(self):
        ''' Return the current repository '''
        return self.repos[self.selected]


class SearchInput:
    ''' Search field widget '''

    def __init__(self, win):
        self.query = ''
        self.win = win
        self.win.chgat(0, 0, -1, curses.A_REVERSE)
        self.win.noutrefresh()

    def update(self):
        ''' Update the TUI '''
        self.win.clear()
        self.win.addstr(0, 0, self.query)
        self.win.chgat(0, 0, -1, curses.A_REVERSE)
        self.win.move(0, len(self.query))
        self.win.noutrefresh()

    def append(self, char):
        ''' Append the character to the input '''
        self.query += char

    def delete(self):
        ''' Remove the last character '''
        self.query = self.query[:-1]

    def value(self):
        ''' Return the content '''
        return self.query


if __name__ == '__main__':
    main()
