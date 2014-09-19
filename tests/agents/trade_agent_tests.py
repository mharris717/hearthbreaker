import random
import unittest
from hearthbreaker.agents.basic_agents import RandomAgent
from hearthbreaker.agents.trade_agent import TradeAgent
from hearthbreaker.cards import GoldshireFootman, MurlocRaider, BloodfenRaptor, FrostwolfGrunt, RiverCrocolisk, \
    IronfurGrizzly, MagmaRager, SilverbackPatriarch, ChillwindYeti, SenjinShieldmasta, BootyBayBodyguard, \
    FenCreeper, BoulderfistOgre, WarGolem, Shieldbearer, FlameImp, YoungPriestess, DarkIronDwarf, DireWolfAlpha, \
    VoidWalker, HarvestGolem, KnifeJuggler, ShatteredSunCleric, ArgentSquire, Doomguard, Soulfire, DefenderOfArgus, \
    AbusiveSergeant, NerubianEgg, KeeperOfTheGrove, Wisp, Deathwing
from hearthbreaker.constants import CHARACTER_CLASS
from hearthbreaker.game_objects import Deck, Game
from hearthbreaker.test_helpers import TestHelpers

class DeckOrder:
    def __init__(self,*names):
        self.names = [n for n in names]

    def sort_func(self,card):
        if card.name in self.names:
            i = self.names.index(card.name)
            self.names[i] = "Gibberish"
            #print("{} for {}".format(i,card.name))
            return i
        else:
            return 99

    def sorted(self,cards):
        return sorted(cards,key=self.sort_func)

    def sorted_mana(self,cards):
        res = sorted(cards,key=self.mana_func)
        res.reverse()
        return res

    def mana_func(self,card):
        return card.mana

class TestTradeAgent(unittest.TestCase):

    def setUp(self):
        random.seed(1857)



    def add_minions(self,game,player_index,*minions):
        player = game.players[player_index]
        for minion in minions:
            minion.use(player,game)

    def make_all_active(self,game):
        for player in game.players:
            for minion in player.minions:
                minion.active = True
                minion.exhausted = False

    def test_setup_smoke(self):
        game = TestHelpers().make_game()

        self.add_minions(game,0,Wisp(),WarGolem())
        self.add_minions(game,1,BloodfenRaptor())

        self.assertEqual(2,len(game.players[0].minions))
        self.assertEqual(1,len(game.players[1].minions))

    def card_names(self,cards):
        return [m.name for m in cards]

    def player_str(self,player):
        res = []
        res.append("\nPlayer\n")
        res.append("Hand: ")
        res.append(self.card_names(player.hand))
        res.append("\nDeck: ")
        res.append(self.card_names(player.deck.cards[0:5]))
        res.append("\n")

        res = [str(x) for x in res]

        return str.join("",res)

    def test_basic_trade(self):
        def cb(game):
            for player in game.players:
                cards = DeckOrder().sorted_mana(player.deck.cards)
                player.deck.cards = cards

                # a = [m.name for m in player.deck.cards]
                #print(a)

        game = TestHelpers().make_game(cb)

        #for player in game.players:
        #    print(self.player_str(player))

        self.add_minions(game,0,Wisp(),WarGolem())
        self.add_minions(game,1,BloodfenRaptor())

        self.make_all_active(game)
        game.current_player = game.players[0]
        game.play_single_turn()

        self.assert_minions(game.players[0],"War Golem")
        self.assert_minions(game.players[1],"Bloodfen Raptor")

    

    def deck_sort_func_old(self,card):
        if card.name == 'Argent Squire':
            return 0
        else:
            return 99

    def test_draw_setup(self):
        game = TestHelpers().make_game()

        player = game.players[1]
        cards = DeckOrder("Argent Squire","Doomguard","Dire Wolf Alpha","Argent Squire").sorted(player.deck.cards)
        self.assertEqual(cards[0].name,"Argent Squire")
        self.assertEqual(cards[1].name,"Doomguard")
        self.assertEqual(cards[2].name,"Dire Wolf Alpha")
        self.assertEqual(cards[3].name,"Argent Squire")

        #print(player.deck.cards[0])
        #foot = [m for m in filter(lambda minion: minion.name == Shieldbearer().name, player.deck.cards)]
        #self.assertEqual(len(foot),2)

    def test_simple_plays(self):
        def cb(game):
            for player in game.players:
                cards = DeckOrder("Argent Squire","Harvest Golem","Doomguard","Dire Wolf Alpha","Doomguard","Dark Iron Dwarf","Dark Iron Dwarf").sorted(player.deck.cards)
                player.deck.cards = cards

        game = TestHelpers().make_game(cb)
        game.current_player = game.players[0]
        game.play_single_turn()

        self.assert_minions(game.players[1],"Argent Squire")

        game.play_single_turn()
        game.play_single_turn()

        self.assert_minions(game.players[1],"Argent Squire","Dire Wolf Alpha")

    def test_will_play_biggest(self):
        game = TestHelpers().make_game()

        game.players[1].hand = [ArgentSquire(),ArgentSquire(),DireWolfAlpha()]
        game.players[1].mana = 1
        game.players[1].max_mana = 1

        game.current_player = game.players[0]
        game.play_single_turn()

        self.assert_minions(game.players[1],"Dire Wolf Alpha")

    def test_will_play_multiple(self):
        game = TestHelpers().make_game()

        game.players[1].hand = [ArgentSquire(),ArgentSquire(),ArgentSquire()]
        game.players[1].mana = 1
        game.players[1].max_mana = 1

        game.current_player = game.players[0]
        game.play_single_turn()

        self.assert_minions(game.players[1],"Argent Squire","Argent Squire")

    def test_will_play_multiple_correct_order(self):
        game = TestHelpers().make_game()

        game.players[1].hand = [ArgentSquire(),ArgentSquire(),ArgentSquire(),HarvestGolem()]
        game.players[1].mana = 3
        game.players[1].max_mana = 3

        game.current_player = game.players[0]
        game.play_single_turn()

        self.assert_minions(game.players[1],"Harvest Golem","Argent Squire")

    def test_will_use_entire_pool(self):
        def cb(game):
            for player in game.players:
                cards = DeckOrder().sorted_mana(player.deck.cards)
                player.deck.cards = cards

        game = TestHelpers().make_game(cb)

        game.players[1].hand = [DireWolfAlpha(),DireWolfAlpha(),DireWolfAlpha(),HarvestGolem()]
        game.players[1].mana = 3
        game.players[1].max_mana = 3

        game.current_player = game.players[0]
        game.play_single_turn()

        self.assert_minions(game.players[1],"Dire Wolf Alpha","Dire Wolf Alpha")


    def assert_minions(self,player,*names):
        actual = [m.name for m in player.minions]
        self.assertEqual(sorted(actual),sorted(names))



        