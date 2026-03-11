from dataclasses import dataclass


@dataclass
class EmaSmoother:
    """Tiny exponential moving average for scalar values."""

    alpha: float = 0.4
    value: float | None = None

    def update(self, sample: float) -> float:
        """Blend a new sample into the running average."""
        if self.value is None:
            self.value = sample
        else:
            self.value = (self.alpha * sample) + ((1 - self.alpha) * self.value)
        return self.value

    def reset(self) -> None:
        """Clear the stored average."""
        self.value = None
