import asyncio
import sys

from pydantic import ValidationError

from orbotino.app import Application
from orbotino.core.logging import setup_logging
from orbotino.core.settings import get_settings


def main() -> None:
    try:
        settings = get_settings()
    except ValidationError as error:
        print(f"orbotino couldn't start, check backend/.env:\n{error}", file=sys.stderr)
        sys.exit(1)

    setup_logging(settings.log_level)

    app = Application(settings)
    asyncio.run(app.run())


if __name__ == "__main__":
    main()
