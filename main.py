import os
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, KeyCode, Controller as KeyboardController
from pynput import keyboard as mainKeyboard
import pyautogui
import enum
from time import sleep, time
import math
import Quartz
import cv2  # pip install opencv-python
import numpy  # this is still needed
import pyscreeze  # this is still needed
from datetime import datetime
import pytesseract


class State(enum.Enum):
    PAUSED = 1
    QUITTING = 2
    PLAYING = 10


class Tab(enum.Enum):
    ATTACK = 1
    DEFENSE = 2
    UTILITY = 3
    ULTIMATE_WEAPON = 4
    UNKNOWN = 5


class Direction(enum.Enum):
    UP = 1
    DOWN = 2


class MenuPosition(enum.Enum):
    TOP = 1
    BOTTOM = 2
    UNKNOWN = 3


mouse = MouseController()
keyboard = KeyboardController()
current_state = State.PAUSED
past_state = State.PLAYING
stop_picking_perks = False
current_wave = 0
GAME_SCREEN_REGION = (0, 0, 0, 0)  # left, top, width, height.   This is populated by verify_window()
TAB_SCREEN_REGION = (660, 971, 560, 60)
TOWER_CENTER_OFFSET = (296, 217)
GEM_DIST = 64  # offset (302, 153)
NUM_GEM_CHECK_PTS = 30
GEM_5_OFFSET = (111, 396)
WAVE_COUNTER_REGION = (360, 452, 56, 20)

# Tesseract setup (brew install tesseract)
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

# Game
MAX_PERK_OPTIONS = 4

# Menu
ATTACK_TAB_OFFSET = (43, 797)
DEFENSE_TAB_OFFSET = (187, 797)
UTILITY_TAB_OFFSET = (333, 797)
UW_TAB_OFFSET = (480, 797)
current_tab = Tab.UNKNOWN
TOP_MENU_SWIPE_OFFSET = (297, 560)
BOTTOM_MENU_SWIPE_OFFSET = (297, 758)
attack_tab_menu_position = MenuPosition.UNKNOWN
defense_tab_menu_position = MenuPosition.UNKNOWN
utility_tab_menu_position = MenuPosition.UNKNOWN

# Game Buttons
EXIT_BUTTON = "exit_button"
RETRY_BUTTON = "retry_button"
MORE_STATS_BUTTON = "more_stats_button"

# Upgrades
UPGRADE_1_OFFSET = (239, 562)
UPGRADE_2_OFFSET = (450, 562)
UPGRADE_4_OFFSET = (450, 667)

# Times
gem_5_last_check_time = 0
gem_2_last_check_time = 0
game_over_last_check_time = 0
perk_last_check_time = 0
wave_last_check_time = 0

# Intervals (seconds)
gem_5_int = 10
gem_2_int = 30
game_over_int = 30
perk_int = 20
wave_int = 60

# Assets
USING_EXTERNAL_MONITOR = Quartz.CGMainDisplayID() != 1
PROJECT_DIR = "/Users/jacobwilliams/dev/the-tower-bot/"
ASSETS_DIR = PROJECT_DIR + "assets/"
ASSETS_FILE_TYPE = ".png"
PERKS_DIR = "perks/"
STATS_DIR = "stats-history/"


# Perks
class Perk:
    priority: int
    img: str
    desc: str

    def __init__(self, priority, img, desc):
        self.img = img
        self.desc = desc
        self.priority = priority

    def __str__(self):
        return self.desc


