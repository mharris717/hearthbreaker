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
from hearthbreaker.game_objects import Deck, Game
from hearthbreaker.deck_order import DeckOrder

class TestHelpers:
    def cb(self,game):
        for player in game.players:
            cards = DeckOrder().sorted_mana(player.deck.cards)
            player.deck.cards = cards

    def make_game(self,before_draw_callback=None):
        deck1 = Deck([
            GoldshireFootman(),
            GoldshireFootman(),
            MurlocRaider(),
            MurlocRaider(),
            BloodfenRaptor(),
            BloodfenRaptor(),
            FrostwolfGrunt(),
            FrostwolfGrunt(),
            RiverCrocolisk(),
            RiverCrocolisk(),
            IronfurGrizzly(),
            IronfurGrizzly(),
            MagmaRager(),
            MagmaRager(),
            SilverbackPatriarch(),
            SilverbackPatriarch(),
            ChillwindYeti(),
            ChillwindYeti(),
            KeeperOfTheGrove(),
            KeeperOfTheGrove(),
            SenjinShieldmasta(),
            SenjinShieldmasta(),
            BootyBayBodyguard(),
            BootyBayBodyguard(),
            FenCreeper(),
            FenCreeper(),
            BoulderfistOgre(),
            BoulderfistOgre(),
            WarGolem(),
            WarGolem(),
        ], CHARACTER_CLASS.DRUID, use_random=False)

        deck2 = Deck([
            Shieldbearer(),
            Shieldbearer(),
            FlameImp(),
            FlameImp(),
            YoungPriestess(),
            YoungPriestess(),
            DarkIronDwarf(),
            DarkIronDwarf(),
            DireWolfAlpha(),
            DireWolfAlpha(),
            VoidWalker(),
            VoidWalker(),
            HarvestGolem(),
            HarvestGolem(),
            KnifeJuggler(),
            KnifeJuggler(),
            ShatteredSunCleric(),
            ShatteredSunCleric(),
            ArgentSquire(),
            ArgentSquire(),
            Doomguard(),
            Doomguard(),
            AbusiveSergeant(),
            AbusiveSergeant(),
            NerubianEgg(),
            NerubianEgg(),
            WarGolem(),
            WarGolem(),
            BoulderfistOgre(),
            BoulderfistOgre()
        ], CHARACTER_CLASS.WARLOCK, use_random=False)

        if not before_draw_callback:
            before_draw_callback = self.cb

        trade = TradeAgent()
        trade.name = "TRAD"

        r = RandomAgent()
        r.name = "RAND"

        def rand_func(a,b): return 0

        game = Game([deck2, deck1], [trade, r], before_draw_callback=before_draw_callback)

        #print("PLAYERS")
        #for i in range(0,2):
        #    print("Player {}: {}".format(i,game.players[i].agent.name))
            
        game.pre_game()
        game.current_player = game.players[1]

        return game