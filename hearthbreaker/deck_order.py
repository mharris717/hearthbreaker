class DeckOrder:
    def __init__(self,*names):
        self.names = [n for n in names]

    def sort_func(self,card):
        if card.name in self.names:
            i = self.names.index(card.name)
            self.names[i] = "Gibberish"
            #print("{} for {}".format(i,card.name))
            return i
        else:
            return 99

    def sorted(self,cards):
        return sorted(cards,key=self.sort_func)

    def sorted_mana(self,cards):
        res = sorted(cards,key=self.mana_func)
        res.reverse()
        return res

    def mana_func(self,card):
        return card.mana