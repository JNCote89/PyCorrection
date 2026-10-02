import os
import sys


def init_linux_qt_env():
    """Resolves missing X11 compose tables and fontconfig for Linux builds."""
    if not sys.platform.startswith("linux"):
        return

    app_dir = os.path.dirname(os.path.abspath(__file__))


    if "XLOCALEDIR" not in os.environ:
        xlocale_candidates = [os.path.join(app_dir, "share", "X11", "locale"),
                              "/usr/share/X11/locale",
                              "/usr/lib/X11/locale",
                              "/usr/local/share/X11/locale"]

        for path in xlocale_candidates:
            if os.path.isdir(path):
                os.environ["XLOCALEDIR"] = path
                break

    if "FONTCONFIG_FILE" not in os.environ:
        fontconfig_candidates = [os.path.join(app_dir, "etc", "fonts", "fonts.conf"),
                                 "/etc/fonts/fonts.conf",
                                 "/usr/share/fontconfig/fonts.conf"]

        for path in fontconfig_candidates:
            if os.path.isfile(path):
                os.environ["FONTCONFIG_FILE"] = path
                break
