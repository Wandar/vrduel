# -*- coding: utf-8 -*-
from b.CardTypes import Monster

# from KBEDebug import INFO_MSG
# from cards.allcards import allcardClass

class dame(Monster):
    pass

class stone_knight(Monster):
    pass

class ghost(Monster):
    pass




class dog(Monster):
    pass





class blazingbattlemage(Monster):
    pass


# class DepthCharge(Monster):
#     def __init__(self, Game, camp):
#         self.blank_init(Game, camp)
#         self.trigsBoard = [Trig_DepthCharge(self)]
#
# class Trig_DepthCharge(TrigBoard):
#     def __init__(self, entity):
#         self.blank_init(entity, ["TurnStarts"])
#
#     def canTrig(self, signal, camp, subject, target, number, comment, choice=0):
#         return self.entity.onBoard and camp == self.entity.camp
#
#     def text(self, CHN):
#         return "在你的回合开始时，对所有随从造成5点伤害" if CHN else "At the start of your turn, deal 5 damage to all monsters"
#
#     def effect(self, signal, camp, subject, target, number, comment, choice=0):
#         targets = self.entity.Game.monstersonBoard(self.entity.camp) + self.entity.Game.monstersonBoard(3-self.entity.camp)
#         self.entity.dealsAOE(targets, [5 for monster in targets])