PERK_POS_OFFSET = (110, 134, 105, 334)  # left, top, width, height
POINT_OFF_PERKS_SCREEN_OFFSET = (60, 200)
NEW_PERK_BUTTON = "new_perk_button"
CHOOSE_A_NEW_PERK = "choose_a_new_perk"
NEVER_PRIORITY = 1000
PERKS = [
    # We want PWR and econ perks first
    Perk(1, "perk_common_pwr", "perk wave requirement -x%"),
    Perk(2, "perk_tradeoff_coins_health", "x coins, but tower max health -70.0%"),
    Perk(3, "perk_uw_golden_tower", "golden tower bonus x1.5"),
    Perk(4, "perk_uw_black_hole", "black hole duration +12s"),
    Perk(5, "perk_common_coins", "x all coin bonuses"),
    Perk(6, "perk_common_game_speed", "increase max game speed by +x"),

    # Then we want perks that will drastically increase run length
    Perk(7, "perk_tradeoff_damage_damage", "enemies damage -50%, but tower damage -50%"),
    Perk(8, "perk_common_defence", "defense percent +x%"),
    Perk(9, "perk_common_health", "x max health"),
    Perk(10, "perk_common_free_upgrades", "free upgrade chance for all +x%"),

    # We want to get these out of the way to make it easier to get the coin tradeoff perk and avoid a perk dead-end
    Perk(11, "perk_tradeoff_damage_boss_health", "x tower damage, but bosses have x8 health"),
    Perk(11, "perk_tradeoff_health_speed", "boss health -70.0%, but boss speed +50%"),
    Perk(11, "perk_tradeoff_tower_regen_health", "tower health regen x8.00, but tower max health -60%"),

    # These are helpful perks
    Perk(12, "perk_uw_death_wave", "+1 wave on death wave"),
    Perk(13, "perk_common_cash", "x cash bonus"),
    Perk(14, "perk_common_orbs", "orbs +1"),

    # These we want to get out of the way because they are singles
    Perk(20, "perk_uw_chain_lightning", "chain lightning damage x2"),
    Perk(20, "perk_uw_smart_missiles", "4 more smart missiles"),
    Perk(20, "perk_uw_spotlight", "spotlight damage bonus x1.5"),
    Perk(20, "perk_uw_inner_land_mines", "extra set of inner mines"),
    Perk(20, "perk_uw_chrono_field", "chrono field duration +5s"),
    Perk(20, "perk_uw_poison_swamp", "swamp radius x1.5"),
    Perk(20, "perk_common_random_uw", "unlock a random ultimate weapon"),

    # This is good, but not needed until deep into the run
    Perk(30, "perk_common_health_regen", "x health regen"),

    # These are basically neutral
    Perk(99, "perk_common_damage", "x damage"),
    Perk(99, "perk_common_land_mine", "land mine damage x"),
    Perk(99, "perk_common_bounce_shot", "bounce shot +2"),
    Perk(100, "perk_common_defense_absolute", "x defense absolute"),
    Perk(100, "perk_common_interest", "interest x"),

    Perk(NEVER_PRIORITY, "perk_tradeoff_lifesteal_knockback", "lifesteal x2.50, but knockback force -70%"),
    Perk(NEVER_PRIORITY, "perk_tradeoff_ranged", "ranged enemies attack distance reduced, but ranged enemies damage x3"),
    Perk(NEVER_PRIORITY, "perk_tradeoff_speed_damage", "enemies speed -40%, but enemies damage x2.5"),
    Perk(NEVER_PRIORITY, "perk_tradeoff_cash_round", "x12.00 cash per wave, but enemy kill doesn't give cash"),
    Perk(NEVER_PRIORITY, "perk_tradeoff_enemy_health_tower_lifesteal", "enemies have -x% health, but tower health regen and lifesteal -90%"),
]


def on_press(key):
    # print(key)
    a = 1  # This is a no-op


def on_release(key):
    global current_state, past_state, current_tab, attack_tab_menu_position, defense_tab_menu_position, utility_tab_menu_position
    if key == Key.alt_r:  # This is the right option key
        if current_state == State.PAUSED:
            print("Un-pausing game!")
            change_state(past_state)
            current_tab = Tab.UNKNOWN
            verify_window()
            attack_tab_menu_position = MenuPosition.UNKNOWN
            defense_tab_menu_position = MenuPosition.UNKNOWN
            utility_tab_menu_position = MenuPosition.UNKNOWN

        else:
            print("Pausing game!")
            change_state(State.PAUSED)
    elif key == KeyCode.from_vk(
            179) or key == Key.ctrl_r:  # This is actually the right command button because I have switched the mapping
        print("Quitting!")
        change_state(State.QUITTING)


