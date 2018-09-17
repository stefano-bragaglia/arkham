from random import choice, randint
from time import sleep

import msvcrt
import numpy as np
from PIL import Image

previous = 15  # start position tile


def createmap():
    """
    The map is sketched in bmp, I make a array
    to use it like a tileset
    """
    global bmp
    bmp = Image.open('sketch.bmp')
    bmp_data = bmp.getdata()
    bmp_array = np.array(bmp_data)
    global map
    map = bmp_array.reshape(bmp.size)


def array_to_text_map():
    """ Tileset
    # = Wall
    . = sand
    + = door
    e = enemy
    D = dragon
    $ = gold
    @ = the player

    numbers as due to the 16 color palette used
    in the sketch
    """
    text_map = open('map.txt', 'w')
    for x in map:
        for y in x:
            if y == 0:
                text_map.write('#')
            elif y == 3:
                text_map.write('.')
            elif y == 8:
                text_map.write('+')
            elif y == 9:
                text_map.write('e')
            elif y == 10:
                text_map.write('D')
            elif y == 12:
                text_map.write('$')
            elif y == 13:
                text_map.write('@')
            elif y == 15:
                text_map.write(' ')
        text_map.write('\n')
    text_map.close()


def print_text_map():
    text_map = open('map.txt')
    for x in range(bmp.size[1]):
        print(text_map.readline(), end='')


def move_player_by_key():
    wkey = msvcrt.getch
    if wkey() == b"\xe0":
        key2 = wkey()
        if key2 == b"H":
            move_in_matrix('up')
        elif key2 == b"M":
            move_in_matrix('right')
        elif key2 == b"K":
            move_in_matrix('left')
        elif key2 == b"P":
            move_in_matrix('down')
    else:
        exit()


def position():
    ver = np.where(map == 13)[0][0]
    hor = np.where(map == 13)[1][0]
    return ver, hor


def move_in_matrix(direction):
    ver, hor = position()

    try:
        if direction == 'up':
            analize(ver - 1, hor)
        elif direction == 'right':
            analize(ver, hor + 1)
        elif direction == 'left':
            analize(ver, hor - 1)
        elif direction == 'down':
            analize(ver + 1, hor)
    except IndexError:
        console.append('Not that way')


def analize(verm, horm):
    """Take decision for each tile
    verm and horm = next position
    ver and hor = actual position
    previous = keeps tile number for later
    """
    global previous
    ver, hor = position()

    def restore(ver, hor, previous):
        """Restore color of the leaved tile"""
        map[ver, hor] = previous

    if map[verm, horm] == 0:
        pass

    elif map[verm, horm] == 3:
        restore(ver, hor, previous)
        previous = map[verm, horm]
        map[verm, horm] = 13

    elif map[verm, horm] == 8:
        print('Open the door (yes/no)?', end='')
        answer = input(' ')
        if door(answer):
            restore(verm, horm, 15)
            console.append('The door was opened')
            console.append(doors_dict[(verm, horm)])  # show the description
            # attached to the door

    elif map[verm, horm] == 9:
        print('Do you want to fight against the monster (yes/no)?', end='')
        answer = input(' ')
        result = fight(answer)
        if result and randint(0, 1) == 1:
            restore(verm, horm, 12)
        elif result:
            restore(verm, horm, 15)

    elif map[verm, horm] == 10:
        print('the beast seems asleep, you want to wake her?(yes/no)?', end='')
        answer = input(' ')
        result = fight(answer, dragon=True)
        if result:
            win()

    elif map[verm, horm] == 12:
        print("You want to grab the items in the floor (yes/no)?", end='')
        if input(' ') == 'yes':
            gold()
            restore(verm, horm, 15)

    elif map[verm, horm] == 15:
        restore(ver, hor, previous)
        previous = map[verm, horm]
        map[verm, horm] = 13


def door(answer):
    if answer == 'yes':
        return True
    elif answer == 'no':
        return False
    else:
        console.append('Invalid command')


