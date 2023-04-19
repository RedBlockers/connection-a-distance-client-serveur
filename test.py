import mss
import mss.tools

with mss.mss() as sct:
    # Get information about each monitor
    monitor = sct.monitors[0]
    # Convert the indices of the monitor dictionary from string to integer
    x, y, w, h = monitor["left"], monitor["top"], monitor["width"], monitor["height"]

    # Capture the monitor image
    sct_img = sct.grab({"left": x, "top": y, "width": w, "height": h})

    # Save the captured image
    filename = "monitor.png"
    mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)