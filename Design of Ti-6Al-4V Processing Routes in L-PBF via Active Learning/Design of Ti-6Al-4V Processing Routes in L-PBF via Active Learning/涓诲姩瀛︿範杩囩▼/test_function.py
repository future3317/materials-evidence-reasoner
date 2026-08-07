#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Synthetic benchmark used by the bundled active-learning example.

The CSV values shipped with this example match ``max(0, -V)`` for the
Müller–Brown potential. This is a deterministic benchmark objective, not a
measured Ti-6Al-4V property and not a replacement for an experiment.
"""

from __future__ import annotations

import numpy as np


_A = np.array([-200.0, -100.0, -170.0, 15.0])
_a = np.array([-1.0, -1.0, -6.5, 0.7])
_b = np.array([0.0, 0.0, 11.0, 0.6])
_c = np.array([-10.0, -10.0, -6.5, 0.7])
_x0 = np.array([1.0, 0.0, -0.5, -1.0])
_y0 = np.array([0.0, 0.5, 1.5, 1.0])


def muller_brown_potential(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Return the standard Müller–Brown potential for broadcastable inputs."""

    x_arr, y_arr = np.broadcast_arrays(np.asarray(x, dtype=float), np.asarray(y, dtype=float))
    potential = np.zeros_like(x_arr, dtype=float)
    for A, a, b, c, x0, y0 in zip(_A, _a, _b, _c, _x0, _y0):
        dx = x_arr - x0
        dy = y_arr - y0
        potential += A * np.exp(a * dx**2 + b * dx * dy + c * dy**2)
    return potential


def test_function(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Return the example's maximization objective, ``max(0, -V(x, y))``."""

    return np.maximum(0.0, -muller_brown_potential(x, y))


__all__ = ["muller_brown_potential", "test_function"]
