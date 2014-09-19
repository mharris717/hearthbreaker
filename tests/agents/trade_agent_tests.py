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
from hearthbreaker.game_objects import Deck, Game, TheCoin, Hero
from hearthbreaker.test_helpers import TestHelpers
from hearthbreaker.deck_order import DeckOrder
from hearthbreaker.agents.trade.trade import Trades
from hearthbreaker.agents.trade.possible_play import PossiblePlays

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

    def assert_minions(self,player,*names):
        actual = [m.name for m in player.minions]
        self.assertEqual(sorted(actual),sorted(names))

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
        game = TestHelpers().make_game()

        self.add_minions(game,1,Wisp(),WarGolem())
        self.add_minions(game,0,BloodfenRaptor())

        self.make_all_active(game)
        game.play_single_turn()

        self.assert_minions(game.players[1],"War Golem")
        self.assert_minions(game.players[0],"Bloodfen Raptor")

    

    def deck_sort_func_old(self,card):
        if card.name == 'Argent Squire':
            return 0
        else:
            return 99

    def test_draw_setup(self):
        game = TestHelpers().make_game()

        player = game.players[0]
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

        self.assertEqual(27,game.players[1].hero.health)

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

    def test_buff_target(self):
        game = TestHelpers().make_game()

        self.add_minions(game,0,BloodfenRaptor(),RiverCrocolisk())
        self.make_all_active(game)
        self.add_minions(game,0,AbusiveSergeant())

        game.play_single_turn()

        #self.assertEqual(25,game.players[1].hero.health)

    def make_trades(self,me,opp):
        me = [m for m in map(lambda c: c.create_minion_named(None),me)]
        opp = [m for m in map(lambda c: c.create_minion_named(None),opp)]

        game = TestHelpers().make_game()
        trades = Trades(game.players[0],me,opp,game.players[1].hero)

        return trades

    def test_trades_obj_smoke(self):
        me = [BloodfenRaptor(),RiverCrocolisk()]
        opp = [Wisp(),WarGolem()]

        trades = self.make_trades(me,opp)

        self.assertEqual(len(trades.trades()),6)

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

    def test_hero_power(self):
        cards = [ArgentSquire()]
        possible_plays = PossiblePlays(cards,10,allow_hero_power=True)

        for play in possible_plays.plays():
            names = [c.name for c in play.cards]
            #print(names)

        self.assertEqual(1,len(possible_plays.plays()))

       # self.assertEqual(false,)
        


        