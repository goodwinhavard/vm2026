GROUPS = {
    "Group A": ["Mexico", "South Africa", "South Korea", "Czech Republic"],
    "Group B": ["Canada", "Bosnia and Herzegovina", "Qatar", "Switzerland"],
    "Group C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "Group D": ["United States", "Paraguay", "Australia", "Turkey"],
    "Group E": ["Germany", "Curacao", "Ivory Coast", "Ecuador"],
    "Group F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "Group G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "Group H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "Group I": ["France", "Senegal", "Iraq", "Norway"],
    "Group J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "Group K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
    "Group L": ["England", "Croatia", "Ghana", "Panama"]
}

KNOCKOUT_DEFS = {
    "Round of 32": {
        73: {"home": {"type": "group", "group": "Group A", "position": "runner_up"}, "away": {"type": "group", "group": "Group B", "position": "runner_up"}},
        74: {"home": {"type": "group", "group": "Group E", "position": "winner"}, "away": {"type": "best_third", "groups": ["Group A", "Group B", "Group C", "Group D", "Group F"]}},
        75: {"home": {"type": "group", "group": "Group F", "position": "winner"}, "away": {"type": "group", "group": "Group C", "position": "runner_up"}},
        76: {"home": {"type": "group", "group": "Group C", "position": "winner"}, "away": {"type": "group", "group": "Group F", "position": "runner_up"}},
        77: {"home": {"type": "group", "group": "Group I", "position": "winner"}, "away": {"type": "best_third", "groups": ["Group C", "Group D", "Group F", "Group G", "Group H"]}},
        78: {"home": {"type": "group", "group": "Group E", "position": "runner_up"}, "away": {"type": "group", "group": "Group I", "position": "runner_up"}},
        79: {"home": {"type": "group", "group": "Group A", "position": "winner"}, "away": {"type": "best_third", "groups": ["Group C", "Group E", "Group F", "Group H", "Group I"]}},
        80: {"home": {"type": "group", "group": "Group L", "position": "winner"}, "away": {"type": "best_third", "groups": ["Group E", "Group H", "Group I", "Group J", "Group K"]}},
        81: {"home": {"type": "group", "group": "Group D", "position": "winner"}, "away": {"type": "best_third", "groups": ["Group B", "Group E", "Group F", "Group I", "Group J"]}},
        82: {"home": {"type": "group", "group": "Group G", "position": "winner"}, "away": {"type": "best_third", "groups": ["Group A", "Group E", "Group H", "Group I", "Group J"]}},
        83: {"home": {"type": "group", "group": "Group K", "position": "runner_up"}, "away": {"type": "group", "group": "Group L", "position": "runner_up"}},
        84: {"home": {"type": "group", "group": "Group H", "position": "winner"}, "away": {"type": "group", "group": "Group J", "position": "runner_up"}},
        85: {"home": {"type": "group", "group": "Group B", "position": "winner"}, "away": {"type": "best_third", "groups": ["Group E", "Group F", "Group G", "Group I", "Group J"]}},
        86: {"home": {"type": "group", "group": "Group J", "position": "winner"}, "away": {"type": "group", "group": "Group H", "position": "runner_up"}},
        87: {"home": {"type": "group", "group": "Group K", "position": "winner"}, "away": {"type": "best_third", "groups": ["Group D", "Group E", "Group I", "Group J", "Group L"]}},
        88: {"home": {"type": "group", "group": "Group D", "position": "runner_up"}, "away": {"type": "group", "group": "Group G", "position": "runner_up"}},
    },
    "Round of 16": {
        89: {"home": {"type": "match", "match": 74}, "away": {"type": "match", "match": 77}},
        90: {"home": {"type": "match", "match": 73}, "away": {"type": "match", "match": 75}},
        91: {"home": {"type": "match", "match": 76}, "away": {"type": "match", "match": 78}},
        92: {"home": {"type": "match", "match": 79}, "away": {"type": "match", "match": 80}},
        93: {"home": {"type": "match", "match": 83}, "away": {"type": "match", "match": 84}},
        94: {"home": {"type": "match", "match": 81}, "away": {"type": "match", "match": 82}},
        95: {"home": {"type": "match", "match": 86}, "away": {"type": "match", "match": 88}},
        96: {"home": {"type": "match", "match": 85}, "away": {"type": "match", "match": 87}},
    },
    "Quarterfinals": {
        97: {"home": {"type": "match", "match": 89}, "away": {"type": "match", "match": 90}},
        98: {"home": {"type": "match", "match": 93}, "away": {"type": "match", "match": 94}},
        99: {"home": {"type": "match", "match": 91}, "away": {"type": "match", "match": 92}},
        100: {"home": {"type": "match", "match": 95}, "away": {"type": "match", "match": 96}},
    },
    "Semifinals": {
        101: {"home": {"type": "match", "match": 97}, "away": {"type": "match", "match": 98}},
        102: {"home": {"type": "match", "match": 99}, "away": {"type": "match", "match": 100}},
    },
    "Final": {
        104: {"home": {"type": "match", "match": 101}, "away": {"type": "match", "match": 102}},
    },
}
