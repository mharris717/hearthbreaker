import copy
import json
import abc
from hearthbreaker.constants import MINION_TYPE
from hearthbreaker.game_objects import Effect, MinionCard, SecretCard, Minion, Character


class Immune(Effect):
    """
    Gives a character immunity.  This immunity will last until the end of the player' turn
    """

    def apply(self):
        self.target.immune = True
        self.target.game.current_player.bind("turn_ended", self.remove_immunity)

    def unapply(self):
        self.remove_immunity()
        self.target.game.current_player.unbind("turn_ended", self.remove_immunity)

    def remove_immunity(self):
        self.target.immune = False

    def __str__(self):
        return "Immune"


class Aura():
    def __init__(self, apply_func, unapply_func, filter_func):
        self.apply = apply_func
        self.unapply = unapply_func
        self.filter = filter_func


class AuraEffect(Effect):
    def __init__(self, apply_aura, unapply_aura, minion_filter="minion", players="friendly", include_self=False):
        self.apply_aura = apply_aura
        self.unapply_aura = unapply_aura
        self.minion_filter = minion_filter
        self.players = players
        self.aura = None
        self.include_self = include_self

    def apply(self):
        if self.minion_filter == "minion":
            if self.include_self:
                filter_func = lambda m: True
            else:
                filter_func = lambda m: m is not self.target
        elif self.minion_filter == "adjacent":
            filter_func = lambda m: m.index == self.target.index + 1 or m.index == self.target.index - 1
        else:
            type_id = MINION_TYPE.from_str(self.minion_filter)
            if self.include_self:
                filter_func = lambda m: m.card.minion_type == type_id
            else:
                filter_func = lambda m: m is not self.target and m.card.minion_type == type_id

        if self.players == "friendly":
            players = [self.target.player]
        elif self.players == "enemy":
            players = [self.target.player.opponent]
        elif self.players == "both":
            players = [self.target.player, self.target.player.opponent]
        self.aura = Aura(self.apply_aura, self.unapply_aura, filter_func)
        for player in players:
            player.auras.append(self.aura)

    def unapply(self):
        if self.players == "friendly":
            players = [self.target.player]
        elif self.players == "enemy":
            players = [self.target.player.opponent]
        elif self.players == "both":
            players = [self.target.player, self.target.player.opponent]

        for player in players:
            player.auras.remove(self.aura)

    def __str__(self):
        return json.dumps(self.__to_json__())

    def __to_json__(self):
        return {
            "filter": self.minion_filter,
            "players": self.players,
            "include_self": self.include_self
        }


class ChargeAura(AuraEffect):
    """
     A Charge Aura gives affected minions charge.   Whether the minions are friendly or not as well as what
     type of minions are affected can be customized
    """

    def __init__(self, players="friendly", minion_filter="minion", include_self=False):
        """
        Create a new ChargeAura
        :param string players: Whose minions should be given charge.  Possible values are "friendly", "enemy" and "both"
        :param string minion_filter: A string representing either a minion type ("Beast", "Dragon", etc.) or "minion"
                                     for any type of minion
        :param boolean include_self: Whether or not this aura should also affect the minion that created it.
        """
        super().__init__(self.give_charge, self.take_charge, minion_filter, players, include_self)
        self.affected_minions = set()

    def give_charge(self, minion):
        if not minion.charge:
            minion.charge = True
            self.affected_minions.add(minion)

    def take_charge(self, minion):
        if minion in self.affected_minions:
            minion.charge = False
            self.affected_minions.remove(minion)

    def __to_json__(self):
        return super().__to_json__().update({
            "type": "charge"
        })


class StatsAura(AuraEffect):
    """
    A StatsAura increases the health and/or attack of affected minions.  Whether the minions are friendly or not as well
    as what type of minions are affected can be customized.
    """

    def __init__(self, attack=0, health=0, players="friendly", minion_filter="minion"):
        """
        Create a new StatsAura

        :param int attack: The amount to increase this minion's attack by
        :param int health: The amount to increase this minion's health by
        :param string players: Whose minions should be given charge.  Possible values are "friendly", "enemy" and "both"
        :param string minion_filter: A string representing either a minion type ("Beast", "Dragon", etc.) or "minion"
                                     for any type of minion
        """
        super().__init__(self.increase_stats, self.decrease_stats, minion_filter, players)
        self.attack = attack
        self.health = health

    def increase_stats(self, minion):
        minion.aura_attack += self.attack
        minion.aura_health += self.health
        minion.health += self.health

    def decrease_stats(self, minion):
        minion.aura_attack -= self.attack
        minion.aura_health -= self.health
        if minion.health > minion.calculate_max_health():
            minion.health = minion.calculate_max_health()

    def __to_json__(self):
        return super().__to_json__().update({
            "type": "stats",
            "attack": self.attack,
            "health": self.health,
        })


