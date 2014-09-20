from hearthbreaker.game_objects import Hero
from functools import reduce

class FakeCard:
    def __init__(self,card):
        self.health = card.health
        self.attack = card.base_attack
        self.base_attack = card.base_attack
        if hasattr(card,"taunt"):
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

    def is_lethal(self):
        return false
        #return self.opp_minion.__class__ == Hero and self.my_minion.attack >= self.opp_minion.player.hero.health

    def is_opp_dead(self):
        return self.after_attack()['opp_minion'].health <= 0

    def needs_sequence(self): return True

class TradeSequence:
    def __init__(self,current_trades_obj,past_trades=[]):
        self.past_trades = past_trades
        self.current_trades_obj = current_trades_obj

    def after_next_trade(self,next_trade):
        past_trades = self.past_trades
        past_trades.append(next_trade)

        trades_obj = Trades(self.current_trades_obj.player,self.current_trades_obj.attack_minions.copy(),self.current_trades_obj.opp_minions.copy(),self.current_trades_obj.opp_hero.copy(None,None))
        trades_obj.attack_minions.remove(next_trade.my_minion)
        if next_trade.is_opp_dead():
            trades_obj.opp_minions.remove(next_trade.opp_minion)
            if len(trades_obj.opp_minions)+1 != len(self.current_trades_obj.opp_minions):
                raise Exception("didn't remove defending minion")

        if len(trades_obj.attack_minions)+1 != len(self.current_trades_obj.attack_minions):
            raise Exception("didn't remove my attacking minion")

        res = TradeSequence(trades_obj,past_trades)
        return res

    def has_lethal(self):
        return self.current_trades_obj.has_lethal()

    def past_trade_value(self):
        if self.has_lethal():
            return 99999999
        else:
            return reduce(lambda s,t: s + t.value(),self.past_trades,0.0)

    def future_trade_value(self):
        if self.has_lethal(): return 9999999999
        if len(self.current_trades_obj.attack_minions) == 0: return 0.0

        next_trades = self.current_trades_obj.trades()
        if len(next_trades) == 0: return 0.0

        next_seq = self.after_next_trade(next_trades[0])
        return next_trades[0].value() + next_seq.future_trade_value()

    def trade_value(self):
        return self.past_trade_value() + self.future_trade_value()




class FaceTrade(Trade):
    def value(self):
        if self.is_lethal(): return 9999999
        return self.my_minion.base_attack * 0.2

    def __str__(self):
        return "Face {} Value {}".format(self.minion_desc(self.my_minion),self.value())

    def is_lethal(self):
        return self.my_minion.base_attack >= self.opp_minion.health

    def needs_sequence(self): return False


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

    def total_attack(self):
        return reduce(lambda s,i: s+i.base_attack,self.attack_minions,0)

    def has_lethal(self):
        #s = "Taunt: {}, {} vs {}".format(self.opp_has_taunt(),self.total_attack(),self.opp_hero.health)
        #print(s)
        return not self.opp_has_taunt() and self.total_attack() >= self.opp_hero.health

    def trade_value(self,trade):
        if not trade.needs_sequence() or len(self.attack_minions) <= 1: 
            return trade.value()

        seq = TradeSequence(self).after_next_trade(trade)
        return seq.trade_value()

    def trades(self):
        res = []

        me = self.attack_minions
        opp = self.targetable_minions(self.opp_minions)

        if not self.has_lethal():
            for my_minion in me:
                for opp_minion in opp:
                    trade = Trade(self.player,my_minion,opp_minion)
                    res.append(trade)

        if not self.opp_has_taunt():
            for my_minion in me:
                trade = FaceTrade(self.player,my_minion,self.opp_hero)
                res.append(trade)

        res = sorted(res,key=self.trade_value)
        res.reverse()

        return res

    def targetable_minions(self,all):
        taunt = [m for m in filter(lambda m: m.taunt,all)]
        if len(taunt) > 0:
            return taunt
        else:
            return all

    def __str__(self):
        res = ["\nTRADES:"]
        for t in self.trades():
            s = t.__str__()
            s += " Root Value: {}".format(self.trade_value(t))
            res.append(s)
        return str.join("\n",res)



class TradeMixin:
    def trades(self,player):
        res = Trades(player,self.attack_minions(player),player.opponent.minions,player.opponent.hero)
        return [t for t in res.trades() if t.value() > -1]



class AttackMixin:
    def attack_once(self,player):
        attack_minions = self.attack_minions(player)
        trades = self.trades(player)
        if len(trades) > 0:
            self.current_trade = trades[0]
            self.current_trade.my_minion.attack()

    def attack(self,player):
        if len(self.trades(player)) > 0:
            self.attack_once(player)
            self.attack(player)

    def attack_minions(self, player):
        res = [minion for minion in filter(lambda minion: minion.can_attack(), player.minions)]

        if player.hero.can_attack() and false:
            res.append(player.hero)

        return res

    