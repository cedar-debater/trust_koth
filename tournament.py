import os
import random
import copy

## Generate competitors
walked = next(os.walk('./competitors'))
filenames = walked[2]
assert not set(walked[1])-{'__pycache__'}, 'No sub-folders apart from __pycache__ allowed in the "competitors/" folder'
competitor_names = ['.'.join(name.split('.')[:-1]) for name in filenames]
competitors = [(
    name,
    getattr(__import__(f'competitors.{name}'),name),
    getattr(__import__(f'info.{name}'),name),
) for name in competitor_names]

class ModuleRepr(object):
    def __init__(self, module):
        self.move = module.move
        self.turn = module.turn
        self.name = module.__name__[12:]
    def __repr__(self):
        return f"<{self.name}>"

# (name, creator, module)
competitors = [(name, info.creator, ModuleRepr(module)) for name, module, info in competitors]

## Game/Tournament
def mistaek(move):
    if random.randint(1,20)<2:
        move=not move
    return move
class GameState(object):
    def __init__(self, p0, p1):
        self.players = [p0, p1]
        self.points = [0, 0]
        self.move_no = 1
        self.perfects = [[], []]
        self.imperfects = [[], []]
        self.states = [[1,[],[],[],0,0], [1,[],[],[],0,0]]
    def update(self):
        for index in range(2):
            self.states[index] = [
                self.move_no,
                self.perfects[index],
                self.imperfects[index],
                self.imperfects[1-index],
                *self.points[::(1-index*2)]
            ]
class Game(object):
    """A game between 2 players"""
    def __init__(self, p0, p1):
        # p is short for player
        self.state = GameState(p0, p1)
        # is first round?
        self.first = True
    def play_round(self, return_best = False):
        state = self.state # for speed
        pl = state.players
        pt = state.points
        for num,cur in enumerate(pl):
            if self.first:
                orig = bool(cur.move())
                move = mistaek(orig)
            else:
                orig = bool(cur.turn(copy.deepcopy(state.states[num])))
                move = mistaek(orig)
            if move:
                pt[1-num] += 3
                pt[num] -= 1
            state.perfects[num].append(orig)
            state.imperfects[num].append(move)
        self.first = False
        state.move_no += 1
        state.update()
        if return_best:
            return sorted(pl,key = lambda p:pt[pl.index(p)])[1]
        else:
            return self
    def play_rounds(self, amount, return_best = False):
        for i in range(1, amount):
            self.play_round()
        if amount > 0:
            return self.play_round(return_best = return_best)
        else:
            return self
    def __repr__(self):
        return ' | '.join([i.name.title() for i in self.state.players])

class Tournament(object):
    def __init__(self, class_amounts=[], classes = [], rounds=10):
        self.classes = [(class_,0) for class_ in classes]
        for class_, amount in class_amounts:
            self.classes.extend([[class_,0]]*amount)
        self.rounds = rounds
    def play_games(self):
        """Plays games with each pair in self.classes"""
        for i in range(len(self.classes)-1):
            for j in range(i+1,len(self.classes)):
                first = self.classes[i][0]
                second = self.classes[j][0]
                game = Game(first, second)
                game.play_rounds(self.rounds)
                self.classes[i][1] += game.state.points[0]
                self.classes[j][1] += game.state.points[1]
    def prepare(self,using=None,reverse=False):
        """Sort the classes"""
        if using == None:
            using = self.classes
        scores = sorted({i[1] for i in using}, reverse=reverse)
        new_dict = {}
        for i in scores:
            new_dict[i] = [k for k in using if k[1] == i]
        self.sort_dict = new_dict
        self.scores = scores
    def knockout(self, amount):
        """Knockout (amount) of the worst from self.classes"""
        for i in range(amount):
            self.prepare()
            buildup = []
            for i in self.scores:
                buildup.extend(self.sort_dict[i])
                if len(buildup) > 0:
                    break
            player = random.choice(buildup)
            self.classes.remove(player)
    def replicate(self, amount):
        """Replicate (amount) of the best from self.classes"""
        k = [(i[0],i[1],a) for a,i in enumerate(self.classes)]
        for i in range(amount):
            self.prepare(k,reverse=True)
            buildup = []
            for i in self.scores:
                buildup.extend(self.sort_dict[i])
                if len(buildup) >= 1:
                    break
            player = random.choice(buildup)
            k.remove(player)
            self.classes.append([i for i in player[:2]])
    def reset_scores(self):
        self.classes = [[i[0],0] for i in self.classes]
    def play_round(self):
        self.play_games()
        self.knockout(5)
        self.replicate(5)
        self.reset_scores()
        return self
    def play_rounds(self, amount):
        for i in range(amount):
            self.play_round()
        return self
    def __repr__(self):
        return "".join(["<Tournament of ",str(len(self.classes))," players>"])
    @property
    def counts(self):
        all_ = [i[0] for i in self.classes]
        retval = []
        for class_ in set(all_):
            retval.append((class_, all_.count(class_)))
        return retval
    @property
    def scores(self):
        if hasattr(self, '_scores'):
            if self._scores is None:
                return sorted(
                    [tuple(i) for i in self.classes],
                    key = lambda a: a[1],
                    reverse=True
                )
            try:
                return self._scores
            finally:
                self._scores = None
        self._scores = None
        return self.scores
    @scores.setter
    def scores(self, new_value):
        self._scores = new_value

"""if globals().get('__name__', None) == '__main__':
    print('Test cases')

    print('Setup')
    copycat = [m for n,c,m in competitors if n=='copycat'][0]
    copykitten = [m for n,c,m in competitors if n=='copykitten'][0]
    print('Done\n')

    ## Game
    game = Game(copycat, copykitten)
    print(game)
    print(game.play_round())
    print(game.play_rounds(10))
    print(game.state.points)
    print('Done\n')

    ## Tournament
    tournament = Tournament([
        (copycat, 10),
        (copykitten, 10),
    ])
    print(tournament)
    for _ in range(10):
        print(tournament.play_rounds(1).counts)
    print('Done\n')"""

official = Tournament([
    (m,10) for n,c,m in competitors
])

counts=official.counts

while not input("Type anything to break: "):
    for i in range(10):
        official.play_round()
    print(counts:=official.counts)



print('Winner','s'[len(counts)==1:],':\n\n','.\n'.join(
    [' '.join([str(i[1]),i[0]]) for i in sorted([
        (' made by '.join([
            (''.join([j[0],'(s)']),j[1]) for j in competitors if j[2] == i[0]
        ][0]),i[1])
    for i in counts],key=lambda n:n[1],reverse=True)]
),'.',sep='')