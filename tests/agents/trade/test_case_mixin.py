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
from hearthbreaker.game_objects import Deck, Game, TheCoin, Hero, Player
from tests.agents.trade.test_helpers import TestHelpers
from tests.agents.trade.deck_order import DeckOrder
from hearthbreaker.agents.trade.trade import Trades
from hearthbreaker.agents.trade.possible_play import PossiblePlays
from tests.agents.trade.test_helpers import CardWrapper

class TestCaseMixin:
    def setUp(self):
        Player.no_draw = True
        TestHelpers.fix_create_minion()
        random.seed(1857)
    def tearDown(self):
        Player.no_draw = False

    def add_minions(self,game,player_index,*minions):
        minions = [CardWrapper(c) for c in minions]
        #raise Exception(minions[0].create_minion(None).name)
        player = game.players[player_index]
        for minion in minions:
            minion.use(player,game)

    def make_all_active(self,game):
        for player in game.players:
            for minion in player.minions:
                minion.active = True
                minion.exhausted = False

    def assert_minions(self,player,*names):
        actual = self.card_names(player.minions)
        self.assertEqual(sorted(actual),sorted(names))

    def card_names(self,cards):
        return [m.try_name() for m in cards]

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

    def make_trades2(self,me,opp,game_callback=None):
        me = [m for m in map(lambda c: CardWrapper(c).create_minion(42),me)]
        opp = [m for m in map(lambda c: CardWrapper(c).create_minion(42),opp)]

        game = TestHelpers().make_game()
        if game_callback:
            game_callback(game)
            
        trades = Trades(game.players[0],me,opp,game.players[1].hero)

        return [game,trades]

    def make_trades(self,me,opp):
        return self.make_trades2(me,opp)[1]

    def make_cards(self,*cards):
        return [CardWrapper(c) for c in cards]

    def set_hand(self,game,player_index,*cards):
        cards = self.make_cards(*cards)
        game.players[player_index].hand = cards