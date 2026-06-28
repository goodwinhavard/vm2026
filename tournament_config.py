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
        73: {"home": "South Africa", "away": "Canada"},
        74: {"home": "Germany", "away": "Paraguay"},
        75: {"home": "Netherlands", "away": "Morocco"},
        76: {"home": "Brazil", "away": "Japan"},
        77: {"home": "France", "away": "Sweden"},
        78: {"home": "Ivory Coast", "away": "Norway"},
        79: {"home": "Mexico", "away": "Ecuador"},
        80: {"home": "England", "away": "DR Congo"},
        81: {"home": "United States", "away": "Bosnia and Herzegovina"},
        82: {"home": "Belgium", "away": "Senegal"},
        83: {"home": "Portugal", "away": "Croatia"},
        84: {"home": "Spain", "away": "Austria"},
        85: {"home": "Switzerland", "away": "Algeria"},
        86: {"home": "Argentina", "away": "Cape Verde"},
        87: {"home": "Colombia", "away": "Ghana"},
        88: {"home": "Australia", "away": "Egypt"},
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
