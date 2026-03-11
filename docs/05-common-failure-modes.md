# Common Failure Modes

![Failure Modes](https://img.shields.io/badge/Debug-Common%20Breakpoints-991B1B)
![Tuning](https://img.shields.io/badge/Fix-Thresholds%20and%20Timing-475569)

Most bad gesture systems fail in the same few ways. Knowing these patterns saves a lot of random threshold tweaking.

## False Positives From Noisy Motion

A detector that trusts one frame will usually misfire.

## Repeated Fire Without Cooldown

If a gesture stays true for ten frames, an event detector can emit ten times unless cooldown logic blocks repeats.

## Camera Angle Mismatch

Thresholds that worked for one camera angle may fail when the user is off-center, lower in frame, or much closer to the camera.

## Low FPS Instability

Lower frame rates can make confirmation windows feel slower and less reliable, especially for quick gestures.

## Thresholds Too Loose or Too Strict

Most tuning problems come down to threshold choice, confirmation length, or cooldown timing.

## Occlusion

A hidden fingertip or partially hidden face can break a detector that assumes perfect landmarks every frame.

## Similar Gesture Shapes

Some gestures overlap visually. A hand near the face can look like several candidate touches unless the target zone is narrow and intentional.
