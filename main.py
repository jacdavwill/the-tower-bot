from pynput.mouse import Button, Controller
from pynput import keyboard
import pyautogui
import enum
from time import sleep, time
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


mouse = Controller()
current_state = State.STARTING
past_state = State.STARTING
summary = {
    "gem_5_rewards_claimed": 0,
    "gem_2_rewards_claimed": 0,
    "start_time": time(),
    "rounds": 0
}
GAME_SCREEN_REGION = (660, 41, 560, 988)  # left, top, width, height
TAB_SCREEN_REGION = (660, 971, 560, 60)

# Times
gem_5_start_time = 0
gem_2_start_time = 0
round_time = time()

# Intervals (seconds)
gem_5_int = 10 * 60  # 10 minutes
gem_2_int = 15 * 60  # 15 minutes
restart_int = 10

# Assets
ASSETS_PREFIX = "./assets/"
ASSETS_FILE_TYPE = ".png"

GEM_5_BUTTON = "gem_5_button"
GEM_5_CLAIM_BUTTON = "gem_5_claim_button"
CLAIM_REWARD_BUTTON = "claim_reward_button"
GEM_2_BUTTONS = [f"gem_2_button_{x}" for x in range(4)]
RETRY_BUTTON = "retry_button"
UTILITY_TAB_DISACTIVATED = "utility_tab_disactivated"
UTILITY_TAB_ACTIVATED = "utility_tab_activated"
# BLUESTACKS_BACK_BUTTON = "bluestacks_back_button"
# BLUESTACKS_HOME_BUTTON = "bluestacks_home_button"
THE_TOWER_IMGS = ["the_tower_img", "the_tower_img_larger"]

# Colors
AFFORDABLE_UPGRADE = (17, 58, 93)


def on_press(key):
    a = 1  # This is a no-op


def on_release(key):
    global current_state, past_state
    if key == keyboard.Key.ctrl_r:
        if current_state == State.PAUSED:
            print("Un-pausing game!")
            change_state(past_state)
        else:
            print("Pausing game!")
            change_state(State.PAUSED)
    elif key == keyboard.Key.alt_gr:
        print("Quitting!")
        change_state(State.QUITTING)
    elif key == keyboard.Key.shift_r or key == keyboard.Key.shift_l:
        total_time = time() - summary["start_time"]
        print("\nPrinting run summary")
        print("----------------------------------------------------------------------------")
        print(summary)
        print("Total run time: ", total_time, " seconds")
        total_gems = 5 * summary["gem_5_rewards_claimed"] + 2 * summary["gem_2_rewards_claimed"]
        print("Total gems collected: ", total_gems)
        print("Gems/hr: ", total_gems / (total_time / 3600))
        print("----------------------------------------------------------------------------")


def change_state(new_state):
    global current_state, past_state
    past_state = current_state
    current_state = new_state


def click(pos, clicks=1):
    mouse.position = pos
    mouse.click(button=Button.left, count=clicks)
    sleep(.25)


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
    global gem_5_start_time
    pos = find_img(GEM_5_BUTTON)
    if pos is not None:
        click(pos)
        print("found 5 gem: ", (time() - gem_5_start_time) / 60, " minutes")
        summary["gem_5_rewards_claimed"] += 1
        gem_5_start_time = time()



def check_gem_2():
    global gem_2_start_time
    for img in GEM_2_BUTTONS:
        pos = find_img(img, 0.7)
        if pos is not None:
            click(pos)
            print("found 2 gem: ", (time() - gem_2_start_time) / 60, " minutes")
            summary["gem_2_rewards_claimed"] += 1
            gem_2_start_time = time()


def check_game_over():
    global current_state, round_time, summary
    pos = find_img(RETRY_BUTTON)
    if pos is not None:
        round_time = time()
        summary["rounds"] += 1
        click(pos)
        change_state(State.STARTING)


def get_current_tab():
    pos = find_img(UTILITY_TAB_ACTIVATED, region=TAB_SCREEN_REGION)
    if pos is not None:
        return Tab.UTILITY
    else:
        return Tab.UNKNOWN


def play_round():
    global current_state
    if current_state == State.STARTING:
        current_tab = get_current_tab()
    else:
        current_tab = Tab.UTILITY

    if current_tab is Tab.UTILITY:
        if True:
            click((1173, 868), clicks=5)  # coins/wave
        else:
            click((823, 868))  # coin/kill bonus
    else:
        pos = find_img(UTILITY_TAB_DISACTIVATED, region=TAB_SCREEN_REGION)
        if pos is not None:
            click(pos)
            sleep(1)


# def reset_game():
#     global current_state, summary
#     print("resetting game")
#     pos = find_img(BLUESTACKS_HOME_BUTTON, full_screen=True)
#     if pos is not None:
#         click(pos)
#         sleep(5)
#         for img in THE_TOWER_IMGS:
#             pos_tower = find_img(img, full_screen=True)
#             if pos_tower is not None:
#                 click(pos_tower)
#                 summary["restarts"] += 1
#                 sleep(5)


def play():
    global current_state
    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()

    while current_state is not State.QUITTING:
        # sleep(1)
        # print('Mouse: {0}, Color: {1}'.format(mouse.position, pyautogui.pixel(*mouse.position)))
        if current_state is not State.PAUSED:
            t = time()
            if t - round_time > restart_int:
                check_game_over()
            if t - gem_2_start_time > gem_2_int:
                check_gem_2()
            if t - gem_5_start_time > gem_5_int:
                check_gem_5()
            play_round()


play()

# 7.95, 8.56, 7.78 = 8.1 c/w
#
