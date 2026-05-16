#!/usr/bin/env python3
"""Entry point for the Algorithm Visualizer & Benchmarking application.

Launches an Eel-based web UI that communicates with the Python core
via exposed functions defined in ``eel_api``.

Usage::

    python main.py
"""

from __future__ import annotations

import eel
import eel_api  # noqa: F401 — registers all @eel.expose functions


def main() -> None:
    """Launch the Eel application.

    Initialises the ``web/`` directory as the static file root, then
    opens ``index.html`` in a Chrome/Edge app-mode window (or the
    default browser as fallback).  The call to ``eel.start()`` blocks
    until the user closes the window.
    """
    eel.init("web")
    eel.start(
        "index.html",
        size=(1440, 860),
        port=0,
        block=True,
        mode="default",
    )


if __name__ == "__main__":
    main()
