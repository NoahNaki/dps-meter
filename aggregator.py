from datetime import datetime
import threading

class Aggregator:
    def __init__(self):
        self.stats = {}
        self.seen_lines = set()
        self.lock = threading.Lock()
        self.global_start_time = None

    def update(self, actor, damage, critical):
        now = datetime.now()
        with self.lock:
            if self.global_start_time is None:
                self.global_start_time = now

            # If we haven't seen this actor yet, initialize their stats
            if actor not in self.stats:
                self.stats[actor] = {
                    "total_damage": damage,
                    "events": 1,
                    "crit_events": 1 if critical else 0,
                    "start_time": now,
                    "class": None,
                    "highest_hit": damage,  # Initialize highest_hit with this first damage
                }
            else:
                self.stats[actor]["total_damage"] += damage
                self.stats[actor]["events"] += 1
                if critical:
                    self.stats[actor]["crit_events"] += 1

                # Update highest hit if this damage is bigger
                if damage > self.stats[actor]["highest_hit"]:
                    self.stats[actor]["highest_hit"] = damage

    def get_stats(self):
        with self.lock:
            return dict(self.stats)

    def reset(self):
        with self.lock:
            self.stats = {}
            self.seen_lines = set()
            self.global_start_time = None

    def set_actor_class(self, actor, class_name):
        with self.lock:
            if actor not in self.stats:
                # If we haven't seen this actor yet, initialize
                self.stats[actor] = {
                    "total_damage": 0,
                    "events": 0,
                    "crit_events": 0,
                    "start_time": datetime.now(),
                    "class": class_name,
                    "highest_hit": 0
                }
            else:
                # If we have, just update their class
                self.stats[actor]["class"] = class_name


