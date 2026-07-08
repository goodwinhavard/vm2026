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
        89: {"home": "Paraguay", "away": "France"},
        90: {"home": "Canada", "away": "Morocco"},
        91: {"home": "Brazil", "away": "Norway"},
        92: {"home": "Mexico", "away": "England"},
        93: {"home": "Portugal", "away": "Spain"},
        94: {"home": "United States", "away": "Belgium"},
        95: {"home": "Argentina", "away": "Egypt"},
        96: {"home": "Switzerland", "away": "Colombia"},
    },
    "Quarterfinals": {
        97: {"home": "France", "away": "Morocco"},
        98: {"home": "Spain", "away": "Belgium"},
        99: {"home": "Norway", "away": "England"},
        100: {"home": "Argentina", "away": "Switzerland"},
    },
    "Semifinals": {
        101: {"home": {"type": "match", "match": 97}, "away": {"type": "match", "match": 98}},
        102: {"home": {"type": "match", "match": 99}, "away": {"type": "match", "match": 100}},
    },
    "Final": {
        104: {"home": {"type": "match", "match": 101}, "away": {"type": "match", "match": 102}},
    },
}
