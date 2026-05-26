#!/usr/bin/env python3
"""File này là điểm bắt đầu của chương trình.

Khi chạy file này, chương trình sẽ mở giao diện web bằng Eel.
"""

from __future__ import annotations

import eel
import eel_api  # noqa: F401 — registers all @eel.expose functions


def main() -> None:
    """Mở chương trình bằng Eel.
    
    Return:
        Không trả về gì.
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
