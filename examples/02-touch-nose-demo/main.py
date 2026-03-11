"""Visualize fingertip-to-nose distance and print touch-nose events."""

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

from detectors.core.geometry import average_face_size, distance_3d
from detectors.face_hand.touch_nose import INDEX_FINGER_TIP, NOSE_LANDMARKS, TouchNoseDetector


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
    """Read webcam frames, visualize the threshold, and emit touch events."""
    model_dir = REPO_ROOT / "ref-things" / "reference-codes" / "models"
    face_model = model_dir / "face_landmarker.task"
    hand_model = model_dir / "hand_landmarker.task"
    if not face_model.exists() or not hand_model.exists():
        raise FileNotFoundError("Missing MediaPipe model assets in ref-things/reference-codes/models/")

    face_landmarker = create_face_landmarker(face_model)
    hand_landmarker = create_hand_landmarker(hand_model)
    detector = TouchNoseDetector()
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        raise RuntimeError("Could not open camera 0")

    banner_until = 0.0
    status_text = "bring fingertip to nose"
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

            # 1. Draw the nose target area from the current face landmarks.
            if face_result.face_landmarks:
                face_landmarks = face_result.face_landmarks[0]
                nose_landmark = face_landmarks[NOSE_LANDMARKS[0]]
                frame_height, frame_width = frame.shape[:2]
                nose_x = int(nose_landmark.x * frame_width)
                nose_y = int(nose_landmark.y * frame_height)
                threshold = average_face_size(face_landmarks) * detector.threshold_ratio
                cv2.circle(frame, (nose_x, nose_y), max(int(threshold * frame_width), 12), (78, 196, 255), 2)

                # 2. Measure the closest fingertip and feed it through the detector.
                if hand_result.hand_landmarks:
                    now = time.monotonic()
                    raw_distance = None
                    for hand_landmarks in hand_result.hand_landmarks:
                        fingertip = hand_landmarks[INDEX_FINGER_TIP]
                        tip_x = int(fingertip.x * frame_width)
                        tip_y = int(fingertip.y * frame_height)
                        cv2.circle(frame, (tip_x, tip_y), 8, (33, 226, 177), -1)
                        cv2.line(frame, (tip_x, tip_y), (nose_x, nose_y), (148, 163, 184), 2)
                        candidate_distance = min(
                            distance_3d(fingertip, face_landmarks[landmark_index])
                            for landmark_index in NOSE_LANDMARKS
                        )
                        if raw_distance is None or candidate_distance < raw_distance:
                            raw_distance = candidate_distance
                        event = detector.update(face_landmarks, hand_landmarks, now=now)
                        if event is not None:
                            banner_until = now + 0.8
                            print(event)

                    # 3. Show the live metric so the threshold stays easy to tune.
                    if raw_distance is not None:
                        status_text = "touch confirmed" if raw_distance <= threshold else "move closer"
                        cv2.putText(
                            frame,
                            f"distance {raw_distance:.3f} / threshold {threshold:.3f}",
                            (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (240, 240, 240),
                            2,
                        )

            if time.monotonic() < banner_until:
                cv2.putText(frame, "touch_nose detected", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (34, 197, 94), 2)
            cv2.putText(frame, status_text, (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (248, 250, 252), 2)
            cv2.imshow("Touch Nose Demo", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()
        face_landmarker.close()
        hand_landmarker.close()


if __name__ == "__main__":
    main()
