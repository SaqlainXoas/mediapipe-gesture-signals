"""Run all launch-scope detectors and print stable outputs to the terminal."""

from pathlib import Path
import sys
import time

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from detectors import (
    FingerTouchDetector,
    NodDetector,
    PinchDetector,
    ShakeHeadDetector,
    TiltDetector,
    TouchHeadDetector,
    TouchNoseDetector,
)


def create_face_landmarker(model_path: Path):
    """Build the face landmarker used by the example loop."""
    options = vision.FaceLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path=str(model_path)),
        running_mode=vision.RunningMode.VIDEO,
        num_faces=1,
    )
    return vision.FaceLandmarker.create_from_options(options)


def create_hand_landmarker(model_path: Path):
    """Build the hand landmarker used by the example loop."""
    options = vision.HandLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path=str(model_path)),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=2,
    )
    return vision.HandLandmarker.create_from_options(options)


def main() -> None:
    """Read webcam frames, run all detectors, and print any stable results."""
    model_dir = REPO_ROOT / "ref-things" / "reference-codes" / "models"
    face_model = model_dir / "face_landmarker.task"
    hand_model = model_dir / "hand_landmarker.task"
    if not face_model.exists() or not hand_model.exists():
        raise FileNotFoundError("Missing MediaPipe model assets in ref-things/reference-codes/models/")

    face_landmarker = create_face_landmarker(face_model)
    hand_landmarker = create_hand_landmarker(hand_model)
    pose = mp.solutions.pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    touch_nose = TouchNoseDetector()
    nod = NodDetector()
    shake = ShakeHeadDetector()
    tilt = TiltDetector()
    touch_head = TouchHeadDetector()
    pinch = PinchDetector()
    finger_touch = FingerTouchDetector()
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        raise RuntimeError("Could not open camera 0")

    last_timestamp_ms = 0
    last_tilt_state = {"tilt_left": False, "tilt_right": False}
    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            timestamp_ms = int(time.time() * 1000)
            if timestamp_ms <= last_timestamp_ms:
                timestamp_ms = last_timestamp_ms + 1
            last_timestamp_ms = timestamp_ms

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            face_result = face_landmarker.detect_for_video(mp_image, timestamp_ms)
            hand_result = hand_landmarker.detect_for_video(mp_image, timestamp_ms)
            pose_result = pose.process(rgb_frame)
            now = time.monotonic()

            # 1. Pull the latest landmark sets from each model result.
            face_landmarks = face_result.face_landmarks[0] if face_result.face_landmarks else None
            pose_landmarks = pose_result.pose_landmarks.landmark if pose_result.pose_landmarks else None

            # 2. Run face-only detectors before mixing in hand or pose signals.
            if face_landmarks:
                for event in (nod.update(face_landmarks, now), shake.update(face_landmarks, now)):
                    if event is not None:
                        print(event)
                tilt_state = tilt.update(face_landmarks)
                if tilt_state != last_tilt_state:
                    print({"name": "tilt_state", **tilt_state})
                    last_tilt_state = tilt_state
            else:
                last_tilt_state = tilt.update(None)

            # 3. Run hand-only and cross-stream detectors for each detected hand.
            if hand_result.hand_landmarks:
                for hand_landmarks in hand_result.hand_landmarks:
                    for event in (pinch.update(hand_landmarks, now), finger_touch.update(hand_landmarks, now)):
                        if event is not None:
                            print(event)
                    if face_landmarks:
                        event = touch_nose.update(face_landmarks, hand_landmarks, now)
                        if event is not None:
                            print(event)
                    if pose_landmarks:
                        event = touch_head.update(pose_landmarks, hand_landmarks, now)
                        if event is not None:
                            print(event)

            cv2.putText(frame, "Press q to quit", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (240, 240, 240), 2)
            cv2.imshow("Basic Event Logger", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()
        pose.close()
        face_landmarker.close()
        hand_landmarker.close()


if __name__ == "__main__":
    main()