def change_state(new_state):
    global current_state, past_state
    past_state = current_state
    current_state = new_state


def click(pos, clicks=1, wait=0.25, wait_after_reposition=0.25, screen_offset=False):
    origin = GAME_SCREEN_REGION[:2]
    if screen_offset:  # if the offset is for the whole screen and not the game region (this happens when locating imgs)
        origin = 0, 0
    mouse.position = origin[0] + pos[0], origin[1] + pos[1]
    if wait_after_reposition > 0:
        sleep(wait_after_reposition)
    mouse.click(button=Button.left, count=clicks)
    sleep(wait)


def find_img(img_file_name, confidence=None, region=None, game_screen_offset=None, grayscale=False):
    img_path = ASSETS_DIR + img_file_name + ASSETS_FILE_TYPE
    needle_img = cv2.imread(img_path)
    pos_offset = 0, 0
    if region is None:
        region = GAME_SCREEN_REGION
        pos_offset = GAME_SCREEN_REGION[0], GAME_SCREEN_REGION[1]
    if game_screen_offset is not None:
        region = GAME_SCREEN_REGION[0] + game_screen_offset[0], GAME_SCREEN_REGION[1] + game_screen_offset[1], \
            game_screen_offset[2], game_screen_offset[3]
        pos_offset = GAME_SCREEN_REGION[0] + game_screen_offset[0], GAME_SCREEN_REGION[1] + game_screen_offset[1]
    haystack = pyautogui.screenshot(region=region)
    try:
        if confidence is None:
            pos = pyautogui.locate(needle_img, haystack, grayscale=grayscale)
        else:
            pos = pyautogui.locate(needle_img, haystack, confidence=confidence, grayscale=grayscale)
    except pyautogui.ImageNotFoundException:
        return None

    # img shape is h, w, d
    return pos[0] + pos_offset[0] + (needle_img.shape[1] / 2), pos[1] + pos_offset[1] + (needle_img.shape[0] / 2)


def find_img_in_img(haystack_img, needle_img_file_name, confidence=None, grayscale=False):
    needle_img = cv2.imread(needle_img_file_name)
    try:
        if confidence is not None:
            pos = pyautogui.locate(needle_img, haystack_img, grayscale=grayscale, confidence=confidence)
        else:
            pos = pyautogui.locate(needle_img, haystack_img, grayscale=grayscale)
        # img shape is h, w, d
        return pos[0] + (needle_img.shape[1] / 2), pos[1] + (needle_img.shape[0] / 2)
    except pyautogui.ImageNotFoundException:
        return None


def check_gem_5():
    global gem_5_last_check_time
    gem_5_last_check_time = time()
    click(GEM_5_OFFSET, wait_after_reposition=0.0)


def check_gem_2():
    global gem_2_last_check_time
    gem_2_last_check_time = time()
    for i in range(NUM_GEM_CHECK_PTS):
        if current_state == State.PLAYING:
            angle = 360 - (360 / NUM_GEM_CHECK_PTS) * i
            pos_x = TOWER_CENTER_OFFSET[0] + (GEM_DIST * math.cos(math.radians(angle)))
            pos_y = TOWER_CENTER_OFFSET[1] + (GEM_DIST * math.sin(math.radians(angle)))
            click((pos_x, pos_y), wait=.1, wait_after_reposition=0.0)


