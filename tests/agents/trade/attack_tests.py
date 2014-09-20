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
from hearthbreaker.game_objects import Deck, Game, TheCoin, Hero, Minion, MinionCard
from tests.agents.trade.test_helpers import TestHelpers
from hearthbreaker.deck_order import DeckOrder
from hearthbreaker.agents.trade.trade import Trades
from hearthbreaker.agents.trade.possible_play import PossiblePlays
from tests.agents.trade.test_case_mixin import TestCaseMixin
import re

class TestTradeAgentAttackBasicTests(TestCaseMixin,unittest.TestCase):
    def test_will_attack_face(self):
        game = TestHelpers().make_game()

        self.add_minions(game,0,BloodfenRaptor())

        self.make_all_active(game)
        game.play_single_turn()

        self.assert_minions(game.players[1])
        self.assert_minions(game.players[0],"Bloodfen Raptor")

        self.assertEqual(27,game.players[1].hero.health)

    def test_will_attack_minion_and_face(self):
        game = TestHelpers().make_game()

        self.add_minions(game,1,Wisp())
        self.add_minions(game,0,BloodfenRaptor(),RiverCrocolisk())

        self.make_all_active(game)
        game.play_single_turn()

        self.assert_minions(game.players[1])
        self.assert_minions(game.players[0],"Bloodfen Raptor","River Crocolisk")

        # should probably be 27
        self.assertEqual(28,game.players[1].hero.health)

    def test_will_respect_taunt(self):
        game = TestHelpers().make_game()

        self.add_minions(game,1,Wisp(),GoldshireFootman())
        self.add_minions(game,0,BloodfenRaptor())

        self.make_all_active(game)
        game.play_single_turn()

        self.assert_minions(game.players[1],"Wisp")
        self.assert_minions(game.players[0],"Bloodfen Raptor")

    def test_will_attack_twice(self):
        game = TestHelpers().make_game()

        self.add_minions(game,1,Wisp(),GoldshireFootman())
        self.add_minions(game,0,BloodfenRaptor(),RiverCrocolisk())

        self.make_all_active(game)
        game.play_single_turn()

        self.assert_minions(game.players[1])
        self.assert_minions(game.players[0],"Bloodfen Raptor","River Crocolisk")

    def test_trades_obj_smoke(self):
        me = [BloodfenRaptor(),RiverCrocolisk()]
        opp = [Wisp(),WarGolem()]

        trades = self.make_trades(me,opp)

        self.assertEqual(len(trades.trades()),6)


class TestTradeAgentAttackTradesTests(TestCaseMixin,unittest.TestCase):
    def test_trades_smart(self):
        me = [MagmaRager()]
        opp = [Wisp(),ChillwindYeti()]

        trades = self.make_trades(me,opp)
        #for t in trades.trades(): print(t)

        self.assertEqual(len(trades.trades()),3)
        self.assertEqual(trades.trades()[0].opp_minion.name,"Chillwind Yeti")

    def test_trades_smart2(self):
        me = [VoidWalker()]
        opp = [Wisp(),ChillwindYeti()]

        trades = self.make_trades(me,opp)

        self.assertEqual(len(trades.trades()),3)
        self.assertEqual(trades.trades()[0].opp_minion.name,"Wisp")

    def test_trades_smart3(self):
        me = [VoidWalker()]
        opp = [ChillwindYeti()]

        trades = self.make_trades(me,opp)

        self.assertEqual(len(trades.trades()),2)
        self.assertEqual(trades.trades()[0].opp_minion.__class__,Hero)

class TempCard:
    def __init__(self,base_attack,health,name="",taunt=False):
        self.base_attack = base_attack
        self.health = health
        self.name = name
        self.taunt = taunt

    def create_minion(self,player):
        return Minion(self.base_attack,self.health,taunt=self.taunt)

    def create_minion_named(self,player):
        return self.create_minion(player)

    @staticmethod
    def make(str):
        taunt = False
        a,h = str.split("/")
        g = re.search("(\d+)t$",h)
        if g:
            taunt = True
            h = g.group(1)
        return TempCard(int(a),int(h),taunt=taunt,name=str)

class TestTempCard(unittest.TestCase):
    def test_make(self):
        m = TempCard.make("1/2")
        self.assertEqual(m.create_minion(None).health,2)

    def test_taunt(self):
        mm = TempCard.make("1/2t")
        m = mm.create_minion(None)
        self.assertEqual(m.health,2)
        self.assertEqual(m.taunt,True)

class TestTradeAgentAttackLethalTests(TestCaseMixin,unittest.TestCase):
    def make_minions(self,*strs):
        res = []
        for s in strs:
            if isinstance(s,MinionCard):
                res.append(s)
            else:
                m = TempCard.make(s)
                res.append(m)
        return res

    def test_lethal(self):
        me = [ChillwindYeti()]
        opp = [AmaniBerserker()]

        a = self.make_trades2(me,opp)
        trades = a[1]
        game = a[0]
        game.players[1].hero.health = 1

        self.assertEqual(len(trades.trades()),1)
        self.assertEqual(trades.trades()[0].opp_minion.__class__,Hero)

    def test_lethal_with_two(self):
        me = [ChillwindYeti(),WarGolem()]
        opp = [AmaniBerserker()]

        a = self.make_trades2(me,opp)
        trades = a[1]
        game = a[0]
        game.players[1].hero.health = 10

        self.assertEqual(len(trades.trades()),2)
        self.assertEqual(trades.trades()[0].opp_minion.__class__,Hero)

    def test_lethal_with_taunt(self):
        #print("\n\nstarting bad test") 
        me = self.make_minions("2/9","3/1")
        opp = self.make_minions("9/2t")

        def cb(g):
            g.players[1].hero.health = 3

        game,trades = self.make_trades2(me,opp,cb)
        trade = trades.trades()[0]
        

        self.assertEqual(len(trades.trades()),2)
        self.assertEqual(trade.my_minion.health,9)

    def test_lethal_with_taunt2(self):
        #print("\n\nstarting bad test") 
        me = self.make_minions("2/9","3/1","2/8")
        opp = self.make_minions("9/4t")

        def cb(g):
            g.players[1].hero.health = 3

        game,trades = self.make_trades2(me,opp,cb)
        trade = trades.trades()[0]
        

        self.assertEqual(len(trades.trades()),3)
        self.assertEqual(trade.my_minion.health,9)

    def test_good_trade_with_taunt2(self):
        #print("\n\nstarting bad test") 
        me = self.make_minions("1/6","1/6","9/1")
        opp = self.make_minions("8/2t","9/9")

        game,trades = self.make_trades2(me,opp)
        trade = trades.trades()[0]

        print(trades)
        

        self.assertEqual(len(trades.trades()),3)
        self.assertEqual(trade.my_minion.health,6)
        self.assertEqual(trade.opp_minion.health,2)

