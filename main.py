from pynput.mouse import Button, Controller
from pynput import keyboard
import pyautogui
import enum
from time import sleep, time


class State(enum.Enum):
    PAUSED = 1
    QUITTING = 2

    BATTLING = 10
    VIEWING_AD = 11


mouse = Controller()
current_state = State.BATTLING
past_state = State.BATTLING
summary = {
    "gem_5_rewards_claimed": 0,
    "gem_2_rewards_claimed": 0,
    "start_time": time(),
    "start_coins": 137.35,
    "start_gems": 240
}


# Times
ad_start_time = 0
gem_5_start_time = 0

# Intervals (seconds)
ad_int = 1
gem_5_int = 10 * 60  # 10 minutes

# Assets
GEM_5_BUTTON = "./assets/gem_5_button.png"
GEM_5_CLAIM_BUTTON = "./assets/gem_5_claim_button.png"
AD_CLOSE_BUTTONS = [
    "./assets/ad_close_1.png"
]


def on_press(key):
    a = 1  # This is a no-op


def on_release(key):
    global current_state, past_state
    if key == keyboard.Key.ctrl_r:
        if current_state == State.PAUSED:
            print("Un-pausing game!")
            current_state = past_state
        else:
            print("Pausing game!")
            past_state = current_state
            current_state = State.PAUSED
    elif key == keyboard.Key.alt_gr:
        print("Quitting!")
        current_state = State.QUITTING
    elif key == keyboard.Key.shift_r or key == keyboard.Key.shift_l:
        total_time = time() - summary["start_time"]
        print("\nPrinting run summary")
        print("----------------------------------------------------------------------------")
        print(summary)
        print("Total run time: ", total_time, " seconds")
        total_gems = 5*summary["gem_5_rewards_claimed"] + 2*summary["gem_2_rewards_claimed"]
        print("Total gems collected: ", total_gems)
        print("Gems/hr: ", total_gems / (total_time / 3600))
        print("----------------------------------------------------------------------------")


def click(pos):
    mouse.position = pos
    mouse.click(button=Button.left)
    sleep(.5)


def is_close_to(target, sample, tolerance):
    return abs(target[0] - sample[0]) < tolerance and abs(target[1] - sample[1]) < tolerance and abs(
        target[2] - sample[2]) < tolerance


def get_pix_color(pos):
    mouse.position = pos
    return pyautogui.pixel(*pos)


def find_img(img_path):
    return pyautogui.locateCenterOnScreen(img_path)


def check_gem_5():
    global current_state, ad_start_time
    print("checking gem 5")
    pos = find_img(GEM_5_BUTTON)
    if pos is not None:
        print("found 5 gem, starting ad")
        click(pos)
        current_state = State.VIEWING_AD
        ad_start_time = time()


def check_ad_finished():
    global current_state
    print("checking ad finished")
    for img in AD_CLOSE_BUTTONS:
        pos = find_img(img)
        if pos is not None:
            print("found ad finished, finishing ad")
            click(pos)


def check_ad_closed():
    global current_state
    print("checking ad closed")
    pos = find_img(GEM_5_CLAIM_BUTTON)
    if pos is not None:
        print("found 5 gem claim, claiming reward")
        click(pos)
        current_state = State.BATTLING
        return True
    else:
        return False


def play():
    global current_state, ad_start_time, ad_int
    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()
    while current_state is not State.QUITTING:
        # sleep(.5)
        # print('Mouse: {0}, Color: {1}'.format(mouse.position, pyautogui.pixel(*mouse.position)))
        if current_state is not State.PAUSED:
            t = time()
            if current_state is State.BATTLING:
                check_gem_5()
            elif current_state is State.VIEWING_AD and not check_ad_closed():
                if t - ad_start_time > ad_int:
                    check_ad_finished()


# current_state = "VIEWING_AD"
play()
