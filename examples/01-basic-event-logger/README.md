# Basic Event Logger

![Demo](https://img.shields.io/badge/Demo-All%20Signals-0EA5E9)
![Output](https://img.shields.io/badge/Output-Live%20Events-15803D)

## Goal

Run the webcam, execute the launch-scope detectors, and print stable events as they fire.

## Gestures Used

- `touch_nose`
- `touch_head`
- `nod`
- `shake_head`
- `pinch`
- `finger_touch`
- `tilt_left`
- `tilt_right`

## Detector Files Used

- `detectors/face_hand/touch_nose.py`
- `detectors/pose_hand/touch_head.py`
- `detectors/face/nod.py`
- `detectors/face/shake_head.py`
- `detectors/face/tilt.py`
- `detectors/hand/pinch.py`
- `detectors/hand/finger_touch.py`

## How It Works

The script loads face and hand task models plus the built-in MediaPipe pose solution, reads webcam frames, and runs all ready launch detectors in one loop. Event detectors print `GestureEvent` objects to the terminal. Tilt is treated as state, so the script prints a small state change record only when left or right tilt changes.

## How to Run

```bash
source .venv/bin/activate
python examples/01-basic-event-logger/main.py
```

## Expected Output

When you perform a supported gesture, the script prints a stable event such as `GestureEvent(name='pinch', ...)` or `GestureEvent(name='nod', ...)`. When you tilt your head, it prints a small state update like `{'name': 'tilt_state', 'tilt_left': True, 'tilt_right': False}`.

## Next Step

Move on to `examples/02-touch-nose-demo/` for a more visual single-detector slice.
