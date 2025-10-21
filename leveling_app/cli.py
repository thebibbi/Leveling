"""Command-line interface that bundles the leveling simulation scripts."""

import argparse
from typing import Callable, Iterable, List, Optional

from leveling_system import run_cli as run_leveling_cli
from platform_visualizer import run_visualizer

AVAILABLE_PLATFORMS: List[str] = ["tripod", "stewart_3dof", "stewart_6dof"]


def _launch(action: Callable[[], None], description: str) -> None:
    """Execute ``action`` and display user-friendly error messages."""

    try:
        action()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Returning to menu...\n")
    except Exception as exc:  # pragma: no cover - defensive UX safeguard
        print(f"\nAn unexpected error occurred while {description}: {exc}\n")


def _interactive_menu(default_platform: str = "tripod") -> None:
    """Provide a simple text-based menu for non-technical users."""

    platform = default_platform

    while True:
        print("=" * 60)
        print("Platform Leveling Application")
        print("=" * 60)
        print(f"Current platform: {platform}")
        print("\nSelect an option:")
        print("  1) Launch 3D visualizer")
        print("  2) Launch leveling system CLI")
        print("  3) Change platform type")
        print("  4) Quit")

        choice = input("Enter choice [1-4]: ").strip()

        if choice == "1":
            _launch(lambda: run_visualizer(platform), "launching the visualizer")
        elif choice == "2":
            _launch(lambda: run_leveling_cli(platform), "starting the leveling system")
        elif choice == "3":
            platform = _prompt_for_platform(platform)
        elif choice == "4":
            print("\nGoodbye!")
            return
        else:
            print("\nPlease enter a valid option.\n")


def _prompt_for_platform(current: str) -> str:
    """Ask the user to pick a supported platform type."""

    print("\nAvailable platforms:")
    for idx, value in enumerate(AVAILABLE_PLATFORMS, start=1):
        print(f"  {idx}) {value}")

    prompt = f"Select platform [1-{len(AVAILABLE_PLATFORMS)}] (current: {current}): "

    while True:
        selection = input(prompt).strip()

        if selection == "":
            return current

        if selection.isdigit():
            index = int(selection) - 1
            if 0 <= index < len(AVAILABLE_PLATFORMS):
                return AVAILABLE_PLATFORMS[index]

        print("Invalid selection, please try again.")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the platform leveling simulation without touching the source scripts.",
    )

    subparsers = parser.add_subparsers(dest="command")

    visualizer_parser = subparsers.add_parser(
        "visualizer",
        help="Launch the matplotlib visualizer for the selected platform type.",
    )
    visualizer_parser.add_argument(
        "--platform",
        choices=AVAILABLE_PLATFORMS,
        default="tripod",
        help="Platform configuration to display (default: %(default)s).",
    )
    visualizer_parser.set_defaults(
        func=lambda args: run_visualizer(args.platform)
    )

    system_parser = subparsers.add_parser(
        "system",
        help="Launch the interactive leveling system shell.",
    )
    system_parser.add_argument(
        "--platform",
        choices=AVAILABLE_PLATFORMS,
        default="tripod",
        help="Platform configuration to control (default: %(default)s).",
    )
    system_parser.set_defaults(
        func=lambda args: run_leveling_cli(args.platform)
    )

    menu_parser = subparsers.add_parser(
        "menu",
        help="Open the guided text menu (default behaviour).",
    )
    menu_parser.add_argument(
        "--platform",
        choices=AVAILABLE_PLATFORMS,
        default="tripod",
        help="Preselect a platform configuration when the menu opens.",
    )
    menu_parser.set_defaults(
        func=lambda args: _interactive_menu(args.platform)
    )

    return parser


def main(argv: Optional[Iterable[str]] = None) -> None:
    """Entry point used by both ``python -m`` and the console script."""

    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if hasattr(args, "func"):
        args.func(args)
    else:
        _interactive_menu()
