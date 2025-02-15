from argparse import ArgumentParser

from . import __version__


class ArgParser(ArgumentParser):
    """
    Class to parse command line arguments
    """
    def __init__(self) -> None:
        """
        Constructor
        """
        super().__init__(
            prog="fightsticker",
            description="Fightsticker - Display fightstick inputs for stream"
        )
        # Fightsticker version
        self.add_argument(
            "-v", "--version",
            action="version",
            version=f"Fightsticker {__version__}"
        )
        self.add_argument(
            "-d", "--debug",
            action="store_true",
            help="Enable debug mode",
            dest="DEBUG",
            default=False
        )
