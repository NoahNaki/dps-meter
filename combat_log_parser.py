import re

class CombatLogParser:
    OtherPlayerExpression = re.compile(
        r"(?P<target>.+?) received (?P<damage>\d+(?:,\d+)?) (?P<critical>Critical Damage|damage)(?: and Daze)? from (?P<actor>.+?)&apos;s (?P<skill>.+?)(?:\.)?"
    )
    YouExpression = re.compile(
        r"(?P<skill>.+?) (?P<critical>critically hit|hit) (?P<target>.+?) for (?P<damage>\d+(?:,\d+)?) damage(?:\.)?"
    )
    ReceivedExpression1 = re.compile(
        r"Received (?P<damage>\d+(?:,\d+)?) damage from (?P<actor>.+?)&apos;s (?P<skill>.+?)(?:\.)?"
    )
    ReceivedExpression2 = re.compile(
        r"(?P<actor>.+?)&apos;s (?P<skill>.+?) inflicted (?P<damage>\d+(?:,\d+)?) damage(?: and (?P<debuff>.+?))?(?:\.)?"
    )
    BlockedExpression = re.compile(
        r"Blocked (?P<actor>.+?)&apos;s (?P<skill>.+?) but received (?P<damage>\d+(?:,\d+)?) damage(?:\.)?"
    )

    @staticmethod
    def evaluate_combat_log_line(line):
        match = CombatLogParser.OtherPlayerExpression.match(line)
        if match:
            target = match.group("target")
            actor = match.group("actor")
            damage = int(match.group("damage").replace(",", ""))
            skill = match.group("skill")
            critical = "critical" in match.group("critical").lower()
            return (actor, damage, target, skill, critical)

        match = CombatLogParser.YouExpression.match(line)
        if match:
            target = match.group("target")
            damage = int(match.group("damage").replace(",", ""))
            skill = match.group("skill")
            critical = "critical" in match.group("critical").lower()
            return ("You", damage, target, skill, critical)

        match = CombatLogParser.ReceivedExpression1.match(line)
        if match:
            actor = match.group("actor")
            damage = int(match.group("damage").replace(",", ""))
            skill = match.group("skill")
            return (actor, damage, "You", skill, False)

        match = CombatLogParser.ReceivedExpression2.match(line)
        if match:
            actor = match.group("actor")
            damage = int(match.group("damage").replace(",", ""))
            skill = match.group("skill")
            return (actor, damage, "You", skill, False)

        match = CombatLogParser.BlockedExpression.match(line)
        if match:
            actor = match.group("actor")
            damage = int(match.group("damage").replace(",", ""))
            skill = match.group("skill")
            return (actor, damage, "You", skill, False)

        return None