class IncreaseBattlecryMinionCost(Effect):
    def __init__(self, amount):
        super().__init__()
        self.amount = amount
        self.mana_filter = None

    def apply(self):
        amount = self.amount
        target = self.target

        class Filter:
            def __init__(self):
                self.amount = -amount
                self.filter = lambda c: isinstance(c, MinionCard) and \
                    c.create_minion(target.player).battlecry is not None
                self.min = 0

        self.mana_filter = Filter()
        self.target.game.current_player.mana_filters.append(self.mana_filter)
        self.target.game.other_player.mana_filters.append(self.mana_filter)

    def unapply(self):
        self.target.game.current_player.mana_filters.remove(self.mana_filter)
        self.target.game.other_player.mana_filters.remove(self.mana_filter)

    def __str__(self):
        return "IncreaseMinionCost(battlecry, {0})".format(self.amount)

    def __to_json__(self):
        return {
            "action": "increase_battlecry",
            "amount": self.amount,
        }


class DoubleDeathrattle(Effect):
    def apply(self):
        if self.target.player.effect_count[DoubleDeathrattle] == 1:
            self.target.player.bind("minion_died", self.trigger_deathrattle)

    def unapply(self):
        if self.target.player.effect_count[DoubleDeathrattle] == 0:
            self.target.player.unbind("minion_died", self.trigger_deathrattle)

    def trigger_deathrattle(self, minion, killed_by):
        minion.deathrattle(minion)

    def __str__(self):
        return "DoubleDeathrattle()"


class HealAsDamage(Effect):
    def apply(self):
        if self.target.player.effect_count[HealAsDamage] == 1:
            self.target.player.heal_does_damage = True

    def unapply(self):
        if self.target.player.effect_count[HealAsDamage] == 0:
            self.target.player.heal_does_damage = False

    def __str__(self):
        return "HealAsDamage()"


class ManaFilter(Effect):
    """
    Associates a mana filter with this minion.  A mana filter affects a player by making cards of a certain type
    cost more or less.  The amount to change, player affected, and cards changed can all be customized
    """

    def __init__(self, amount, filter_type="card", minimum=0, player="friendly"):
        """
        Creates a new mana filter

        :param int amount: The amount to reduce mana by (can be negative)
        :param string filter_type: A filter to determine which cards can be affected.  Should be one of "card",
                                   "spell", "secret" or "minion"
        :param int minimum: The least amount that this filter can adjust the card to

        """
        super().__init__()
        self.amount = amount
        self.minimum = minimum
        self.filter_type = filter_type
        self.filter_object = None
        self.player = player

    def apply(self):
        if self.filter_type == "minion":
            my_filter = lambda c: isinstance(c, MinionCard)
        elif self.filter_type == "spell":
            my_filter = lambda c: c.is_spell()
        elif self.filter_type == "secret":
            my_filter = lambda c: isinstance(c, SecretCard)
        else:
            my_filter = lambda c: True

        class Filter:
            def __init__(self, amount, minimum, filter):
                self.amount = amount
                self.min = minimum
                self.filter = filter

        self.filter_object = Filter(self.amount, self.minimum, my_filter)
        if self.player == "friendly" or self.player == "both":
            self.target.player.mana_filters.append(self.filter_object)
        if self.player == "enemy" or self.player == "both":
            self.target.player.opponent.mana_filters.append(self.filter_object)

    def unapply(self):
        if self.player == "friendly" or self.player == "both":
            self.target.player.mana_filters.remove(self.filter_object)
        if self.player == "enemy" or self.player == "both":
            self.target.player.opponent.mana_filters.remove(self.filter_object)

    def __str__(self):
        return "ManaFilter({0}, {1}, {2}, {3})".format(self.amount, self.minimum, self.filter_type, self.player)


