# Gesture Design Principles

![Rules](https://img.shields.io/badge/Design-Signal%20Rules-1D4ED8)
![Focus](https://img.shields.io/badge/Goal-Stable%20Intent-0F766E)

These are the rules that keep a detector usable in real webcam conditions instead of only looking correct on a lucky frame.

## Normalize Before Comparing

Pixel distances change when the user moves closer to the camera. Compare normalized landmarks or scale thresholds relative to face or hand size.

## Prefer Relative Distances

A raw pixel threshold is brittle. A threshold tied to face width, face height, or hand size survives different users and camera positions much better.

## Avoid Single-Frame Truth

One lucky frame is not proof of a real gesture. Stable interaction comes from short temporal confirmation, not one-frame guesses.

## Use Confirmation Windows

A detector should require the condition to hold for a few frames before it emits an event. This is the fastest practical way to cut accidental triggers.

## Separate Intent From Noise

Small accidental movement should not look the same as a deliberate touch, nod, or pinch. Good detector design makes that distinction explicit.

## Keep Detector Logic Small

A detector is easier to tune when it has one job, obvious thresholds, and only a few helpers. Small modules are easier to trust and easier to debug.
