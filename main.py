from pynput.mouse import Button, Controller
from pynput import keyboard
import pyautogui
from time import sleep, time

mouse = Controller()
playing = True

# times
continue_time = 0
elevator_time = 0
stock_time = time()

# intervals (sec)
CONTINUE_INT = 30
ELEVATOR_INT = 10
STOCK_INT = 60 * 1 # 1 minutes

# screen position
screen_pos = "UNKNOWN"


def on_press(key):
    a=1

def on_release(key):
    global playing
    if key == keyboard.Key.space:
        playing = False

def click(pos):
    mouse.position = pos
    mouse.click(button=Button.left)
    sleep(.5)

def go_to_bottom():
    global screen_pos
    if screen_pos != "BOTTOM":
        screen_pos = "BOTTOM"
        click((340,890))
        sleep(1)

def go_to_top():
    global screen_pos
    if screen_pos != "TOP":
        screen_pos = "TOP"
        click((24, 53))
        sleep(1)

def is_close_to(target, sample, tolerance):
    return abs(target[0]-sample[0]) < tolerance and abs(target[1] - sample[1]) < tolerance and abs(target[2] - sample[2]) < tolerance

def avg_color(colors):
    x, y, z = 0, 0, 0
    for color in colors:
        x += color[0]
        y += color[1]
        z += color[2]
    return x / len(colors), y / len(colors), z / len(colors)

def get_pix_color(pos):
    mouse.position = pos
    return pyautogui.pixel(*pos)

def check_continue(button="cont"):
    # print("checking continue")
    global continue_time
    continue_time = time()
    REGION = (69, 309, 347, 323) # left, top, width, height
    try:
        path = "./assets/continue_button.png"
        if button == "yes":
            path = "assets/yes_button.png"
        pos = pyautogui.locateCenterOnScreen(path, region=REGION)
        click(pos)
        continue_time = time()
        # print("clicked continue")
        return True
    except:
        return False

def check_elevator():
    print("checking elevator")
    pass

def check_stock():
    # print("checking stock")
    global stock_time
    stock_time = time()
    STOCK_ALL_POS = (217, 766)
    STOCK_ALL_COLOR = (0, 143, 208)
    go_to_bottom()
    mouse.position = STOCK_ALL_POS
    if is_close_to(get_pix_color(STOCK_ALL_POS), STOCK_ALL_COLOR, tolerance=20):
        # print("restocking")
        click(STOCK_ALL_POS)
        if check_continue(button="yes"):
            print(time(), "RE-STOCK")
        sleep(.25)
        check_continue() # to catch full stock bonus msg

def check_parachute():
    # print("checking parachute")
    PARACHUTE_POS = (245, 107)
    SKY_POS = [(420,105),(455,191),(103,72),(104,230)]
    TOLERANCE = 10
    go_to_top()
    sky_color = avg_color([get_pix_color(pos) for pos in SKY_POS])
    pixel_color = get_pix_color(PARACHUTE_POS)
    if not is_close_to(pixel_color, sky_color, TOLERANCE):
        click(PARACHUTE_POS)
        if check_continue():
            print(time(), "CATCH PARACHUTE")

def play():
    global continue_time, stock_time
    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()
    while playing:
        t = time()
        sleep(.25)
        check_parachute()
        if t - continue_time > CONTINUE_INT:
            check_continue()
        # if t - elevator_time > ELEVATOR_INT:
        #     pass
        if t - stock_time > STOCK_INT:
            check_stock()
        # print('Mouse: {0}, Color: {1}'.format(mouse.position, pyautogui.pixel(*mouse.position)))

play()