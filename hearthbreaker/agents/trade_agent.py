from hearthbreaker.agents.basic_agents import RandomAgent

def uniq_by_sorted(list):
    res = {}
    for obj in list:
        a = [c.name for c in obj]
        k = str.join("",sorted(a))
        if not res.get(k):
            res[k] = obj

    return res.values()

class PossiblePlay:
    def __init__(self,cards,available_mana):
        if len(cards) == 0:
            raise Exception("PossiblePlay cards is empty")

        self.cards = cards
        self.available_mana = available_mana

    def card_mana(self):
        res = 0
        for card in self.cards:
            res += card.mana
        return res

    def sorted_mana(self):
        res = [card.mana for card in self.cards]
        res = sorted(res)
        res.reverse()
        return res

    def value(self):
        res = self.card_mana()
        wasted = self.available_mana - self.card_mana()
        if wasted < 0:
            raise Exception("Too Much Mana")

        #print("wasted {}".format(wasted))
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

        res = uniq_by_sorted(res)

        #print("Plays:")
        #for play in res:
        #    print([c.name for c in play])

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
        def mana_func(card):
            return card.mana * -1

        res = [card for card in filter(lambda card: card.can_use(player, player.game), player.hand)]
        res = [card for card in filter(lambda card: card.name != "The Coin", res)]
        return sorted(res,key=mana_func)

    def trades(self,player):
        res = []

        me = self.attack_minions(player)
        opp = player.opponent.minions

        for my_minion in me:
            for opp_minion in opp:
                trade = Trade(player,my_minion,opp_minion)
                res.append(trade)

        res = sorted(res,key=Trade.value)
        res.reverse()

        return res

    def play_cards(self, player):
        plays = PossiblePlays(player.hand,player.mana).plays()

        #print("Plays:")
        #for play in plays:
        #    print(play)

        if len(plays) > 0:
            play = plays[0]
            if len(play.cards) == 0:
                raise Exception("play has no cards")

            card = play.cards[0]
            player.game.play_card(card)
            self.play_cards(player)


    def play_cards_old(self, player):
        

        #print("Starting Mana {}".format(player.mana))
        playable_cards = self.playable_cards(player)
        while len(playable_cards) > 0:
            player.game.play_card(playable_cards[0])
            playable_cards = self.playable_cards(player)

    def do_turn(self, player):
        #print("do_turn")
        #raise Exception("actually in do_turn")
        attack_minions = self.attack_minions(player)
        #print("attack minions: {}, all: {}".format(len(attack_minions),len(player.minions)))

        

        self.play_cards(player)
        #print("playable cards: {}".format(len(playable_cards)))


        if len(attack_minions) > 0:
            self.current_trade = self.trades(player)[0]
            #print("set trade {}".format(self.current_trade))
            self.current_trade.my_minion.attack()
        else:
            return

    def choose_target(self, targets):
        if not self.current_trade:
            raise Exception("No current trade")

        if len(targets) == 0:
            raise Exception("No targets")

        for target in targets:
            if self.current_trade.opp_minion == target:
                return target

        raise Exception("Could not find target")
            
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
