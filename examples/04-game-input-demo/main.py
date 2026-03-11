"""Map gesture events and tilt state onto a tiny menu interaction loop."""

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
    NodDetector,
    PinchDetector,
    ShakeHeadDetector,
    TiltDetector,
    TouchHeadDetector,
    TouchNoseDetector,
)
from detectors.core.cooldown import Cooldown

MENU_ITEMS = ["Start", "Settings", "Accessibility", "Quit"]


def create_face_landmarker(model_path: Path):
    """Build the face landmarker used by the demo loop."""
    options = vision.FaceLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path=str(model_path)),
        running_mode=vision.RunningMode.VIDEO,
        num_faces=1,
    )
    return vision.FaceLandmarker.create_from_options(options)


def create_hand_landmarker(model_path: Path):
    """Build the hand landmarker used by the demo loop."""
    options = vision.HandLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path=str(model_path)),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=2,
    )
    return vision.HandLandmarker.create_from_options(options)


def main() -> None:
    """Read webcam frames and translate gestures into menu actions."""
    model_dir = REPO_ROOT / "ref-things" / "reference-codes" / "models"
    face_model = model_dir / "face_landmarker.task"
    hand_model = model_dir / "hand_landmarker.task"
    if not face_model.exists() or not hand_model.exists():
        raise FileNotFoundError("Missing MediaPipe model assets in ref-things/reference-codes/models/")

    face_landmarker = create_face_landmarker(face_model)
    hand_landmarker = create_hand_landmarker(hand_model)
    pose = mp.solutions.pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    touch_nose = TouchNoseDetector()
    pinch = PinchDetector()
    nod = NodDetector()
    shake = ShakeHeadDetector()
    tilt = TiltDetector()
    touch_head = TouchHeadDetector()
    navigation_cooldown = Cooldown(0.45)
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        raise RuntimeError("Could not open camera 0")

    selected_index = 0
    action_text = "tilt to move, nod or pinch to confirm"
    action_until = 0.0
    last_timestamp_ms = 0
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

            # 2. Use face gestures for navigation, confirm, and cancel actions.
            if face_landmarks:
                tilt_state = tilt.update(face_landmarks)
                if navigation_cooldown.is_ready(now):
                    if tilt_state["tilt_left"]:
                        selected_index = (selected_index - 1) % len(MENU_ITEMS)
                        action_text = f"navigate left -> {MENU_ITEMS[selected_index]}"
                        action_until = now + 0.8
                        navigation_cooldown.trigger(now)
                    elif tilt_state["tilt_right"]:
                        selected_index = (selected_index + 1) % len(MENU_ITEMS)
                        action_text = f"navigate right -> {MENU_ITEMS[selected_index]}"
                        action_until = now + 0.8
                        navigation_cooldown.trigger(now)

                for event in (nod.update(face_landmarks, now), shake.update(face_landmarks, now)):
                    if event is None:
                        continue
                    print(event)
                    if event.name == "nod":
                        action_text = f"confirm {MENU_ITEMS[selected_index]}"
                    else:
                        action_text = "cancel"
                    action_until = now + 0.9

            # 3. Use hand-driven gestures for confirm and reset actions.
            if hand_result.hand_landmarks:
                for hand_landmarks in hand_result.hand_landmarks:
                    for event in (pinch.update(hand_landmarks, now),):
                        if event is not None:
                            print(event)
                            action_text = f"select {MENU_ITEMS[selected_index]}"
                            action_until = now + 0.9
                    if face_landmarks:
                        event = touch_nose.update(face_landmarks, hand_landmarks, now)
                        if event is not None:
                            print(event)
                            action_text = f"confirm {MENU_ITEMS[selected_index]}"
                            action_until = now + 0.9
                    if pose_landmarks:
                        event = touch_head.update(pose_landmarks, hand_landmarks, now)
                        if event is not None:
                            print(event)
                            action_text = "reset menu"
                            action_until = now + 0.9
                            selected_index = 0

            overlay = frame.copy()
            cv2.rectangle(overlay, (20, 20), (330, 220), (15, 23, 42), -1)
            cv2.addWeighted(overlay, 0.78, frame, 0.22, 0, frame)
            cv2.putText(frame, "Gesture Menu", (40, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (226, 232, 240), 2)
            for index, item in enumerate(MENU_ITEMS):
                y = 95 + (index * 30)
                color = (34, 197, 94) if index == selected_index else (203, 213, 225)
                prefix = ">" if index == selected_index else " "
                cv2.putText(frame, f"{prefix} {item}", (45, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            controls = "tilt: move  nod/touch_nose/pinch: confirm  shake: cancel  touch_head: reset"
            cv2.putText(frame, controls, (20, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (241, 245, 249), 2)
            if time.monotonic() < action_until:
                cv2.putText(frame, action_text, (20, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (125, 211, 252), 2)
            cv2.imshow("Game Input Demo", frame)
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
