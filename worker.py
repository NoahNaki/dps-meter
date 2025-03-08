import time
from skill_map import SKILL_TO_CLASS  # <-- CHANGED: Import from skill_map
# from aggregator import SKILL_TO_CLASS  # (REMOVED)

def combat_log_worker(reader, parser, aggregator, stop_event):
    seen_lines = set(reader.get_combat_chat_log())
    while not stop_event.is_set():
        try:
            combat_log = reader.get_combat_chat_log()
            for line in combat_log:
                line = line.strip()
                if not line or line in seen_lines:
                    continue
                seen_lines.add(line)
                result = parser.evaluate_combat_log_line(line)
                if result:
                    actor, damage, target, skill, critical = result
                    print(f"[DEBUG] Worker parsed line -> actor: {actor}, skill: {skill}, damage: {damage}")
                    aggregator.update(actor, damage, critical)

                    # Attempt to guess the class from the skill
                    guessed_class = SKILL_TO_CLASS.get(skill, None)
                    if guessed_class:
                        print(f"[DEBUG] Guessed class {guessed_class} for actor {actor} from skill {skill}")
                        aggregator.set_actor_class(actor, guessed_class)
                    else:
                        print(f"[DEBUG] No class guess for skill '{skill}'")

            time.sleep(1)
        except Exception as e:
            print("Error in combat log worker:", e)
            time.sleep(5)