def check_game_over():
    global current_state, game_over_last_check_time, current_tab, stop_picking_perks
    game_over_last_check_time = time()
    retry_pos = find_img(RETRY_BUTTON, confidence=0.8, grayscale=True)
    if retry_pos is not None:
        stats_pos = find_img(MORE_STATS_BUTTON, confidence=0.8, grayscale=True)
        if stats_pos is not None:
            click(stats_pos, screen_offset=True)
            filename = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ASSETS_FILE_TYPE
            pyautogui.screenshot(filename, region=GAME_SCREEN_REGION).save(PROJECT_DIR + STATS_DIR + filename)
            sleep(.5)
            exit_pos = find_img(EXIT_BUTTON, confidence=0.8)
            if exit_pos is not None:
                click(exit_pos, screen_offset=True)
            else:
                click(UW_TAB_OFFSET)
            sleep(.5)
        click(retry_pos, screen_offset=True)
        change_state(State.PLAYING)
        current_tab = Tab.UNKNOWN
        stop_picking_perks = False


def swipe_menu(direction=Direction.UP, times=3):
    sleep(0.5)
    for i in range(times):
        if current_state is State.PLAYING:
            if direction is Direction.UP:
                mouse.position = GAME_SCREEN_REGION[0] + BOTTOM_MENU_SWIPE_OFFSET[0], GAME_SCREEN_REGION[1] + \
                                 BOTTOM_MENU_SWIPE_OFFSET[1]
                swipe_direction = -200
            else:
                mouse.position = GAME_SCREEN_REGION[0] + TOP_MENU_SWIPE_OFFSET[0], GAME_SCREEN_REGION[1] + \
                                 TOP_MENU_SWIPE_OFFSET[1]
                swipe_direction = 200
            pyautogui.drag(0, swipe_direction, 0.2, button='left')
    sleep(0.5)


def set_tab(tab):
    global current_tab
    if current_tab is not tab:
        if current_tab is Tab.UNKNOWN and current_state is State.PLAYING:
            click(UW_TAB_OFFSET)

        if tab is Tab.ATTACK and current_state is State.PLAYING:
            click(ATTACK_TAB_OFFSET)
            current_tab = Tab.ATTACK
        elif tab is Tab.DEFENSE and current_state is State.PLAYING:
            click(DEFENSE_TAB_OFFSET)
            current_tab = Tab.DEFENSE
        elif tab is Tab.UTILITY and current_state is State.PLAYING:
            click(UTILITY_TAB_OFFSET)
            current_tab = Tab.UTILITY


def set_menu_position(menu_position):
    global attack_tab_menu_position, defense_tab_menu_position, utility_tab_menu_position, current_tab
    if current_tab is Tab.UNKNOWN and current_state is State.PLAYING:
        set_tab(Tab.DEFENSE)

    if current_tab is Tab.ATTACK:
        if attack_tab_menu_position is MenuPosition.UNKNOWN:
            if menu_position is MenuPosition.TOP:
                swipe_menu(direction=Direction.DOWN)
                attack_tab_menu_position = MenuPosition.TOP
            else:
                swipe_menu(direction=Direction.UP)
                attack_tab_menu_position = MenuPosition.BOTTOM
        elif menu_position is MenuPosition.TOP and attack_tab_menu_position is MenuPosition.BOTTOM:
            swipe_menu(direction=Direction.DOWN)
            attack_tab_menu_position = MenuPosition.TOP
        elif menu_position is MenuPosition.BOTTOM and attack_tab_menu_position is MenuPosition.TOP:
            swipe_menu(direction=Direction.UP)
            attack_tab_menu_position = MenuPosition.BOTTOM
    elif current_tab is Tab.DEFENSE:
        if defense_tab_menu_position is MenuPosition.UNKNOWN:
            if menu_position is MenuPosition.TOP:
                swipe_menu(direction=Direction.DOWN)
                defense_tab_menu_position = MenuPosition.TOP
            else:
                swipe_menu(direction=Direction.UP)
                defense_tab_menu_position = MenuPosition.BOTTOM
        elif menu_position is MenuPosition.TOP and defense_tab_menu_position is MenuPosition.BOTTOM:
            swipe_menu(direction=Direction.DOWN)
            defense_tab_menu_position = MenuPosition.TOP
        elif menu_position is MenuPosition.BOTTOM and defense_tab_menu_position is MenuPosition.TOP:
            swipe_menu(direction=Direction.UP)
            defense_tab_menu_position = MenuPosition.BOTTOM
    elif current_tab is Tab.UTILITY:
        if utility_tab_menu_position is MenuPosition.UNKNOWN:
            if menu_position is MenuPosition.TOP:
                swipe_menu(direction=Direction.DOWN, times=2)
                utility_tab_menu_position = MenuPosition.TOP
            else:
                swipe_menu(direction=Direction.UP, times=2)
                utility_tab_menu_position = MenuPosition.BOTTOM
        elif menu_position is MenuPosition.TOP and utility_tab_menu_position is MenuPosition.BOTTOM:
            swipe_menu(direction=Direction.DOWN, times=2)
            utility_tab_menu_position = MenuPosition.TOP
        elif menu_position is MenuPosition.BOTTOM and utility_tab_menu_position is MenuPosition.TOP:
            swipe_menu(direction=Direction.UP, times=2)
            utility_tab_menu_position = MenuPosition.BOTTOM


