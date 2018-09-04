from cmd import Cmd

from sty import ef, fg, rs

from arkham.investigators import pool

welcome = ef.italic + fg.da_yellow + 'Welcome to' + rs.all
title = ef.bold + fg.da_green + 'ARKHAM HORROR' + rs.all
tag_line = fg.green + 'The Card Game' + rs.all
icons = '3👤 3📓 4✊🏼 2👞'

selected = []


class Phase:
    def handle(self):
        raise NotImplementedError

    def next(self) -> 'Phase':
        raise NotImplementedError


class Lobby(Cmd, Phase):
    intro = 'Welcome to ARKHAM HORROR The Card Game'
    prompt = '\n> '

    def __init__(self, game: 'Game', completekey='tab', stdin=None, stdout=None):
        super().__init__(completekey, stdin, stdout)
        self.game = game

    def handle(self):
        self.cmdloop()

    def next(self) -> Phase:
        pass

    def do_quit(self, arg):
        """Quit the game."""
        return True

    def do_add(self, arg):
        """Add the given investigator to the game."""
        for investigator in pool.investigators:
            if arg == str(investigator):
                if investigator in selected:
                    print('%s has been already selected.' % arg)
                else:
                    selected.append(investigator)
                    print('%s has been selected.' % arg)
                    print()
                    self._print_selected()
                return

        print('Unknown investigator: select an investigator to add (double TAB to autocomplete).')

    def complete_add(self, text, line, start_index, end_index):
        completions = []
        for word, investigator in pool.get_completion().items():
            if investigator not in selected:
                value = str(investigator)
                if (not text or word.startswith(text.lower())) and value not in completions:
                    completions.append(value)

        return completions

    def do_remove(self, arg):
        """Remove the given investigator from the game."""
        for investigator in pool.investigators:
            if arg == str(investigator):
                if investigator in selected:
                    selected.remove(investigator)
                    print('%s has been deselected.' % arg)
                    print()
                    self._print_selected()
                else:
                    print('%s was not selected.' % arg)
                return

        print('Unknown investigator: select an investigator to remove (double TAB to autocomplete).')

    def complete_remove(self, text, line, start_index, end_index):
        completions = []
        for word, investigator in pool.get_completion().items():
            if investigator in selected:
                value = str(investigator)
                if (not text or word.startswith(text.lower())) and value not in completions:
                    completions.append(value)

        return completions

    def do_list(self, arg):
        """List the investigators available to select."""
        self._print_selected()
        self._print_available()

    def _print_selected(self):
        if not selected:
            print('No investigator is currently selected.')
        else:
            print('The following investigators are currently selected:')
            for selection in selected:
                print('* %s' % str(selection))

    def _print_available(self):
        available = [investigator for investigator in pool.investigators if investigator not in selected]
        if available:
            print()
            print('The following investigators are available for selection:')
            for investigator in available:
                print('* %s' % str(investigator))

    def do_start(self):
        """Start the game."""
        return True


class Game:
    def __init__(self):
        self.phase = Lobby(self)
        self.phase.handle()

    def next(self):
        self.phase = self.phase.advance()
        self.phase.handle()
