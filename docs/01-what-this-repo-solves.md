# What This Repo Solves

![Problem](https://img.shields.io/badge/Problem-Raw%20Landmarks%20Are%20Noisy-0F172A)
![Outcome](https://img.shields.io/badge/Outcome-Stable%20Gesture%20Signals-0EA5E9)

MediaPipe is very good at telling you where a face, hand, or pose landmark is on the current frame. It does not tell your app whether the user actually meant to perform a gesture.

That gap matters. Real interaction systems need signals like `touch_nose`, `pinch`, `nod`, or `shake_head` that feel calm and intentional, not twitchy and accidental.

## The Raw-Landmark Gap

Raw landmarks move every frame. They wobble with lighting changes, camera noise, small posture shifts, and temporary occlusion.

If you compare one frame directly to a threshold, you usually get one of two bad outcomes:

- false positives from random motion
- repeated triggers while the same gesture stays true

## The Missing Middle Layer

Apps need a thin decision layer between landmarks and behavior. That layer should answer questions like:

- Is this gesture present for long enough to count?
- Is the movement strong enough to be intentional?
- Has this event already fired and cooled down?
- Should this action behave like a one-shot event or a continuous state?

## What Lives In This Repo

- landmark comparison helpers
- smoothing and simple temporal filtering
- cooldown and confirmation logic
- small readable detectors
- runnable webcam demos that show the signal flow in action

## What It Intentionally Avoids

This repo is not trying to be a product shell, web app, deployment system, or general CV experiments dump.

It stays focused on one job: turning fast landmark streams into gesture output your app can trust.