def check_perk():
    global stop_picking_perks, perk_last_check_time
    perk_last_check_time = time()
    new_perk_pos = find_img(NEW_PERK_BUTTON, confidence=0.7, grayscale=True)
    if new_perk_pos is not None:
        sleep(1)
        click(new_perk_pos, screen_offset=True)
        # print("Perk Choices:")
        more_perks_to_select = True
        while more_perks_to_select:
            perk_to_select = None  # (perk, pos)
            perks_identified = 0
            perk_region = GAME_SCREEN_REGION[0] + PERK_POS_OFFSET[0], GAME_SCREEN_REGION[1] + PERK_POS_OFFSET[1], \
                PERK_POS_OFFSET[2], PERK_POS_OFFSET[3]
            haystack_img = pyautogui.screenshot(region=perk_region)
            for perk in PERKS:
                if current_state == State.PLAYING:
                    perk_img_file = ASSETS_DIR + PERKS_DIR + perk.img + ASSETS_FILE_TYPE
                    perk_pos = find_img_in_img(haystack_img, perk_img_file, confidence=0.9, grayscale=True)
                    if perk_pos is not None:
                        perks_identified += 1
                        # print(f"\t{perk.desc}")
                        if perks_identified >= MAX_PERK_OPTIONS:
                            break
                    if perk_pos is not None and (perk_to_select is None or perk.priority < perk_to_select[0].priority) and not (perk.img == "perk_tradeoff_coins_health" and current_wave > 4000):
                        perk_to_select = (perk, perk_pos)
                else:
                    return
            if perks_identified is not MAX_PERK_OPTIONS:
                print("Missing Perk")
                haystack_img.save(PROJECT_DIR + "missingPerk.png")
            if perk_to_select is None or perk_to_select[0].priority == NEVER_PRIORITY:
                stop_picking_perks = True
                more_perks_to_select = False
                print("Stopping perk selection\n\n")
            else:
                print(f"Chose: {perk_to_select[0].desc}")
                perk_offset = PERK_POS_OFFSET[0] + perk_to_select[1][0], PERK_POS_OFFSET[1] + perk_to_select[1][1]
                mouse.position = GAME_SCREEN_REGION[0] + perk_offset[0], GAME_SCREEN_REGION[1] + perk_offset[1]
                click(perk_offset)
                choose_a_perk_pos = find_img(CHOOSE_A_NEW_PERK, confidence=0.7)
                if choose_a_perk_pos is None:
                    more_perks_to_select = False
        exit_pos = find_img(EXIT_BUTTON, confidence=0.8)
        if exit_pos is not None:
            click(exit_pos, screen_offset=True, wait=0.5)
        else:
            # failsafe for if the exit button can't be found
            click(POINT_OFF_PERKS_SCREEN_OFFSET, clicks=2)


