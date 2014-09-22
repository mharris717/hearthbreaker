import random
import unittest
from hearthbreaker.agents.basic_agents import RandomAgent
from hearthbreaker.agents.trade_agent import TradeAgent
from hearthbreaker.cards import GoldshireFootman, MurlocRaider, BloodfenRaptor, FrostwolfGrunt, RiverCrocolisk, \
    IronfurGrizzly, MagmaRager, SilverbackPatriarch, ChillwindYeti, SenjinShieldmasta, BootyBayBodyguard, \
    FenCreeper, BoulderfistOgre, WarGolem, Shieldbearer, FlameImp, YoungPriestess, DarkIronDwarf, DireWolfAlpha, \
    VoidWalker, HarvestGolem, KnifeJuggler, ShatteredSunCleric, ArgentSquire, Doomguard, Soulfire, DefenderOfArgus, \
    AbusiveSergeant, NerubianEgg, KeeperOfTheGrove, Wisp, Deathwing, NatPagle, AmaniBerserker
from hearthbreaker.constants import CHARACTER_CLASS
from hearthbreaker.game_objects import Deck, Game, TheCoin, Hero
from tests.agents.trade.test_helpers import TestHelpers
from hearthbreaker.agents.trade.trade import Trades
from hearthbreaker.agents.trade.possible_play import PossiblePlays
from tests.agents.trade.test_case_mixin import TestCaseMixin
from tests.agents.trade.play_tests import *
from tests.agents.trade.attack_tests import *

class TestTradeAgent(TestCaseMixin,unittest.TestCase):
    def test_setup_smoke(self):
        game = TestHelpers().make_game()

        self.add_minions(game,0,Wisp(),WarGolem())
        self.add_minions(game,1,BloodfenRaptor())

        self.assertEqual(2,len(game.players[0].minions))
        self.assertEqual(1,len(game.players[1].minions))

    def test_basic_trade(self):
        game = TestHelpers().make_game()

        self.add_minions(game,1,Wisp(),WarGolem())
        self.add_minions(game,0,BloodfenRaptor())

        self.make_all_active(game)
        game.play_single_turn()

        self.assert_minions(game.players[1],"War Golem")
        self.assert_minions(game.players[0],"Bloodfen Raptor")

    def test_buff_target(self):
        game = TestHelpers().make_game()

        self.add_minions(game,0,BloodfenRaptor(),RiverCrocolisk())
        self.make_all_active(game)
        self.add_minions(game,0,AbusiveSergeant())

        game.play_single_turn()

        #self.assertEqual(25,game.players[1].hero.health)

    def test_hero_power(self):
        cards = [ArgentSquire()]
        possible_plays = PossiblePlays(cards,10,allow_hero_power=True)

        for play in possible_plays.plays():
            names = [c.name for c in play.cards]
            #print(names)

        self.assertEqual(1,len(possible_plays.plays()))
        