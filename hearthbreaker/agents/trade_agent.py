from hearthbreaker.agents.basic_agents import RandomAgent
from hearthbreaker.agents.trade.possible_play import PossiblePlays,PlayMixin
from hearthbreaker.agents.trade.trade import Trade,TradeMixin,AttackMixin

class ChooseTargetMixin:
    def gdfgdfggdfgdf(self):
        print('hello')

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

class TradeAgent(TradeMixin,AttackMixin,PlayMixin,ChooseTargetMixin,RandomAgent):
    def playable_cards(self, player):
        raise Exception("unused")
        res = filter(lambda card: card.can_use(player, player.game), player.hand)
        return Util.reverse_sorted(res,Card.mana)

    def do_turn(self, player):
        #raise Exception("do_turn")
        #print("do_turn")
        self.player = player
        self.play_cards(player)
        self.attack(player)

        if not player.game.game_ended:
          self.play_cards(player)

    

    


