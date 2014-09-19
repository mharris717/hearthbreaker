class FakeCard:
    def __init__(self,card):
        self.health = card.health
        self.attack = card.base_attack
        self.base_attack = card.base_attack
        self.taunt = card.taunt

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

    def start_value(self):
        return self.minion_value(self.my_minion) - self.minion_value(self.opp_minion)

    def end_value(self):
        return self.minion_value(self.after_attack()['my_minion']) - self.minion_value(self.after_attack()['opp_minion'])

    def value(self): 
        res = self.end_value() - self.start_value()

        if self.after_attack()['my_minion'].health > 0 and self.after_attack()['opp_minion'].health <= 0:
            res += 1.0

        return round(res,2)

    def minion_desc(self,minion):
        return "{}/{}".format(minion.base_attack,minion.health)

    def __str__(self):
        return "Trade {} for {} Value {}".format(self.minion_desc(self.my_minion),self.minion_desc(self.opp_minion),self.value())

    def minion_value(self,minion):
        if minion.health <= 0: return 0

        res = (minion.base_attack+0.5) * minion.health**1.5
        if minion.taunt: res += 0.5
        return res**0.4

class FaceTrade(Trade):
    def value(self):
        return self.my_minion.base_attack * 0.2

    def __str__(self):
        return "Face {} Value {}".format(self.minion_desc(self.my_minion),self.value())

class Trades:
    def __init__(self,player,attack_minions,opp_minions,opp_hero):
        self.player = player
        self.attack_minions = attack_minions
        self.opp_minions = opp_minions
        self.opp_hero = opp_hero

    def opp_has_taunt(self):
        for minion in self.opp_minions:
            if minion.taunt: return True
        return False

    def trades(self):
        res = []

        me = self.attack_minions
        opp = self.targetable_minions(self.opp_minions)

        for my_minion in me:
            for opp_minion in opp:
                trade = Trade(self.player,my_minion,opp_minion)
                res.append(trade)

        if not self.opp_has_taunt():
            for my_minion in me:
                trade = FaceTrade(self.player,my_minion,self.opp_hero)
                res.append(trade)

        res = sorted(res,key=lambda t: t.value())
        res.reverse()

        return res

    def targetable_minions(self,all):
        taunt = [m for m in filter(lambda m: m.taunt,all)]
        if len(taunt) > 0:
            return taunt
        else:
            return all



class TradeMixin:
    def trades(self,player):
        res = Trades(player,self.attack_minions(player),player.opponent.minions,player.opponent.hero)
        return res.trades()



class AttackMixin:
    def attack_once(self,player):
        attack_minions = self.attack_minions(player)
        trades = self.trades(player)
        if len(trades) > 0:
            #print(trades[0])
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

    def attack_minions(self, player):
        res = [minion for minion in filter(lambda minion: minion.can_attack(), player.minions)]

        if player.hero.can_attack() and false:
            res.append(player.hero)

        return res

    