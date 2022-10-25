from pynput.mouse import Button, Controller
from pynput import keyboard
import pyautogui
from time import sleep, time

mouse = Controller()
playing = True

# state
state = "BATTLING"  # BATTLING, VIEWING_AD

# times
ad_start_time = 0

# intervals (seconds)
ad_int = 30

# img pts
gem_5_button = [
    ((760, 496), (255, 255, 255)),
    ((745, 479), (255, 255, 255)),
    ((781, 515), (255, 255, 255))
]


def on_press(key):
    a = 1  # This is a no-op


def on_release(key):
    global playing
    if key == keyboard.Key.space:
        playing = False


def click(pos):
    mouse.position = pos
    mouse.click(button=Button.left)
    sleep(.5)


def is_close_to(target, sample, tolerance):
    return abs(target[0]-sample[0]) < tolerance and abs(target[1] - sample[1]) < tolerance and abs(target[2] - sample[2]) < tolerance


def get_pix_color(pos):
    mouse.position = pos
    return pyautogui.pixel(*pos)


def check_5G():
    global state, ad_start_time
    print("checking 5 gem")
    for pt in gem_5_button:
        if not is_close_to(pt[1], get_pix_color(pt[0]), 10):
            return False

    print("found 5 gem")
    click(gem_5_button[0][0])
    state = "VIEWING_AD"
    ad_start_time = time()


def check_ad_finished():
    global state
    print("checking ad finished")


def play():
    global state, ad_start_time, ad_int
    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()
    while playing:
        sleep(1)
        t = time()
        if state == "BATTLING":
            check_5G()
        elif state == "VIEWING_AD":
            if t - ad_start_time > ad_int:
                check_ad_finished()
        # print('Mouse: {0}, Color: {1}'.format(mouse.position, pyautogui.pixel(*mouse.position)))


play()
