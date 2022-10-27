from pynput.mouse import Button, Controller
from pynput import keyboard
import pyautogui
import enum
from time import sleep, time
import datetime


class State(enum.Enum):
    PAUSED = 1
    QUITTING = 2

    BATTLING = 10
    VIEWING_AD = 11


mouse = Controller()
current_state = State.BATTLING
past_state = State.BATTLING
log_file = open(f'./logs/{datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")}.txt', 'w')
summary = {
    "gem_5_rewards_claimed": 0,
    "gem_2_rewards_claimed": 0,
    "start_time": time(),
    "start_coins": "1.35M",
    "start_gems": 619
}

# Times
ad_start_time = time()
gem_5_start_time = 0
gem_2_start_time = 0
round_time = time()

# Intervals (seconds)
ad_int = 32
ad_max_timeout_int = 40
gem_5_int = 10 * 60  # 10 minutes
gem_2_int = 10 * 60  # 10 minutes
sprint_t6_int = 37
restart_int = 45

# Assets
ASSETS_PREFIX = "./assets/"
ASSETS_FILE_TYPE = ".png"

GEM_5_BUTTON = "gem_5_button"
GEM_5_CLAIM_BUTTON = "gem_5_claim_button"
GEM_2_BUTTON = "gem_2_button"
RETRY_BUTTON = "retry_button"
AD_CLOSE_BUTTONS = [f"ad_close_{x}" for x in range(5)]  # TODO: make this dynamic (grabs asset files with this prefix from the folder)
UTILITY_TAB_DISACTIVATED = "utility_tab_disactivated"
UTILITY_TAB_ACTIVATED = "utility_tab_activated"
BLUESTACKS_BACK_BUTTON = "bluestacks_back_button"


# def log(*args):
#     line = ""
#     for item in args:
#         line += str(item) + " "
#     print(line)
#     log_file.write(line + "\n")


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


def find_img(img_file_name, confidence=None):
    if confidence is None:
        return pyautogui.locateCenterOnScreen(ASSETS_PREFIX + img_file_name + ASSETS_FILE_TYPE)
    else:
        return pyautogui.locateCenterOnScreen(ASSETS_PREFIX + img_file_name + ASSETS_FILE_TYPE, confidence=confidence)


def check_gem_5():
    global current_state, ad_start_time
    # print("checking gem 5")
    pos = find_img(GEM_5_BUTTON)
    if pos is not None:
        print("found 5 gem, starting ad: ", (time() - gem_5_start_time) / 60, " minutes")
        click(pos)
        change_state(State.VIEWING_AD)
        ad_start_time = time()


def check_ad_finished():
    global current_state
    # print("checking ad finished")
    for img in AD_CLOSE_BUTTONS:
        pos = find_img(img)
        if pos is not None:
            print("found ad finished, closing ad")
            click(pos)


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
    else:
        return False


def check_gem_2():
    global gem_2_start_time
    # print("checking gem 2")
    pos = find_img(GEM_2_BUTTON, 0.7)
    if pos is not None:
        print("found 2 gem: ", (time() - gem_2_start_time) / 60, " minutes")
        summary["gem_2_rewards_claimed"] += 1
        gem_2_start_time = time()
        click(pos)


def check_game_over():
    global current_state, round_time
    # print("checking game over")
    pos = find_img(RETRY_BUTTON)
    if pos is not None:
        print("found game over, restarting")
        round_time = time()
        click(pos)
        change_state(State.BATTLING)


def play_round():
    print("playing round")
    pos = find_img(UTILITY_TAB_ACTIVATED)
    if pos is None:
        print("activating utility tab")
        dPos = find_img(UTILITY_TAB_ACTIVATED)
        if dPos is not None:
            click(pos)
            sleep(1)
        else:
            print("uh-oh, bad state")
            return False


def reset_game():
    global ad_start_time
    print("resetting game. Current state: ", current_state)
    pos = find_img(BLUESTACKS_BACK_BUTTON)
    if pos is not None:
        click(pos)
        sleep(2)


def play():
    global current_state, ad_start_time, ad_int, log_file
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
            elif current_state is State.VIEWING_AD:
                # print("viewing add time: ", t - ad_start_time)
                if t - ad_start_time > ad_max_timeout_int:
                    reset_game()
                if t - ad_start_time > ad_int:
                    if not check_ad_closed():
                        check_ad_finished()


# change_state(State.VIEWING_AD)
play()
log_file.close()

# cards for t6 sprints: extra orb, coins, critical coin, intro sprint, wave skip, crit chance
