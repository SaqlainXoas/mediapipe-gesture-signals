# Thresholds, Smoothing, and Cooldowns

![Tuning](https://img.shields.io/badge/Tuning-Core%20Signal%20Layer-DC2626)
![Most Important](https://img.shields.io/badge/Guide-Most%20Important-7C2D12)

This is the practical tuning stack behind almost every stable detector in the repo.

## Threshold Basics

A threshold is the line between "not happening" and "happening". For touch detection that usually means a distance threshold between two landmarks or between a fingertip and a target zone.

Loose thresholds fire too often. Tight thresholds miss real gestures.

## Smoothing Basics

Landmarks move a little even when the user is still. A simple EMA or moving average can reduce that noise without turning the detector into a framework.

## Cooldown and Debounce

An event detector should not fire every frame while the gesture remains true. Cooldown gives the user one event, then blocks repeats for a short interval.

## Hold Duration

Some gestures should survive a short hold before they count. Requiring a condition to stay true across a few frames is often enough.

## Frame Confirmation

Confirmation windows are the easiest way to avoid accidental one-frame triggers. The detector counts consecutive matching frames and emits only when the count is high enough.

## Fast Tuning Smell Test

Too sensitive:

- threshold too large
- no confirmation
- no cooldown

Too strict:

- threshold too small
- too many confirmation frames
- cooldown too long for repeated interaction
