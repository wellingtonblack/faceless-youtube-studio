"""Allow ``python -m pipeline`` to run the studio CLI."""

from pipeline.cli.main import main


if __name__ == "__main__":
    raise SystemExit(main())
