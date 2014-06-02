from hsgame.cards.battlecries import draw_card, silence, deal_one_damage,\
    gain_one_health_for_each_card_in_hand
from hsgame.game_objects import Minion, MinionCard
from hsgame.constants import CARD_RARITY, CHARACTER_CLASS, MINION_TYPE
import hsgame.targeting
__author__ = 'Daniel'


class BloodfenRaptor(MinionCard):
    def __init__(self):
        super().__init__("Bloodfen Raptor", 2, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(3, 2, MINION_TYPE.BEAST)


class ElvenArcher(MinionCard):
    def __init__(self):
        super().__init__("Elven Archer", 1, CHARACTER_CLASS.ALL, CARD_RARITY.FREE, hsgame.targeting.find_battlecry_target)

    def create_minion(self, player):
        minion = Minion(1, 1)
        minion.bind("added_to_board", deal_one_damage)
        return minion

class NoviceEngineer(MinionCard):
    def __init__(self):
        super().__init__("Novice Engineer", 2, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        minion = Minion(1, 1)
        minion.bind('added_to_board', draw_card)
        return minion

class StonetuskBoar(MinionCard):
    def __init__(self):
        super().__init__("Stonetusk Boar", 1, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        minion = Minion(1, 1, MINION_TYPE.BEAST)
        minion.charge = True
        return minion

class IronbeakOwl(MinionCard):
    def __init__(self):
        super().__init__("Ironbeak Owl", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON, hsgame.targeting.find_minion_battlecry_target)

    def create_minion(self, player):
        minion = Minion(2, 1, MINION_TYPE.BEAST)
        minion.bind('added_to_board', silence)
        return minion


class WarGolem(MinionCard):
    def __init__(self):
        super().__init__("War Golem", 7, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(7, 7)


class MogushanWarden(MinionCard):
    def __init__(self):
        super().__init__("Mogu'shan Warden", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        minion = Minion(1, 7)
        minion.taunt = True
        return minion


class OasisSnapjaw(MinionCard):
    def __init__(self):
        super().__init__("Oasis Snapjaw", 4, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(2, 7, MINION_TYPE.BEAST)


class FaerieDragon(MinionCard):
    def __init__(self):
        super().__init__("Faerie Dragon", 2, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        def silence():
            minion.spell_targettable = lambda : True
        minion = Minion(3, 2, MINION_TYPE.DRAGON)
        minion.spell_targettable = lambda: False
        minion.bind("silenced", silence())
        return minion


class KoboldGeomancer(MinionCard):

    def __init__(self):
        super().__init__("Kobold Geomancer", 2, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        minion = Minion(2, 2)
        minion.spell_power = 1
        return minion


class IronfurGrizzly(MinionCard):

    def __init__(self):
        super().__init__("Ironfur Grizzly", 2, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        minion = Minion(3, 3)
        minion.taunt = True
        return minion

class ArgentSquire(MinionCard):
    def __init__(self):
        super().__init__("Argent Squire", 1, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        minion = Minion(1, 1)
        minion.divine_shield = True
        return minion
    
class SilvermoonGuardian(MinionCard):
    def __init__(self):
        super().__init__("Silvermoon Guardian", 4, CHARACTER_CLASS.ALL, CARD_RARITY.COMMON)

    def create_minion(self, player):
        minion = Minion(3, 3)
        minion.divine_shield = True
        return minion
    
class TwilightDrake(MinionCard):
    def __init__(self):
        super().__init__("Twilight Drake", 4, CHARACTER_CLASS.ALL, CARD_RARITY.RARE)

    def create_minion(self, player):
        minion = Minion(4, 1, MINION_TYPE.DRAGON)
        minion.bind('added_to_board', gain_one_health_for_each_card_in_hand)
        return minion
    
class MagmaRager(MinionCard):
    def __init__(self):
        super().__init__("Magma Rager", 3, CHARACTER_CLASS.ALL, CARD_RARITY.FREE)

    def create_minion(self, player):
        return Minion(5, 1)
    