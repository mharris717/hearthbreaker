from hearthbreaker.agents.basic_agents import RandomAgent
from hearthbreaker.util import Util
from functools import reduce

class PossiblePlay:
    def __init__(self,cards,available_mana):
        if len(cards) == 0:
            raise Exception("PossiblePlay cards is empty")

        self.cards = cards
        self.available_mana = available_mana

    def card_mana(self):
        return reduce(lambda s,c: s + c.mana, self.cards, 0)

    def sorted_mana(self):
        return Util.reverse_sorted(map(lambda c: c.mana, self.cards))

    def value(self):
        res = self.card_mana()
        wasted = self.available_mana - self.card_mana()
        if wasted < 0:
            raise Exception("Too Much Mana")

        res += wasted*-100000000000

        factor = 100000000
        for card_mana in self.sorted_mana():
            res += card_mana*factor
            factor = factor / 10

        return res

    def __str__(self):
        names = [c.name for c in self.cards]
        s = str(names)
        return "{} {}".format(s,self.value())


class PossiblePlays:
    def __init__(self,cards,mana):
        self.cards = cards
        self.mana = mana

    def raw_plays(self):
        res = []

        possible = [card for card in filter(lambda card: card.mana <= self.mana, self.cards)]
        if len(possible) == 0:
            return [[]]

        for card in possible:
            rest = self.cards.copy()
            rest.remove(card)

            following_plays = PossiblePlays(rest,self.mana-card.mana).raw_plays()
            for following_play in following_plays:
                combined = [card] + following_play
                res.append(combined)

        res = Util.uniq_by_sorted(res)

        return res

    def plays(self):
        res = [PossiblePlay(raw,self.mana) for raw in self.raw_plays() if len(raw) > 0]
        res = sorted(res,key=PossiblePlay.value)
        res.reverse()
        return res

class TradeAgent(RandomAgent):
    def attack_minions(self, player):
        res = [minion for minion in filter(lambda minion: minion.can_attack(), player.minions)]

        if player.hero.can_attack() and false:
            res.append(player.hero)

        return res

    def playable_cards(self, player):
        res = filter(lambda card: card.can_use(player, player.game), player.hand)
        return Util.reverse_sorted(res,Card.mana)

    def targetable_minions(self,all):
        taunt = [m for m in filter(lambda m: m.taunt,all)]
        if len(taunt) > 0:
            return taunt
        else:
            return all

    def trades(self,player):
        res = []

        me = self.attack_minions(player)
        opp = self.targetable_minions(player.opponent.minions)

        for my_minion in me:
            for opp_minion in opp:
                trade = Trade(player,my_minion,opp_minion)
                res.append(trade)

        res = sorted(res,key=Trade.value)
        res.reverse()

        return res

    def play_cards(self, player):
        if len(player.minions) == 7: return

        plays = PossiblePlays(player.hand,player.mana).plays()

        if len(plays) > 0:
            play = plays[0]
            if len(play.cards) == 0:
                raise Exception("play has no cards")

            #print("Playing {} Mana {} Board {}".format(play.cards[0].name,player.mana,len(player.minions)))
            card = play.cards[0]
            player.game.play_card(card)
            self.play_cards(player)

    def attack_once(self,player):
        attack_minions = self.attack_minions(player)
        trades = self.trades(player)
        if len(trades) > 0:
            self.current_trade = trades[0]
            self.current_trade.my_minion.attack()
        else:
            self.current_trade = Trade(player,attack_minions[0],player.opponent.hero)
            self.current_trade.my_minion.attack()

    def attack(self,player):
        attack_minions = self.attack_minions(player)
        if len(attack_minions) > 0:
            self.attack_once(player)
            self.attack(player)

    def do_turn(self, player):
        self.player = player
        self.play_cards(player)

        self.attack(player)

    def choose_target_enemy(self, targets):
        if not self.current_trade:
            raise Exception("No current trade")

        if len(targets) == 0:
            raise Exception("No targets")

        for target in targets:
            if self.current_trade.opp_minion == target:
                return target

        raise Exception("Could not find target")

    def choose_target_friendly(self,targets):
        return targets[0]

    def target_owner(self,player,target):
        for minion in player.minions:
            if minion == target: return "Me"
        for minion in player.opponent.minions:
            if minion == target: return "Opponent"

        if target.name == "Hero": return "Hero"

        raise Exception("No Owner of {}".format(target.name))


    def choose_target(self,targets):
        if len(targets) == 0: return None
        owners = [self.target_owner(self.player,target) for target in targets]
        # print(owners)
        return self.choose_target_enemy(targets)
            
class FakeCard:
    def __init__(self,card):
        self.health = card.health
        self.attack = card.attack

class Trade:
    def __init__(self,player,my_minion,opp_minion):
        self.player = player
        self.my_minion = my_minion
        self.opp_minion = opp_minion

    def after_attack(self):
        res = {}
        res["my_minion"] = self.after_damage(self.my_minion,self.opp_minion)
        res["opp_minion"] = self.after_damage(self.opp_minion,self.my_minion)
        return res

    def after_damage(self,target,attacker):
        res = FakeCard(target)
        res.health -= attacker.base_attack
        return res

    def value(self): 
        res = 0

        if self.after_attack()['my_minion'].health > 0:
            res += 1

        if self.after_attack()['opp_minion'].health <= 0:
            res += 1

        return res

    def minion_desc(self,minion):
        return "{}/{}".format(minion.base_attack,minion.health)

    def __str__(self):
        return "Trade {} for {}".format(self.minion_desc(self.my_minion),self.minion_desc(self.opp_minion))



