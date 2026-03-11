# Game Input Demo

![Demo](https://img.shields.io/badge/Demo-App--Like%20Input-DC2626)
![Mapping](https://img.shields.io/badge/Flow-Gesture%20to%20Action-7C3AED)

## Goal

Map stable gesture events and tilt state to a tiny menu interaction loop.

## Gestures Used

- `tilt_left`
- `tilt_right`
- `nod`
- `shake_head`
- `touch_nose`
- `touch_head`
- `pinch`

## Detector Files Used

- `detectors/face/tilt.py`
- `detectors/face/nod.py`
- `detectors/face/shake_head.py`
- `detectors/face_hand/touch_nose.py`
- `detectors/pose_hand/touch_head.py`
- `detectors/hand/pinch.py`

## How It Works

The script renders a small on-frame menu and uses gestures as input. Tilt moves the selection left or right with a short cooldown so the menu does not race. `nod`, `touch_nose`, and `pinch` confirm the current item, `shake_head` cancels, and `touch_head` resets the menu back to the first item.

## How to Run

```bash
source .venv/bin/activate
python examples/04-game-input-demo/main.py
```

## Expected Output

The frame shows a highlighted menu item and an action banner like `navigate right -> Settings`, `confirm Start`, or `reset menu`. Matching `GestureEvent` objects are also printed in the terminal for the event-style detectors.

## Next Step

Go back to the main [README](../../README.md) to jump into another detector or guide.
