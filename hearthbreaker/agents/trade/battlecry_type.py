import hearthbreaker.cards.battlecries


class BattlecryType:
    @staticmethod
    def buff_battlecries():
        res = []
        res.append(hearthbreaker.cards.battlecries.heal_two)
        res.append(hearthbreaker.cards.battlecries.heal_three)
        res.append(hearthbreaker.cards.battlecries.give_divine_shield)
        res.append(hearthbreaker.cards.battlecries.give_stealth)
        res.append(hearthbreaker.cards.battlecries.give_three_health)
        res.append(hearthbreaker.cards.battlecries.two_temp_attack)
        res.append(hearthbreaker.cards.battlecries.give_windfury)
        return res

    @staticmethod
    def damage_battlecries():
        res = []
        res.append(hearthbreaker.cards.battlecries.silence)
        res.append(hearthbreaker.cards.battlecries.deal_one_damage)
        res.append(hearthbreaker.cards.battlecries.deal_two_damage)
        res.append(hearthbreaker.cards.battlecries.deal_three_damage)
        res.append(hearthbreaker.cards.battlecries.change_attack_to_one)
        res.append(hearthbreaker.cards.battlecries.take_control_of_minion)
        return res

    @staticmethod
    def target_type(cry):
        if cry in BattlecryType.buff_battlecries():
            return "Friendly"
        elif cry in BattlecryType.damage_battlecries():
            return "Enemy"
        else:
            return None

    def target_type_for_card(card):
        res = None
        if not hasattr(card, "create_minion"):
            return None

        minion = card.create_minion(None)
        if hasattr(minion, "battlecry"):
            res = BattlecryType.target_type(minion.battlecry)
        return res
