from cmd import Cmd

from sty import ef, fg, rs

welcome = ef.italic + fg.da_yellow + 'Welcome to' + rs.all
title = ef.bold + fg.da_green + 'ARKHAM HORROR' + rs.all
tag_line = fg.green + 'The Card Game' + rs.all
icons = '3👤 3📓 4✊🏼 2👞'

investigators = {
    'Roland': 'Roland Banks (Guardian, Core Set)',
    'Banks': 'Roland Banks (Guardian, Core Set)',
    'Daisy': 'Daisy Walker (Seeker, Core Set)',
    'Walker': 'Daisy Walker (Seeker, Core Set)',
    'Skids': '"Skids" O\'Toole (Rogue, Core Set)',
    '"Skids"': '"Skids" O\'Toole (Rogue, Core Set)',
    'O\'Toole': '"Skids" O\'Toole (Rogue, Core Set)',
    'Agnes': 'Agnes Baker (Mystic, Core Set)',
    'Baker': 'Agnes Baker (Mystic, Core Set)',
    'Wendy': 'Wendy Adams (Survivor, Core Set)',
    'Adams': 'Wendy Adams (Survivor, Core Set)',
}

selected = []


class Phase:
    def handle(self):
        raise NotImplementedError

    def next(self) -> 'Phase':
        raise NotImplementedError


class Lobby(Cmd, Phase):
    intro = '\n'.join(line for line in [welcome, title, tag_line, icons])
    prompt = '\n' + fg.li_red + '> ' + rs.all

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
        if arg not in investigators.values():
            print('Unknown investigator: select an investigator to add (double TAB to autocomplete).')
        elif arg in selected:
            print('%s has been already selected.' % arg)
        else:
            selected.append(arg)
            print('The following investigators have been selected:', *selected, sep='\n* ')

    def complete_add(self, text, line, start_index, end_index):
        completions = []
        for key, value in investigators.items():
            if value not in selected and (
                    not text or key.lower().startswith(text.lower())) and value not in completions:
                completions.append(value)

        return completions

    def do_remove(self, arg):
        """Remove the given investigator from the game."""
        if arg not in investigators.values():
            print('Unknown investigator: select an investigator to remove (double TAB to autocomplete).')
        elif arg not in selected:
            print('%s has not been selected.' % arg)
        else:
            selected.remove(arg)
            print('The following investigators have been selected:', *selected, sep='\n* ')

    def complete_remove(self, text, line, start_index, end_index):
        completions = []
        for value in selected:
            if (not text or value.lower().startswith(text.lower())) and value not in completions:
                completions.append(value)

        return completions

    def do_list(self, arg):
        """List the investigators available to select."""
        available = []
        for investigator in investigators.values():
            if investigator not in selected and investigator not in available:
                available.append(investigator)
        print('The following investigators are available to be selected:', *available, sep='\n* ')

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