class EventEffect(Effect, metaclass=abc.ABCMeta):
    def __init__(self, when, minion_filter="self", target="self", players="friendly"):
        super().__init__()
        self.when = when
        self.minion_filter = minion_filter
        self.action_target = target
        self.players = players
        self.other = None

    def apply(self):
        if self.players == "friendly":
            players = [self.target.player]
        elif self.players == "enemy":
            players = [self.target.player.opponent]
        elif self.players == "both":
            players = [self.target.player, self.target.player.opponent]
        else:
            raise RuntimeError("Required players to be 'friendly', 'enemy', or 'both', got '{0}".format(self.players))

        if self.when == "death":
            for player in players:
                player.bind("minion_died", self._check_minion_filter)
        elif self.when == "damaged":
            for player in players:
                player.bind("minion_damaged", self._check_minion_filter)
        elif self.when == "summoned":
            for player in players:
                player.bind("minion_summoned", self._check_minion_filter)
        elif self.when == "played":
            if self.minion_filter == "spell" or self.minion_filter == "secret" or self.minion_filter == "card":
                for player in players:
                    player.bind("card_played", self._check_card_filter)
            else:
                for player in players:
                    player.bind("minion_played", self._check_minion_filter)
        elif self.when == "placed":
            for player in players:
                    player.bind("minion_placed", self._check_minion_filter)
        elif self.when == "attack":
            self.target.bind("attack", self._check_minion_filter)
        elif self.when == "attacked":
            self.target.bind("attacked", self._check_minion_filter)
        elif self.when == "did_damage":
            self.target.bind("did_damage", self._check_minion_filter)
        elif self.when == "turn_ended":
            for player in players:
                player.bind("turn_ended", self._check_turn_end_filter)
        elif self.when == "turn_started":
            for player in players:
                player.bind("turn_started", self._check_turn_end_filter)

    def unapply(self):
        if self.players == "friendly":
            players = [self.target.player]
        elif self.players == "enemy":
            players = [self.target.player.opponent]
        elif self.players == "both":
            players = [self.target.player, self.target.player.opponent]
        else:
            raise RuntimeError("Required players to be 'friendly', 'enemy', or 'both', got '{0}".format(self.players))

        if self.when == "death":
            for player in players:
                player.unbind("minion_died", self._check_minion_filter)
        elif self.when == "damaged":
            for player in players:
                player.unbind("minion_damaged", self._check_minion_filter)
        elif self.when == "summoned":
            for player in players:
                player.unbind("minion_summoned", self._check_minion_filter)
        elif self.when == "played":
            if self.minion_filter == "spell" or self.minion_filter == "secret" or self.minion_filter == "card":
                for player in players:
                    player.unbind("card_played", self._check_card_filter)
            else:
                for player in players:
                    player.unbind("minion_played", self._check_minion_filter)
        elif self.when == "placed":
            for player in players:
                    player.unbind("minion_placed", self._check_minion_filter)
        elif self.when == "attack":
            self.target.unbind("attack", self._check_minion_filter)
        elif self.when == "attacked":
            self.target.unbind("attacked", self._check_minion_filter)
        elif self.when == "did_damage":
            self.target.unbind("did_damage", self._check_minion_filter)
        elif self.when == "turn_ended":
            for player in players:
                player.unbind("turn_ended", self._check_turn_end_filter)
        elif self.when == "turn_started":
            for player in players:
                player.unbind("turn_started", self._check_turn_end_filter)

    def _check_minion_filter(self, minion, *args):
        self.other = minion
        if self.minion_filter == "self":
            if minion == self.target:
                self._select_target()
        elif self.minion_filter == "minion":
            self._select_target()
        elif self.minion_filter == "deathrattle" and minion.deathrattle is not None:
            self._select_target()
        elif self.target is not minion:
            try:
                type_id = MINION_TYPE.from_str(self.minion_filter)
                if minion.card.minion_type == type_id:
                    self._select_target()
            except KeyError:
                pass

    def _check_card_filter(self, card, index):
        if self.minion_filter == "spell" and card.is_spell():
            self._select_target()
        elif self.minion_filter == "secret" and isinstance(card, SecretCard):
            self._select_target()
        elif self.minion_filter == "card":
            self._select_target()

    def _check_turn_end_filter(self):
        if self.minion_filter != "secret" or len(self.target.player.secrets) > 0:
            self._select_target()

    def _select_target(self):
        if self.action_target == "self":
            target = self.target
        elif self.action_target == "other":
            target = self.other
        else:
            if self.action_target == "random":
                targets = copy.copy(self.target.player.minions)
                targets.extend(self.target.player.opponent.minions)
                targets.remove(self.target)
            elif self.action_target == "random_friendly":
                targets = copy.copy(self.target.player.minions)
                targets.remove(self.target)
            elif self.action_target == "random_enemy":
                targets = copy.copy(self.target.player.opponent.minions)
            else:
                raise RuntimeError("Expected 'target' to be one of 'self', 'other', 'random', " +
                                   "'random_friendly' or 'random_enemy'.  Got '{0}'".format(self.action_target))
            target = targets[self.target.game.random(0, len(targets) - 1)]
        self._do_action(target)

    @abc.abstractmethod
    def _do_action(self, target):
        pass

    def __str__(self):
        return json.dumps(self.__to_json__())

    def __to_json__(self):
        return {
            "when": self.when,
            "filter": self.minion_filter,
            "target": self.action_target,
            "players": self.players,
        }


