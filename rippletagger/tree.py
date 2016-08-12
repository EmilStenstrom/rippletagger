# -*- coding: utf-8 -*-

from codecs import open
from node import Node
from fwobject import FWObject

class SCRDRTree:
    """
    Single Classification Ripple Down Rules tree for Part-of-Speech and morphological tagging
    """

    def __init__(self, root=None):
        self.root = root

    # Build tree from file containing rules using FWObject
    def constructSCRDRtreeFromRDRfile(self, rulesFilePath):

        self.root = Node(FWObject(False), "NN", None, None, None, [], 0)
        currentNode = self.root
        currentDepth = 0

        rulesFile = open(rulesFilePath, "r", encoding="utf-8")
        lines = rulesFile.readlines()

        for i in xrange(1, len(lines)):
            line = lines[i]
            depth = 0
            for c in line:
                if c == '\t':
                    depth = depth + 1
                else:
                    break

            line = line.strip()
            if len(line) == 0:
                continue

            temp = line.find("cc")
            if temp == 0:
                continue

            condition = getCondition(line.split(" : ", 1)[0].strip())
            conclusion = getConcreteValue(line.split(" : ", 1)[1].strip())

            node = Node(condition, conclusion, None, None, None, [], depth)

            if depth > currentDepth:
                currentNode.exceptChild = node
            elif depth == currentDepth:
                currentNode.elseChild = node
            else:
                while currentNode.depth != depth:
                    currentNode = currentNode.father
                currentNode.elseChild = node

            node.father = currentNode
            currentNode = node
            currentDepth = depth

    def findFiredNode(self, fwObject):
        currentNode = self.root
        firedNode = None
        obContext = fwObject.context
        while True:
            # Check whether object satisfying the current node's condition
            cnContext = currentNode.condition.context
            satisfied = True
            for i in xrange(13):
                if (cnContext[i] is not None):
                    if cnContext[i] != obContext[i]:
                        satisfied = False
                        break

            if(satisfied):
                firedNode = currentNode
                exChild = currentNode.exceptChild
                if exChild is None:
                    break
                else:
                    currentNode = exChild
            else:
                elChild = currentNode.elseChild
                if elChild is None:
                    break
                else:
                    currentNode = elChild
        return firedNode

def getConcreteValue(str):
    if str.find('""') > 0:
        if str.find("Word") > 0:
            return "<W>"
        elif str.find("suffixL") > 0:
            return "<SFX>"
        else:
            return "<T>"
    return str[str.find("\"") + 1: len(str) - 1]

def getCondition(strCondition):
    condition = FWObject(False)
    for rule in strCondition.split(" and "):
        rule = rule.strip()
        key = rule[rule.find(".") + 1: rule.find(" ")]
        value = getConcreteValue(rule)

        if key == "prevWord2":
            condition.context[0] = value
        elif key == "prevTag2":
            condition.context[1] = value
        elif key == "prevWord1":
            condition.context[2] = value
        elif key == "prevTag1":
            condition.context[3] = value
        elif key == "word":
            condition.context[4] = value
        elif key == "tag":
            condition.context[5] = value
        elif key == "nextWord1":
            condition.context[6] = value
        elif key == "nextTag1":
            condition.context[7] = value
        elif key == "nextWord2":
            condition.context[8] = value
        elif key == "nextTag2":
            condition.context[9] = value
        elif key == "suffixL2":
            condition.context[10] = value
        elif key == "suffixL3":
            condition.context[11] = value
        elif key == "suffixL4":
            condition.context[12] = value

    return condition