def find_window(name):
    windows = Quartz.CGWindowListCopyWindowInfo(
        Quartz.kCGWindowListExcludeDesktopElements | Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID)
    for window in windows:
        if window.get(Quartz.kCGWindowOwnerName) == name:
            bounds = window.get(Quartz.kCGWindowBounds)
            return int(bounds["X"]), int(bounds["Y"]), int(bounds["Width"]), int(bounds["Height"])

    print(f"Could not find window '{name}'!")
    exit()


def verify_window(name="The Tower", required_dims=(591, 816)):
    global GAME_SCREEN_REGION
    GAME_SCREEN_REGION = find_window(name)
    dims = GAME_SCREEN_REGION[2:]
    if dims != required_dims:
        print("Window is not correctly sized!")
        print(f"Current dimensions: {dims}")
        print(f"Expected dimensions: {required_dims}")
        exit()


def read_wave_counter():
    global current_wave, wave_last_check_time
    try:
        wave_last_check_time = time()
        wave_counter_offset = GAME_SCREEN_REGION[0] + WAVE_COUNTER_REGION[0], GAME_SCREEN_REGION[1] + WAVE_COUNTER_REGION[1]
        wave_counter_region = wave_counter_offset[0], wave_counter_offset[1], WAVE_COUNTER_REGION[2], WAVE_COUNTER_REGION[3]
        wave_img = pyautogui.screenshot(region=wave_counter_region)
        wave = pytesseract.image_to_string(wave_img, config="--psm 7")
        current_wave = int(wave.strip())
    except Exception:
        pass


def play_round():
    if current_wave < 450:  # upgrade EALS until it gets too expensive
        set_tab(Tab.UTILITY)
        set_menu_position(MenuPosition.BOTTOM)
        if current_state is State.PLAYING:
            click(UPGRADE_4_OFFSET)
    elif current_wave < 500:  # upgrade Recovery Amount so free upgrades can be focused on EALS as soon as possible
        set_tab(Tab.UTILITY)
        set_menu_position(MenuPosition.BOTTOM)
        if current_state is State.PLAYING:
            click(UPGRADE_1_OFFSET)
    elif current_wave < 750:  # upgrade Max Recovery so free upgrades can be focused on EALS as soon as possible
        set_tab(Tab.UTILITY)
        set_menu_position(MenuPosition.BOTTOM)
        if current_state is State.PLAYING:
            click(UPGRADE_2_OFFSET)
    elif current_wave < 900:  # upgrade health until max
        set_tab(Tab.DEFENSE)
        set_menu_position(MenuPosition.TOP)
        if current_state is State.PLAYING:
            click(UPGRADE_1_OFFSET)
    else:  # upgrade health regen
        set_tab(Tab.DEFENSE)
        set_menu_position(MenuPosition.TOP)
        if current_state is State.PLAYING:
            click(UPGRADE_2_OFFSET)


def play():
    global current_state, current_tab
    listener = mainKeyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()
    verify_window()
    read_wave_counter()
    print("Pausing game!")

    while current_state is not State.QUITTING:
        if current_state is not State.PAUSED:
            # print('Mouse: {0}, Offset: {1}'.format(mouse.position, (mouse.position[0] - GAME_SCREEN_REGION[0], mouse.position[1] - GAME_SCREEN_REGION[1])))
            # sleep(1)

            t = time()
            if t - game_over_last_check_time > game_over_int and current_state == State.PLAYING:
                check_game_over()
            if t - wave_last_check_time > wave_int and current_state == State.PLAYING:
                read_wave_counter()
            if t - gem_2_last_check_time > gem_2_int and current_state == State.PLAYING:
                check_gem_2()
            if t - gem_5_last_check_time > gem_5_int and current_state == State.PLAYING:
                check_gem_5()
            if t - perk_last_check_time > perk_int and not stop_picking_perks and current_state == State.PLAYING:
                check_perk()
            if current_state is State.PLAYING:
                play_round()


play()
