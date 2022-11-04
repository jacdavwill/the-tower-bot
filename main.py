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

    BATTLING = 10
    VIEWING_AD = 11


class Tab(enum.Enum):
    ATTACK = 1
    DEFENSE = 2
    UTILITY = 3
    ULTIMATE_WEAPON = 4
    UNKNOWN = 5


mouse = Controller()
current_state = State.BATTLING
past_state = State.BATTLING
summary = {
    "gem_5_rewards_claimed": 0,
    "gem_2_rewards_claimed": 0,
    "start_time": time(),
    "start_coins": "187.20K",
    "start_gems": 1008,
    "restarts": 0
}
GAME_SCREEN_REGION = (661, 41, 559, 988)  # left, top, width, height

# Times
ad_start_time = time()
gem_5_start_time = 0
gem_2_start_time = 0
round_time = time()

# Intervals (seconds)
ad_int = 35
ad_max_timeout_int = 60
gem_5_int = 10 * 60  # 10 minutes
gem_2_int = 15 * 60  # 15 minutes
sprint_t6_int = 37
restart_int = 20

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
BLUESTACKS_BACK_BUTTON = "bluestacks_back_button"
BLUESTACKS_HOME_BUTTON = "bluestacks_home_button"
ROUND_REWARD_BUTTON = "round_reward_button"
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
    print("State: ", new_state)
    past_state = current_state
    current_state = new_state


def click(pos):
    mouse.position = pos
    mouse.click(button=Button.left)
    sleep(.5)


def find_img(img_file_name, confidence=None, full_screen=False):
    img_path = ASSETS_PREFIX + img_file_name + ASSETS_FILE_TYPE
    if confidence is None:
        if full_screen:
            return pyautogui.locateCenterOnScreen(img_path)
        else:
            return pyautogui.locateCenterOnScreen(img_path, region=GAME_SCREEN_REGION)
    else:
        return pyautogui.locateCenterOnScreen(img_path, confidence=confidence, region=GAME_SCREEN_REGION)


def check_gem_5():
    global current_state, ad_start_time
    # print("checking gem 5")
    pos = find_img(GEM_5_BUTTON)
    if pos is not None:
        print("found 5 gem, starting ad: ", (time() - gem_5_start_time) / 60, " minutes")
        click(pos)
        change_state(State.VIEWING_AD)
        ad_start_time = time()


def check_ad_closed():
    global current_state, summary, gem_5_start_time
    # print("checking ad closed")
    pos = find_img(GEM_5_CLAIM_BUTTON)
    if pos is not None:
        print("found 5 gem claim, ad closed: ", time() - ad_start_time)
        summary["gem_5_rewards_claimed"] += 1
        gem_5_start_time = time()
        click(pos)
        change_state(State.BATTLING)
        return True

    pos = find_img(CLAIM_REWARD_BUTTON)
    if pos is not None:
        print("found 1.5x coin claim, ad closed: ", time() - ad_start_time)
        click(pos)
        change_state(State.BATTLING)
        return True

    return False


def check_gem_2():
    global gem_2_start_time
    # print("checking gem 2")
    for img in GEM_2_BUTTONS:
        pos = find_img(img, 0.7)
        if pos is not None:
            click(pos)
            print("found 2 gem: ", (time() - gem_2_start_time) / 60, " minutes")
            summary["gem_2_rewards_claimed"] += 1
            gem_2_start_time = time()
            break


def check_game_over():
    global current_state, round_time, ad_start_time
    # print("checking game over")
    pos = find_img(RETRY_BUTTON)
    if pos is not None:
        t = time() - round_time
        if t > 3 * ad_int:
            reward_pos = find_img(ROUND_REWARD_BUTTON)
            if reward_pos is not None:
                print("found game over, watching reward ad")
                click(reward_pos)
                change_state(State.VIEWING_AD)
                ad_start_time = time()
                sleep(1)
                return True

        print("found game over, restarting")
        click(pos)
        change_state(State.BATTLING)


def get_current_tab():
    pos = find_img(UTILITY_TAB_ACTIVATED)
    if pos is not None:
        return Tab.UTILITY
    else:
        return Tab.UNKNOWN


def play_round():
    # print("playing round")
    current_tab = get_current_tab()
    if current_tab is Tab.UTILITY:
        if True:
            click((1173, 868))  # coins/wave
        else:
            click((823, 868))  # coin/kill bonus
    else:
        # print("activating utility tab")
        pos = find_img(UTILITY_TAB_DISACTIVATED)
        if pos is not None:
            click(pos)
            sleep(1)
        else:
            print("uh-oh, bad state")
            return False


def exit_ad():
    global ad_start_time
    print("exiting ad")
    pos = find_img(BLUESTACKS_BACK_BUTTON, full_screen=True)
    if pos is not None:
        click(pos)
        sleep(2)


def reset_game():
    global current_state, summary
    print("resetting game")
    pos = find_img(BLUESTACKS_HOME_BUTTON, full_screen=True)
    if pos is not None:
        click(pos)
        sleep(5)
        for img in THE_TOWER_IMGS:
            pos_tower = find_img(img, full_screen=True)
            if pos_tower is not None:
                click(pos_tower)
                summary["restarts"] += 1
                sleep(5)


def play():
    global current_state, ad_start_time, ad_int
    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()
    print("Starting in state: ", current_state)
    while current_state is not State.QUITTING:
        # sleep(1)
        # print('Mouse: {0}, Color: {1}'.format(mouse.position, pyautogui.pixel(*mouse.position)))
        if current_state is not State.PAUSED:
            t = time()
            if current_state is State.BATTLING:
                if t - round_time > restart_int:
                    check_game_over()
                if t - gem_2_start_time > gem_2_int:
                    check_gem_2()
                if t - gem_5_start_time > gem_5_int:
                    check_gem_5()
                play_round()
            elif current_state is State.VIEWING_AD:
                # print("viewing add time: ", t - ad_start_time)
                if t - ad_start_time > ad_max_timeout_int:
                    reset_game()
                if t - ad_start_time > ad_int:
                    if not check_ad_closed():
                        exit_ad()


# change_state(State.VIEWING_AD)
play()
