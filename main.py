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
    "start_coins": 281.46,
    "start_gems": 369
}

# Times
ad_start_time = 0
gem_5_start_time = 0
gem_2_start_time = 0
round_time = time()

# Intervals (seconds)
ad_int = 30
gem_5_int = 10 * 60  # 10 minutes
gem_2_int = 10 * 60  # 10 minutes
sprint_t6_int = 37
restart_int = 60

# Assets
ASSETS_PREFIX = "./assets/"
ASSETS_FILE_TYPE = ".png"

GEM_5_BUTTON = "gem_5_button"
GEM_5_CLAIM_BUTTON = "gem_5_claim_button"
GEM_2_BUTTON = "gem_2_button"
RETRY_BUTTON = "retry_button"
AD_CLOSE_BUTTONS = [f"ad_close_{x}" for x in range(4)]  # TODO: make this dynamic (grabs asset files with this prefix from the folder)


def log(*args):
    line = ""
    for item in args:
        line += str(item) + " "
    print(line)
    log_file.write(line + "\n")


def on_press(key):
    a = 1  # This is a no-op


def on_release(key):
    global current_state, past_state
    if key == keyboard.Key.ctrl_r:
        if current_state == State.PAUSED:
            log("Un-pausing game!")
            current_state = past_state
        else:
            log("Pausing game!")
            past_state = current_state
            current_state = State.PAUSED
    elif key == keyboard.Key.alt_gr:
        log("Quitting!")
        current_state = State.QUITTING
    elif key == keyboard.Key.shift_r or key == keyboard.Key.shift_l:
        total_time = time() - summary["start_time"]
        log("\nPrinting run summary")
        log("----------------------------------------------------------------------------")
        log(summary)
        log("Total run time: ", total_time, " seconds")
        total_gems = 5 * summary["gem_5_rewards_claimed"] + 2 * summary["gem_2_rewards_claimed"]
        log("Total gems collected: ", total_gems)
        log("Gems/hr: ", total_gems / (total_time / 3600))
        log("----------------------------------------------------------------------------")


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
    # log("checking gem 5")
    pos = find_img(GEM_5_BUTTON)
    if pos is not None:
        log("found 5 gem, starting ad: ", (time() - gem_5_start_time) / 60, " minutes")
        click(pos)
        current_state = State.VIEWING_AD
        ad_start_time = time()


def check_ad_finished():
    global current_state
    log("checking ad finished")
    for img in AD_CLOSE_BUTTONS:
        pos = find_img(img)
        if pos is not None:
            log("found ad finished, closing ad")
            click(pos)


def check_ad_closed():
    global current_state, summary, gem_5_start_time
    log("checking ad closed")
    pos = find_img(GEM_5_CLAIM_BUTTON)
    if pos is not None:
        log("found 5 gem claim, claiming reward")
        summary["gem_5_rewards_claimed"] += 1
        gem_5_start_time = time()
        click(pos)
        current_state = State.BATTLING
        return True
    else:
        return False


def check_gem_2():
    global gem_2_start_time
    # log("checking gem 2")
    pos = find_img(GEM_2_BUTTON, 0.7)
    if pos is not None:
        log("found 2 gem: ", (time() - gem_2_start_time) / 60, " minutes")
        summary["gem_2_rewards_claimed"] += 1
        gem_2_start_time = time()
        click(pos)


def check_game_over():
    global current_state, round_time
    log("checking game over")
    pos = find_img(RETRY_BUTTON)
    if pos is not None:
        log("found game over, retrying")
        round_time = time()
        click(pos)
        current_state = State.BATTLING


def play():
    global current_state, ad_start_time, ad_int, log_file
    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()
    log("Starting in state: ", current_state)
    while current_state is not State.QUITTING:
        # sleep(1)
        # log('Mouse: {0}, Color: {1}'.format(mouse.position, pyautogui.pixel(*mouse.position)))
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
                if t - ad_start_time > ad_int:
                    if not check_ad_closed():
                        check_ad_finished()


# current_state = State.VIEWING_AD
play()
log_file.close()

# cards for t6 sprints: extra orb, coins, critical coin, intro sprint, wave skip, crit chance
