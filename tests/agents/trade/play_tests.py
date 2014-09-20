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
from hearthbreaker.deck_order import DeckOrder
from hearthbreaker.agents.trade.trade import Trades
from hearthbreaker.agents.trade.possible_play import PossiblePlays
from tests.agents.trade.test_case_mixin import TestCaseMixin

class TestTradeAgentPlayTests(TestCaseMixin,unittest.TestCase):
    def test_simple_plays(self):
        def cb(game):
            for player in game.players:
                cards = DeckOrder("Argent Squire","Harvest Golem","Doomguard","Dire Wolf Alpha","Doomguard","Dark Iron Dwarf","Dark Iron Dwarf").sorted(player.deck.cards)
                player.deck.cards = cards

        game = TestHelpers().make_game(cb)

        self.assertEqual(game.players[0].agent.name,"TRAD")

        game.play_single_turn()

        names = [m.name for m in game.players[0].hand]
        #print(names)
        self.assert_minions(game.players[0],"Argent Squire")

        game.play_single_turn()
        game.play_single_turn()

        self.assert_minions(game.players[0],"Argent Squire","Dire Wolf Alpha")

    def test_will_play_biggest(self):
        game = TestHelpers().make_game()

        game.players[0].hand = [ArgentSquire(),ArgentSquire(),DireWolfAlpha()]
        game.players[0].mana = 1
        game.players[0].max_mana = 1

        game.play_single_turn()

        self.assert_minions(game.players[0],"Dire Wolf Alpha")

    def test_will_play_multiple(self):
        game = TestHelpers().make_game()

        game.players[0].hand = [ArgentSquire(),ArgentSquire(),ArgentSquire()]
        game.players[0].mana = 1
        game.players[0].max_mana = 1

        game.play_single_turn()

        self.assert_minions(game.players[0],"Argent Squire","Argent Squire")

    def test_will_play_multiple_correct_order(self):
        game = TestHelpers().make_game()

        game.players[0].hand = [ArgentSquire(),ArgentSquire(),ArgentSquire(),HarvestGolem()]
        game.players[0].mana = 3
        game.players[0].max_mana = 3

        game.play_single_turn()

        self.assert_minions(game.players[0],"Harvest Golem","Argent Squire")

    def test_will_use_entire_pool(self):
        game = TestHelpers().make_game()

        game.players[0].hand = [DireWolfAlpha(),DireWolfAlpha(),DireWolfAlpha(),HarvestGolem()]
        game.players[0].mana = 3
        game.players[0].max_mana = 3

        game.play_single_turn()

        self.assert_minions(game.players[0],"Dire Wolf Alpha","Dire Wolf Alpha")

class TestTradeAgentPlayCoinTests(TestCaseMixin,unittest.TestCase):
    def test_coin(self):
        cards = [ArgentSquire(),BloodfenRaptor(),TheCoin()]
        possible_plays = PossiblePlays(cards,1)
        play = possible_plays.plays()[0]
        names = [c.name for c in play.cards]
        self.assertEqual(names,["The Coin","Bloodfen Raptor"])

    def test_coin_save(self):
        cards = [ArgentSquire(),MagmaRager(),TheCoin()]
        possible_plays = PossiblePlays(cards,1)
        play = possible_plays.plays()[0]
        names = [c.name for c in play.cards]
        self.assertEqual(names,["Argent Squire"])

