# Touch Nose Demo

![Demo](https://img.shields.io/badge/Demo-Single%20Detector-0EA5E9)
![Overlay](https://img.shields.io/badge/View-Live%20Distance%20Overlay-7C3AED)

## Goal

Run the `touch_nose` detector with a minimal OpenCV overlay.

## Gestures Used

- `touch_nose`

## Detector Files Used

- `detectors/face_hand/touch_nose.py`

## How It Works

The script loads face and hand landmarkers, draws the fingertip, nose target area, and the live line between them, then prints each `touch_nose` event. It also shows the current fingertip-to-nose distance against the detector threshold so tuning is easy to understand from the frame itself.

## How to Run

```bash
source .venv/bin/activate
python examples/02-touch-nose-demo/main.py
```

## Expected Output

The window shows the camera feed with a live metric like `distance 0.021 / threshold 0.036`. When the fingertip reaches the nose area for a few frames, the script prints a `GestureEvent` and briefly shows `touch_nose detected`.

## Next Step

Move on to `examples/03-head-gestures-demo/` to see event detectors and state detectors together.
