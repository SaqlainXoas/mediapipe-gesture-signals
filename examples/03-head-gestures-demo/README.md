# Head Gestures Demo

![Demo](https://img.shields.io/badge/Demo-Head%20Signals-2563EB)
![Behavior](https://img.shields.io/badge/Shows-Event%20vs%20State-0F766E)

## Goal

Run the face-only head gesture detectors together and watch event vs state behavior.

## Gestures Used

- `nod`
- `shake_head`
- `tilt_left`
- `tilt_right`

## Detector Files Used

- `detectors/face/nod.py`
- `detectors/face/shake_head.py`
- `detectors/face/tilt.py`

## How It Works

The script loads the MediaPipe face landmarker, tracks the eye line and nose movement, and runs the head gesture detectors in one webcam loop. `nod` and `shake_head` emit one-shot events, while tilt stays active as long as your head remains angled. The overlay shows the eye line plus the current tilt state, and recent event detections are printed to the terminal.

## How to Run

```bash
source .venv/bin/activate
python examples/03-head-gestures-demo/main.py
```

## Expected Output

When you nod, the terminal prints a `GestureEvent(name='nod', ...)`. When you shake, it prints `GestureEvent(name='shake_head', ...)`. The frame also shows `tilt: tilt_left`, `tilt: tilt_right`, or `tilt: neutral` based on your head angle.

## Next Step

Open `examples/04-game-input-demo/` to map these gestures to simple app-like actions.
