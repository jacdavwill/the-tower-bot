from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
from pynput import keyboard as mainKeyboard
import pyautogui
import enum
from time import sleep, time
import math
import datetime
from random import random


class State(enum.Enum):
    PAUSED = 1
    QUITTING = 2
    STARTING = 10
    BATTLING = 11


class Tab(enum.Enum):
    ATTACK = 1
    DEFENSE = 2
    UTILITY = 3
    ULTIMATE_WEAPON = 4
    UNKNOWN = 5


mouse = MouseController()
keyboard = KeyboardController()
current_state = State.STARTING
past_state = State.STARTING
stop_picking_perks = False
summary = {
    "gem_5_rewards_claimed": 0,
    "gem_2_rewards_claimed": 0,
    "start_time": time(),
    "rounds": 0
}
GAME_SCREEN_REGION = (660, 41, 560, 988)  # left, top, width, height
TAB_SCREEN_REGION = (660, 971, 560, 60)
TOWER_CENTER = (939, 320)
GEM_DIST = 73  # (974, 394)
NUM_GEM_CHECK_PTS = 30
GEM_5_POS = (713, 503)

# Tabs
ATTACK_TAB_POS = (732, 1000)
DEFENSE_TAB_POS = (869, 1000)
UTILITY_TAB_POS = (1008, 1000)
UW_TAB_POS = (1150, 1000)
current_tab = Tab.UNKNOWN

# Upgrades
UPGRADE_1_POS = (815, 759)
UPGRADE_2_POS = (1184, 759)
UPGRADE_3_POS = (815, 869)
UPGRADE_4_POS = (1184, 869)
UPGRADE_5_POS = (815, 969)
UPGRADE_6_POS = (1184, 969)

# Times
gem_5_start_time = 0
gem_2_start_time = 0
round_time = time()

# Intervals (seconds)
gem_5_int = 10 * 60  # 10 minutes
gem_2_int = 15 * 60  # 15 minutes
restart_int = 3
force_restart_int = 100
gem_2_check_after = 10

# Assets
ASSETS_PREFIX = "./assets/"
ASSETS_FILE_TYPE = ".png"

GEM_5_BUTTON = "gem_5_button"
GEM_5_CLAIM_BUTTON = "gem_5_claim_button"
CLAIM_REWARD_BUTTON = "claim_reward_button"
GEM_2_BUTTONS = [f"gem_2_button_{x}" for x in range(4)]
RETRY_BUTTON = "retry_button"
END_ROUND_BUTTON = "end_round_button"
NOT_RESPONDING_WAIT = "not_responding_wait"

# Colors
AFFORDABLE_UPGRADE = (17, 58, 93)


# Perks
class Perk:
    priority: int
    img: str
    desc: str

    def __init__(self, priority, img, desc):
        self.img = img
        self.desc = desc
        self.priority = priority


PERK_POS = (712, 170, 122, 219)  # left, top, width, height
NEW_PERK_BUTTON = "new_perk_button"
CHOOSE_ANOTHER_PERK = "choose_another_perk"
PERK_EXIT_BUTTON = "perk_exit_button"
PERKS = [
    Perk(7, "perk_common_1", "x max health"),
    Perk(12, "perk_common_2", "x damage"),
    Perk(12, "perk_common_3", "x health regen"),
    Perk(4, "perk_common_4", "x all coin bonuses"),
    Perk(12, "perk_common_5", "bounce shot +2"),
    Perk(12, "perk_common_6", "interest x"),
    Perk(12, "perk_common_7", "land mine damage xx"),
    Perk(7, "perk_common_8", "orbs +1"),
    Perk(11, "perk_common_9", "free upgrade chance for all +x%"),
    Perk(8, "perk_common_10", "defense percent +x%"),
    Perk(5, "perk_common_11", "perk wave requirement -x%"),
    Perk(13, "perk_common_12", "unlock a random ultimate weapon"),
    Perk(3, "perk_common_13", "increase max game speed by +x"),
    # Perk(12, "perk_uw_1", "4 more smart missiles"),
    # Perk(12, "perk_uw_2", "swamp radius x1.5"),
    # Perk(12, "perk_uw_3", "+1 wave on death wave"),
    Perk(2, "perk_uw_4", "golden tower bonus x1.5"),
    # Perk(12, "perk_uw_5", "chain lightning damage x2"),
    Perk(8, "perk_uw_6", "chrono field radius x1.5"),
    # Perk(12, "perk_uw_7", "extra set of inner mines"),
    Perk(13, "perk_tradeoff_1", "x tower damage, but bosses have x8 health"),
    Perk(1, "perk_tradeoff_2", "x coins, but tower max health -70.0%"),
    Perk(10, "perk_tradeoff_3", "enemies have -x% health, but tower health regen and lifesteal -90%"),
    Perk(6, "perk_tradeoff_4", "enemies damage -50%, but tower damage -50%"),
    # Perk(9, "perk_tradeoff_5", "ranged enemies attach distance reduced, but ranged enemies damage x3"),
    # Perk(100, "perk_tradeoff_6", "enemies speed -40%, but enemies damage x2.5"),
    # Perk(100, "perk_tradeoff_7", "x12.00 cash per wave, but enemy kill doesn't give cash"),
    # Perk(100, "perk_tradeoff_8", "tower health regen x8.00, but tower max health -60%"),
    Perk(12, "perk_tradeoff_9", "boss health -70.0%, but boss speed +50%"),
    # Perk(100, "perk_tradeoff_10", "lifesteal x2.50, but knockback force -70%"),
]


