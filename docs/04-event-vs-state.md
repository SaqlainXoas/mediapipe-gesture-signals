# Event vs State

![Behavior](https://img.shields.io/badge/Behavior-One--Shot%20vs%20Continuous-0F766E)
![API Shape](https://img.shields.io/badge/Output-Events%20and%20State-334155)

Stable gesture systems get much easier to reason about when you separate one-shot actions from continuous conditions.

## Event

An event fires once when a gesture is confirmed.

Examples:

- `touch_nose`
- `pinch`
- `nod`
- `shake_head`

Use an event when the app needs one action such as confirm, select, cancel, or reset.

## State

A state stays true while the condition remains active.

Examples:

- `tilt_left`
- `tilt_right`

Use a state when the app needs continuous behavior such as steering, scrolling focus, or menu navigation.

## Why The Split Matters

If you treat a state like an event, the action feels spammy. If you treat an event like a state, the app feels sluggish and unclear.

This repo keeps the distinction explicit so the example code stays readable and the detector output shape stays predictable.