def identify_doors():
    """Hardcode: Identify each door and zip() it with
    a description stored previously
    """
    doors_array = np.where(map == 8)
    doors = zip(doors_array[0], doors_array[1])
    dict_doors = {}
    narrate = open('narrate.txt')
    for x in doors:
        dict_doors[x] = narrate.readline()
    return dict_doors


def fight(answer, dragon=False):
    if answer == 'yes':
        if dragon == False:
            monster = choice([Orc(), Goblin(), Cyclops()])
        else:
            monster = Dragon()

        monster.show_appearance()
        print('Fighting against', monster.name)
        sleep(2)

        while True:
            monster.show_appearance()
            print(monster.name, 'is attacking you', end='')

            answer = input('fight (1) or defend (2)? ')
            if answer == '1':
                player.defense = 1 + player.armor
                monster.life = monster.life - player.damage
            elif answer == '2':
                player.defense = 1.5 + player.armor
            else:
                print('Invalid command')
                continue

            print(monster.name, 'counterattack!!')
            player.life = player.life - (monster.damage / player.defense)

            print(monster.life, 'remaining', monster.name, 'life')
            print(player.life, 'remaining Player life')

            if player.life <= 0:
                print('The End')
                exit()

            if monster.life <= 0:
                print('\n' * 5)
                print('Enemy defeated')
                print('You earn', monster.gold, 'gold coins')
                player.gold += monster.gold
                break
        sleep(3)
        return True

    else:
        return False


def moredamge(val):
    player.damage += val


def morearmor(val):
    player.armor += val


golds = {'Fire sword': (moredamge, 20),
         'Oak shield': (morearmor, 0.1),
         'Anhilation sword': (moredamge, 40),
         'Iron shield': (morearmor, 0.2),
         'Siege shield': (morearmor, 0.5)
         }


def gold():
    bunch = randint(10, 200)
    print('You have found', bunch, 'gold coins')
    player.gold += bunch
    sleep(1)
    print('Is there anything else?')
    if randint(0, 10) > 7:
        obtained = choice(list(golds))
        print('You have get', obtained)
        golds[obtained][0](golds[obtained][1])  # access to key: (function, quantity)
        del golds[obtained]
    else:
        print('Oooohh.. nothing else')
    sleep(2)


def win():
    print('You have win the game')
    print('You get', player.gold, 'gold coins!!')
    exit()


class Orc():
    def __init__(self):
        self.name = 'Orc'
        self.life = 100
        self.damage = 10
        self.defense = 1
        self.gold = 100
        self.appearance = open('orc.txt')

    def show_appearance(self):
        print(self.appearance.read())


class Player(Orc):
    def __init__(self):
        self.life = 1000
        self.damage = 20
        self.gold = 0
        self.appearance = open('knight.txt')
        self.armor = 0


class Goblin(Orc):
    def __init__(self):
        self.name = 'Goblin'
        self.life = 50
        self.damage = 10
        self.gold = 50
        self.appearance = open('goblin.txt')


class Dragon(Orc):
    def __init__(self):
        self.name = 'Dragon'
        self.life = 400
        self.damage = 40
        self.gold = 2000
        self.appearance = open('dragon.txt')


class Cyclops(Orc):
    def __init__(self):
        self.name = 'Cyclops'
        self.life = 150
        self.damage = 20
        self.gold = 120
        self.appearance = open('cyclops.txt')


def presentation():
    print('\n' * 2)
    player.show_appearance()
    print('Welcome hero, are you ready for fight?')
    input()


if __name__ == "__main__":
    player = Player()

    presentation()
    console = []

    createmap()
    array_to_text_map()

    doors_dict = identify_doors()
    print_text_map()

    while True:
        move_player_by_key()
        array_to_text_map()
        print_text_map()
        if console:
            for x in console:
                print(x)
        else:
            print()
        console = []
