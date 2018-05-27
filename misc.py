from enum import Enum, auto

# Awesome class to name Enums
class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name
