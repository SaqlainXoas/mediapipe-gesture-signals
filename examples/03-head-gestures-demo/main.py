"""Run nod, shake, and tilt detectors in one webcam loop."""

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

from detectors.face import NodDetector, ShakeHeadDetector, TiltDetector

LEFT_EYE_OUTER = 33
RIGHT_EYE_OUTER = 263


def create_face_landmarker(model_path: Path):
    """Build the face landmarker used by the demo loop."""
    options = vision.FaceLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path=str(model_path)),
        running_mode=vision.RunningMode.VIDEO,
        num_faces=1,
    )
    return vision.FaceLandmarker.create_from_options(options)


def main() -> None:
    """Read webcam frames, run head detectors, and show the current state."""
    model_dir = REPO_ROOT / "ref-things" / "reference-codes" / "models"
    face_model = model_dir / "face_landmarker.task"
    if not face_model.exists():
        raise FileNotFoundError("Missing MediaPipe face model in ref-things/reference-codes/models/")

    face_landmarker = create_face_landmarker(face_model)
    nod = NodDetector()
    shake = ShakeHeadDetector()
    tilt = TiltDetector()
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        raise RuntimeError("Could not open camera 0")

    last_timestamp_ms = 0
    banner_text = ""
    banner_until = 0.0
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
            face_landmarks = face_result.face_landmarks[0] if face_result.face_landmarks else None

            # 1. Run the face detectors when landmarks are available.
            if face_landmarks:
                now = time.monotonic()
                for event in (nod.update(face_landmarks, now), shake.update(face_landmarks, now)):
                    if event is not None:
                        banner_text = event.name
                        banner_until = now + 0.8
                        print(event)

                tilt_state = tilt.update(face_landmarks)
                if tilt_state != last_tilt_state:
                    print({"name": "tilt_state", **tilt_state})
                    last_tilt_state = tilt_state

                # 2. Draw the eye line so the tilt state is easy to read.
                left_eye = face_landmarks[LEFT_EYE_OUTER]
                right_eye = face_landmarks[RIGHT_EYE_OUTER]
                height, width = frame.shape[:2]
                cv2.line(
                    frame,
                    (int(left_eye.x * width), int(left_eye.y * height)),
                    (int(right_eye.x * width), int(right_eye.y * height)),
                    (96, 165, 250),
                    2,
                )
                active_tilt = "tilt_left" if tilt_state["tilt_left"] else "tilt_right" if tilt_state["tilt_right"] else "neutral"
                cv2.putText(frame, f"tilt: {active_tilt}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (240, 240, 240), 2)
            else:
                # 3. Clear the tilt state when the face drops out.
                last_tilt_state = tilt.update(None)

            if time.monotonic() < banner_until:
                cv2.putText(frame, banner_text, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (34, 197, 94), 2)
            cv2.putText(frame, "nod, shake, or tilt. press q to quit", (20, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (226, 232, 240), 2)
            cv2.imshow("Head Gestures Demo", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()
        face_landmarker.close()


if __name__ == "__main__":
    main()