def on_press(key):
    a = 1  # This is a no-op


def on_release(key):
    global current_state, past_state, current_tab
    if key == Key.ctrl_r:
        if current_state == State.PAUSED:
            print("Un-pausing game!")
            change_state(past_state)
            current_tab = Tab.UNKNOWN
        else:
            print("Pausing game!")
            change_state(State.PAUSED)
    elif key == Key.alt_gr:
        print("Quitting!")
        change_state(State.QUITTING)
    elif key == Key.shift_r or key == Key.shift_l:
        total_time = time() - summary["start_time"]
        print("\nPrinting run summary")
        print("----------------------------------------------------------------------------")
        print(summary)
        print("Total run time: ", total_time, " seconds")
        print("----------------------------------------------------------------------------")


def change_state(new_state):
    global current_state, past_state
    past_state = current_state
    current_state = new_state


def click(pos, clicks=1, wait=0.25):
    mouse.position = pos
    mouse.click(button=Button.left, count=clicks)
    sleep(wait)


def find_img(img_file_name, confidence=None, full_screen=False, region=GAME_SCREEN_REGION):
    img_path = ASSETS_PREFIX + img_file_name + ASSETS_FILE_TYPE
    if confidence is None:
        if full_screen:
            return pyautogui.locateCenterOnScreen(img_path)
        else:
            return pyautogui.locateCenterOnScreen(img_path, region=region)
    else:
        return pyautogui.locateCenterOnScreen(img_path, confidence=confidence, region=region)


def check_gem_5():
    click(GEM_5_POS)


def check_gem_2():
    for i in range(NUM_GEM_CHECK_PTS):
        angle = (360 / NUM_GEM_CHECK_PTS) * i
        pos_x = TOWER_CENTER[0] + (GEM_DIST * math.cos(math.radians(angle)))
        pos_y = TOWER_CENTER[1] + (GEM_DIST * math.sin(math.radians(angle)))
        click((pos_x, pos_y), wait=0)


def check_game_over(with_restart=True):
    global current_state, round_time, summary, current_tab, stop_picking_perks
    pos = find_img(RETRY_BUTTON)
    if pos is not None:
        sleep(1)
        round_time = time()

        stats_pos = find_img()

        click(pos)

        # doing short reset because uncleared enemies can cause loss of Second Wind
        if with_restart:
            sleep(2)
            restart_round()
            check_game_over(with_restart=False)

        summary["rounds"] += 1
        change_state(State.STARTING)
        current_tab = Tab.UNKNOWN
        stop_picking_perks = False

    pos = find_img(NOT_RESPONDING_WAIT)
    if pos is not None:
        sleep(3)
        click(pos)
        sleep(3)


def set_tab(tab):
    global current_tab
    if current_tab is not tab:
        if current_tab is Tab.UNKNOWN:
            click(UW_TAB_POS)

        if tab is Tab.ATTACK:
            click(ATTACK_TAB_POS)
            current_tab = Tab.ATTACK
        elif tab is Tab.DEFENSE:
            click(DEFENSE_TAB_POS)
            current_tab = Tab.DEFENSE
        elif tab is Tab.UTILITY:
            click(UTILITY_TAB_POS)
            current_tab = Tab.UTILITY


def play_round():
    global current_state

    set_tab(Tab.DEFENSE)
    sleep(.25)
    click(UPGRADE_1_POS)


def restart_round():
    global keyboard
    keyboard.tap(Key.esc)

    end_round_pos = find_img(END_ROUND_BUTTON)
    if end_round_pos:
        click(end_round_pos)
    sleep(1)


def check_perk():
    global stop_picking_perks
    pos = find_img(NEW_PERK_BUTTON)
    if pos is not None:
        click(pos)
        sleep(1)
        more_perks_to_select = True
        while more_perks_to_select:
            perk_to_select = None
            for perk in PERKS:
                pos = find_img(perk.img, confidence=.7, region=PERK_POS)
                if pos is not None:
                    print()
                if pos is not None and (perk_to_select is None or perk.priority < perk_to_select[0].priority):
                    perk_to_select = (perk, pos)

            if perk_to_select is None or perk_to_select[0].priority == 100:
                stop_picking_perks = True
                more_perks_to_select = False
            else:
                click(perk_to_select[1])
                sleep(.5)
                pos = find_img(CHOOSE_ANOTHER_PERK)
                if pos is None:
                    more_perks_to_select = False
        pos = find_img(PERK_EXIT_BUTTON)
        if pos is not None:
            click(pos)
            sleep(.5)


def play():
    global current_state
    listener = mainKeyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()

    sleep(3)
    while current_state is not State.QUITTING:
        if current_state is not State.PAUSED:
            # print('Mouse: {0}, Color: {1}'.format(mouse.position, pyautogui.pixel(*mouse.position)))
            # sleep(1)

            t = time()
            if t - round_time > restart_int:
                check_game_over()
            if t - round_time > gem_2_check_after:
                check_gem_2()
            if t - gem_5_start_time > gem_5_int:
                check_gem_5()
            if not stop_picking_perks:
                check_perk()
            play_round()


play()
