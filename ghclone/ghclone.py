#!/usr/bin/env python3
'''
Interactively search GitHub repositories and clone them to the current directory
'''
import os
import curses
import curses.ascii
from threading import Thread
import requests

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

def tui(stdscr):
    ''' Main function. This must be called by curses.wrapper() '''
    init_curses(stdscr)
    draw_title(stdscr)
    search_input = create_searchbar(stdscr)
    repolist = create_repolist()
    draw_help(stdscr)

    curses.doupdate()

    while True:
        char = stdscr.getch()
        if char is KEY_EXIT:
            break
        elif char == KEY_CLONE:
            thread = Thread(target=clone, args=(repolist.current(),))
            thread.start()
            break
        elif char == KEY_SEARCH:
            search(search_input.value(), repolist)
            draw_nav_help(stdscr)
        elif char == KEY_BACK:
            search_input.delete()
        elif char == KEY_DOWN:
            repolist.selection_down()
        elif char == KEY_UP:
            repolist.selection_up()
        else:
            search_input.append(curses.keyname(char).decode('utf-8'))
        curses.doupdate()

def init_curses(win):
    ''' Configure curses '''
    curses.raw()
    curses.nonl()
    curses.curs_set(0)
    win.noutrefresh()

def draw_title(win):
    ''' Draw the title bar '''
    win.addstr('GitHub search', curses.A_BOLD | curses.A_REVERSE)
    win.chgat(-1, curses.A_BOLD | curses.A_REVERSE)

def create_searchbar(win):
    ''' Create the searchbar '''
    win.addstr(curses.LINES-2, 0, 'Search: ', curses.A_REVERSE)
    searchwin = curses.newwin(1, curses.COLS, curses.LINES-2, 8)
    search_input = SearchInput(searchwin)
    return search_input

def create_repolist():
    ''' Create the repo list '''
    repolistwin = curses.newwin(curses.LINES-4, curses.COLS - 2, 2, 1)
    repos = RepoList(repolistwin)
    return repos

def draw_help(win):
    ''' Draw the help '''
    win.addstr(curses.LINES-1, 0, 'Press \'Enter\' to search')

def draw_nav_help(win):
    ''' Draw the navigation help '''
    win.addstr(curses.LINES-1, 0, 'Use C-J/C-K to navigate, Press C-L to clone')

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
        self.win.noutrefresh()

    def append(self, char):
        ''' Append the character to the input '''
        self.query += char
        self.update()

    def delete(self):
        ''' Remove the last character '''
        self.query = self.query[:-1]
        self.update()

    def value(self):
        ''' Return the content '''
        return self.query

if __name__=='__main__':
    main()
