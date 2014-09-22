import random
import unittest
from hearthbreaker.agents.basic_agents import RandomAgent
from hearthbreaker.agents.trade_agent import TradeAgent
from hearthbreaker.cards import GoldshireFootman, MurlocRaider, BloodfenRaptor, FrostwolfGrunt, RiverCrocolisk, \
    IronfurGrizzly, MagmaRager, SilverbackPatriarch, ChillwindYeti, SenjinShieldmasta, BootyBayBodyguard, \
    FenCreeper, BoulderfistOgre, WarGolem, Shieldbearer, FlameImp, YoungPriestess, DarkIronDwarf, DireWolfAlpha, \
    VoidWalker, HarvestGolem, KnifeJuggler, ShatteredSunCleric, ArgentSquire, Doomguard, Soulfire, DefenderOfArgus, \
    AbusiveSergeant, NerubianEgg, KeeperOfTheGrove
from hearthbreaker.constants import CHARACTER_CLASS
from hearthbreaker.game_objects import Deck, Game, MinionCard, Minion, TheCoin, Player, Bindable
from tests.agents.trade.deck_order import DeckOrder
import re

def CardWrapper(c): 
    #print(c)
    if isinstance(c,str):
        c = TempCard.make(c)
    elif isinstance(c,TempCard):
        c = c
    else:
        TestHelpers.fix_create_minion_single(c)
    return c

def t(self):
    if hasattr(self,"name"):
        return self.name
    else:
        return "Placeholder"

Minion.try_name = t

class TempCard:
    def __init__(self,base_attack,health,name="",taunt=False):
        self.base_attack = base_attack
        self.health = health
        self.name = name
        self.taunt = taunt
        self.mana = None

    def create_minion(self,player):
        res = Minion(self.base_attack,self.health,taunt=self.taunt)
        res.name = self.name
        return res

    @staticmethod
    def make(s):
        if not isinstance(s,str): sfsdfd()

        taunt = False
        a,h = s.split("/")
        g = re.search("(\d+)t$",h)
        if g:
            taunt = True
            h = g.group(1)
        return TempCard(int(a),int(h),taunt=taunt,name=s)

class FakeDeckUnused(Deck):
    def can_draw(self): return False
    def is_fake_deck(self): return True

class FakePlayer(Player):
    def draw(self): None

class FakeGame(Game):
    def __init__(self, decks, agents, random_func=random.randint):
        super(Game,self).__init__()
        self.delayed_minions = set()
        self.random = random_func
        first_player = random_func(0, 1)
        if first_player is 0:
            play_order = [0, 1]
        else:
            play_order = [1, 0]
        self.players = [FakePlayer("one", decks[play_order[0]], agents[play_order[0]], self, random_func),
                        FakePlayer("two", decks[play_order[1]], agents[play_order[1]], self, random_func)]
        self.current_player = self.players[0]
        self.other_player = self.players[1]
        self.current_player.opponent = self.other_player
        self.other_player.opponent = self.current_player
        self.game_ended = False
        self.minion_counter = 0
        for i in range(0, 3):
            self.players[0].draw()

        for i in range(0, 4):
            self.players[1].draw()

class TestHelpers:
    @staticmethod
    def fix_create_minion(classes=None):
        if not classes: classes = MinionCard.__subclasses__()
        for cls in classes:
            TestHelpers.fix_create_minion_single(cls)

    def fix_create_minion_single(cls):
        if isinstance(cls,str): sdfsdfd()
        if isinstance(cls,TheCoin): return

        if not hasattr(cls,"create_minion_old"):
            old = cls.create_minion
            cls.create_minion_old = old
            def create_minion_named_gen(self,player):
                #if len(args) != 1:
                #    raise Exception("bad args {}".format(args))

                #player = args[0]
                res = old(self,player)
                res.name = self.name
                return res
            cls.create_minion = create_minion_named_gen


    def cb(self,game):
        for player in game.players:
            cards = DeckOrder().sorted_mana(player.deck.cards)
            player.deck.cards = cards

    def make_game(self,before_draw_callback=None):
        cs = [WarGolem() for i in range(0,30)]
        cs = [CardWrapper(c) for c in cs]
        deck1 = Deck(cs.copy(), CHARACTER_CLASS.DRUID)
        deck2 = Deck(cs.copy(), CHARACTER_CLASS.WARLOCK)

        if not before_draw_callback:
            before_draw_callback = self.cb

        trade = TradeAgent()
        #trade.name = "TRAD"

        r = RandomAgent()
        #r.name = "RAND"

        def rand_func(a,b): return 0

        game = FakeGame([deck2, deck1], [trade, r])

        #print("PLAYERS")
        #for i in range(0,2):
        #    print("Player {}: {}".format(i,game.players[i].agent.name))

        game.pre_game()
        game.current_player = game.players[1]

        return game