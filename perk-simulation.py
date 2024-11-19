from random import random, randint

PERK_WAVES_REQUIRED_LAB = 5
PERK_STANDARD_BONUS_LAB = 7
PERK_OPTIONS = 3
PERK_BANS = 2
IMPROVE_TRADEOFF_PERKS_LAB = 0
COMMON_PERKS = {
    "x1.20 Max Health":	5,
    "x1.15 Damage":	5,
    "x1.15 All Coin Bonuses": 5,
    "x1.15 Defense Absolute": 5,
    "x1.15 Cash Bonus": 5,
    "x1.75 Health Regen": 5,
    "Interest x1.50": 5,
    "Land Mine Damage x3.50": 5,
    "Free Upgrade Chance for All +5.0%": 5,
    "Defense Percent +4.00": 5,
    "Bounce Shot +2": 3,
    "Perk Wave Requirement -20.00%": 3,
    "Orbs +1": 2,
    "Unlock a Random Ultimate Weapon": 1,
    "Increase Max Game Speed by +1.00": 1,
}
TRADEOFF_PERKS = {
    "x1.50 Tower Damage, but Bosses Have 8x Health":	1,
    "x1.80 coins, but Tower Max Health -70%":	1,
    "Enemies Have -50% Health, but Tower Health Regen and Lifesteal -90%": 1,
    "Enemies Damage -50%, but Tower Damage -50%":	1,
    "Ranged Enemies Attack Distance Reduced, But Tower Ranged Enemies Damage x3": 1,
    "Enemies Speed -40%, But Enemies Damage x2.5":	1,
    "x12.00 Cash Per Wave, But Enemy Kill Don't Give Cash":	1,
    "Tower Health Regen x8.00, But Tower Max Max Health -60%":	1,
    "Boss Health -70%, But Boss Speed +50%":	1,
    "Lifesteal x2.50, But Knockback force -70%":	1,
}
UW_PERKS = {
    # "4 More Smart Missiles":	1,
    # "Swamp Radius x1.5":	1,
    "+1 Wave on Death Wave":	1,
    # "Extra Set of Inner Mines":	1,
    "Golden Tower Bonus x1.5":	1,
    # "Chain Lightning Damage x2":	1,
    "Chrono Field Duration +5s":	1,
    "Blackhole Duration +12.0s":	1,
    # "Spotlight Damage Bonus x1.5":	1,
}
NEVER_PRIORITY = 1000
PERK_PRIORITY = {
    "Perk Wave Requirement -20.00%": 1,
    "x1.80 coins, but Tower Max Health -70%": 2,
    "Golden Tower Bonus x1.5": 3,
    "x1.15 All Coin Bonuses": 4,
    "Increase Max Game Speed by +1.00": 5,
    "Enemies Damage -50%, but Tower Damage -50%": 6,
    "Defense Percent +4.00": 7,
    "x1.20 Max Health": 8,
    "Free Upgrade Chance for All +5.0%": 9,
    "x1.15 Cash Bonus": 10,
    "x1.15 Damage": 11,
    "Blackhole Duration +12.0s": 12,
    "Orbs +1": 13,
    "+1 Wave on Death Wave": 14,
    "Chain Lightning Damage x2": 15,
    "Unlock a Random Ultimate Weapon": 16,
    "Bounce Shot +2": 17,
    "x1.50 Tower Damage, but Bosses Have 8x Health": 18,
    "Spotlight Damage Bonus x1.5": 20,
    "4 More Smart Missiles": 20,
    "Swamp Radius x1.5": 20,
    "Extra Set of Inner Mines": 20,
    "Chrono Field Duration +5s": 20,
    "x1.15 Defense Absolute": 100,
    "Interest x1.50": 100,
    "Land Mine Damage x3.50": 100,
    "Boss Health -70%, But Boss Speed +50%": 100,
    "x1.75 Health Regen": 100,
    "Lifesteal x2.50, But Knockback force -70%": NEVER_PRIORITY,
    "Ranged Enemies Attack Distance Reduced, But Tower Ranged Enemies Damage x3": NEVER_PRIORITY,
    "Enemies Speed -40%, But Enemies Damage x2.5": NEVER_PRIORITY,
    "x12.00 Cash Per Wave, But Enemy Kill Don't Give Cash": NEVER_PRIORITY,
    "Tower Health Regen x8.00, But Tower Max Max Health -60%": NEVER_PRIORITY,
    "Enemies Have -50% Health, but Tower Health Regen and Lifesteal -90%": NEVER_PRIORITY,
}
ITERATIONS = 100
MAX_WAVE = 5000
FIRST_PERK_CHOICE = "Perk Wave Requirement -20.00%"
BANNED_PERKS = [
    "x12.00 Cash Per Wave, But Enemy Kill Don't Give Cash",
    "Enemies Have -50% Health, but Tower Health Regen and Lifesteal -90%"
]


def waves_till_next_perk(perk_wave_reduction, num_perks_selected):
    if num_perks_selected < 20:
        waves_till_next = 200
    elif num_perks_selected < 30:
        waves_till_next = 250
    elif num_perks_selected < 40:
        waves_till_next = 300
    else:
        waves_till_next = 350
    return (waves_till_next - PERK_WAVES_REQUIRED_LAB) * perk_wave_reduction


# the purpose of this simulation is to see what combination of first choice, ban and priority of perks
# will allow us to get all econ perks at the lowest average wave.
first_perk = True
for _ in range(ITERATIONS):
    perk_wave_reduction = 0
    waves = 0
    num_perks_chosen = 0
    common_perk_options = COMMON_PERKS.copy()
    uw_perk_options = UW_PERKS.copy()
    tradeoff_perk_options = TRADEOFF_PERKS.copy()
    perks_chosen = {}
    while waves < MAX_WAVE:
        waves += waves_till_next_perk(perk_wave_reduction, num_perks_chosen)
        perk_options = []
        common_perk_override = False
        for _ in range(PERK_OPTIONS):
            r = random()
            if r < 0.15:  # tradeoff
                r_tradeoff = randint(0, len(tradeoff_perk_options) - 1)
                perk_options.append(tradeoff_perk_options.k)
            if 0.15 <= r < 0.35:  # uw
                uw
            if 0.35 <= r or common_perk_override:  # common
                common
        if first_perk:
            perk_options = FIRST_PERK_CHOICE

