import cv2
import numpy.typing
import win32gui
import win32api
import win32con
import win32ui
import time
import pynput.mouse
import mouse, keyboard
from PIL import ImageGrab
import numpy




def get_window_under_mouse():
    """Gets the dimensions of the window currently under the mouse cursor."""

    flags, hcursor, point = win32gui.GetCursorInfo()
    hwnd = win32gui.WindowFromPoint(point)

    if hwnd:
        rect = win32gui.GetWindowRect(hwnd)
        left, top, right, bottom = rect
        width = right - left
        height = bottom - top

        window_title = win32gui.GetWindowText(hwnd) 

        return {
            "hwnd": hwnd,
            "title": window_title,
            "left": left,
            "top": top,
            "right": right,
            "bottom": bottom,
            "width": width,
            "height": height
        }
    else:
        return None

def draw_rectangle_on_screen(x, y, width, height, color=(255, 0, 0), thickness=2):
    """Draws a rectangle directly on the screen."""

    # Get the device context for the entire screen
    hdc = win32gui.GetWindowDC(0)

    # Create a pen with the specified color and thickness
    hpen = win32gui.CreatePen(win32con.PS_SOLID, thickness, win32api.RGB(*color))
    win32gui.SelectObject(hdc, hpen)

    # Draw the rectangle
    win32gui.MoveToEx(hdc, x, y)
    win32gui.LineTo(hdc, x + width, y)
    win32gui.LineTo(hdc, x + width, y + height)
    win32gui.LineTo(hdc, x, y + height)
    win32gui.LineTo(hdc, x, y)  # Close the rectangle

    # Clean up resources
    win32gui.DeleteObject(hpen)
    win32gui.ReleaseDC(0, hdc)

def on_click(xn, yn, button, pressed):
    if button == pynput.mouse.Button.left and pressed:
        global data, window_info
        data = window_info
        return False  # Return False to block the click
def capture_window_area(window_info):
    """
    Captures a screenshot of a specific window area defined by window_info.

    Args:
        window_info (dict): A dictionary containing window information:
            "title": Window title (optional, used for debugging).
            "left": Left coordinate of the window area.
            "top": Top coordinate of the window area.
            "right": Right coordinate of the window area.
            "bottom": Bottom coordinate of the window area.
            "width": Width of the window area (optional, can be calculated).
            "height": Height of the window area (optional, can be calculated).

    Returns:
        numpy.ndarray: A NumPy array representing the captured window area as a BGR image.
                          Returns None if capturing fails.
    """

    try:
        # Capture the entire screen
        screenshot = ImageGrab.grab(bbox=(window_info["left"], window_info["top"], window_info["right"], window_info["bottom"]))

        # Convert RGB to BGR (OpenCV uses BGR)
        screenshot_bgr = cv2.cvtColor(numpy.array(screenshot), cv2.COLOR_RGB2BGR)

        # Crop the screenshot to the specified window area

        return screenshot_bgr

    except Exception as e:
        print(f"Error capturing window area: {e}")
        return None
def pixelate(image, block_size=10) -> numpy.ndarray:
    """Pixelates the image by averaging pixel values within blocks."""

    height, width = image.shape[:2]
    new_height = height // block_size
    new_width = width // block_size

    # Resize the image down
    pixelated_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    return pixelated_image
def is_green(red, green, blue) -> bool:
    return ((blue < 0.8*green) and (red < 0.64 * green)) and (red+green+blue)>35
def process_pixels(image:numpy.ndarray):
    j={}
    for l in range(len(image)-1, -1, -1):
        start = None
        for i in range(len(image[l])-1, -1, -1):
            red = image[l,i,0]
            green = image[l,i,1]
            blue = image[l,i,2]
            pass
            if is_green(red, green, blue):
                if start == None:
                    start = i
            elif start!=None:
                click((i+start)/2,l)
                # time.sleep(1)
                return
def click(x, y):
    # print(x,y)
    cx = int(data['left'] + x*pixelize_value)
    cy = int(data['top'] + y*pixelize_value + pixelize_value//2)
    mouse.move(cx,cy)
    mouse.click()
    mouse.release()
    pass
def main():
    while run:
        fps_start = time.time()
        try:
            window_area = capture_window_area(window_info)
            # cv2.imwrite("original_image.png", window_area)  # remove
            processed_image = pixelate(window_area, pixelize_value)
            # cv2.imwrite("pixelated_image.png", processed_image) # remove
            processed_image = process_pixels(processed_image)
            # cv2.imwrite("pixelated_image2.png", processed_image) # remove
            fps_end = time.time()
            print("FPS:", 1/(fps_end-fps_start))
        except Exception as e:
            print(f"Error: {e}")
            break
def test_proc(image):
    for l in range(len(image)-1, -1, -1):
        for i in range(len(image[l])-1, -1, -1):
            red = image[l,i,0]
            green = image[l,i,1]
            blue = image[l,i,2]
            if is_green(red, green, blue):
                image[l,i] = [255,0,0]
                pass
    return image
# for i in range(1,50):
#     img = cv2.imread('sample.jpg')
#     cv2.imwrite(f'pixelated_sample{i}.png', test_proc(pixelate(img,i)))

# exit()

color = [(0, 0, 255), (255,0,0)]
thickness = 3
temp = 0
pixelize_value = 16

listener = pynput.mouse.Listener(on_click=on_click)
listener.start()
data = {}
while data == {}:
    window_info = get_window_under_mouse()

    if window_info:
        x = window_info['left']
        y = window_info['top']
        width = window_info['width']
        height = window_info['height']
        draw_rectangle_on_screen(x, y, width, height, color[temp], thickness)
        temp = (temp+1) % len(color)
    else:
        print("No window found under the mouse cursor.")
    time.sleep(0.5)
print(data)
def on_delete_press(*p):
    global run
    run = not run
keyboard.on_release_key('delete',on_delete_press)
run = False
# input()
while True:
    main()