class Buff(EventEffect):
    def __init__(self, when, minion_filter="self", target="self", attack=0, health=0, players="friendly"):
        super().__init__(when, minion_filter, target, players)
        self.attack = attack
        self.health = health

    def _do_action(self, target):
        if self.health > 0:
            target.increase_health(self.health)
        elif self.health < 0:
            target.decrease_health(-self.health)
        if self.attack != 0:
            target.change_attack(self.attack)

    def __to_json__(self):
        return super().__to_json__().update({
            "action": "buff",
            "attack": self.attack,
            "health": self.health,
        })


class Kill(EventEffect):
    def __init__(self, when, minion_filter="self", target="self", players="friendly"):
        super().__init__(when, minion_filter, target, players)

    def _do_action(self, target):
        if isinstance(target, Minion):
            target.die(None)

    def __to_json__(self):
        return super().__to_json__().update({
            "action": "kill",
        })


class Freeze(EventEffect):
    def __init__(self, when, minion_filter="self", target="self", players="friendly"):
        super().__init__(when, minion_filter, target, players)

    def _do_action(self, target):
        if isinstance(target, Character):
            target.freeze()

    def __to_json__(self):
        return super().__to_json__().update({
            "action": "freeze",
        })


class EventEffectPlayer(EventEffect):
    def __init__(self, when, minion_filter="self", target="owner", players="friendly"):
        super().__init__(when, minion_filter, target, players)

    def _select_target(self):
        if self.action_target == "owner":
            self._do_action(self.target.player)
        elif self.action_target == "opponent":
            self._do_action(self.target.player.opponent)
        elif self.action_target == "p1":
            self._do_action(self.target.game.players[0])
        elif self.action_target == "p2":
            self._do_action(self.target.game.players[1])


class AddCard(EventEffectPlayer):
    def __init__(self, when, card, minion_filter="self", target="owner", players="friendly"):
        super().__init__(when, minion_filter, target, players)
        self.card = card

    def _do_action(self, target):
        if len(target.hand) < 10:
            target.hand.append(self.card())

    def __to_json__(self):
        return super().__to_json__().update({
            "action": "add_card",
            "card": self.card.name
        })


class Draw(EventEffectPlayer):
    def __init__(self, when, minion_filter="self", target="owner", players="friendly"):
        super().__init__(when, minion_filter, target, players)

    def _do_action(self, target):
        target.draw()

    def __to_json__(self):
        return super().__to_json__().update({
            "action": "draw",
        })


class Summon(EventEffectPlayer):
    def __init__(self, when, card, minion_filter="self", target="owner", players="friendly"):
        super().__init__(when, minion_filter, target, players)
        self.card = card

    def _do_action(self, target):
        self.card().summon(target, target.game, len(target.minions))

    def __to_json__(self):
        return super().__to_json__().update({
            "action": "summon",
            "card": self.card.name
        })


class ResurrectFriendlyMinionsAtEndOfTurn(Effect):
    def __init__(self):
        super().__init__()

    def apply(self):
        self.target.player.bind("turn_ended", self._turn_ended)
        self.target.player.opponent.bind("turn_ended", self._turn_ended)

    def unapply(self):
        self.target.player.unbind("turn_ended", self._turn_ended)
        self.target.player.opponent.unbind("turn_ended", self._turn_ended)

    def _turn_ended(self):
        # Will be called once per Kel'Thuzad on the board
        # http://www.hearthhead.com/card=1794/kelthuzad#comments
        for minion in sorted(self.target.player.dead_this_turn, key=lambda m: m.born):
            minion.card.summon(self.target.player, self.target.game, len(self.target.player.minions))

    def __to_json__(self):
        return {
            "action": "resurrect_frendly"
        }

    def __str__(self):
        return ""
