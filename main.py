import asyncio
import logging
from pathlib import Path

import pillow_jxl  # noqa: F401
from PIL import Image


def blocking_image_conversion(input_path: Path, output_path: Path) -> str:
    try:
        with Image.open(input_path) as img:
            img.save(output_path, format="JXL", quality=90)
    except Exception as e:
        return f'Could not process {input_path.name}: {e}.'

    return ""

async def process_image(input_path: Path, output_dir: Path) -> str:
    output_path = output_dir / f'{input_path.stem}.jxl'

    msg = await asyncio.to_thread(
        blocking_image_conversion, input_path, output_path
    )

    return msg

async def main():
    input_dir = Path("./test")
    output_dir = Path("./test")
    tasks = []

    allowed_extensions = {".jpg", ".jpeg", ".png"}
    image_paths = [
        p for p in input_dir.iterdir() if p.suffix.lower() in allowed_extensions
    ]

    try:
        async with asyncio.TaskGroup() as tg:
            for path in image_paths:
                task = tg.create_task(process_image(path, output_dir))
                tasks.append(task)

        print(f'Results: {" ".join(t.result() for t in tasks)}')
    except asyncio.CancelledError as e:
        logging.critical("A task has been cancelled.", exc_info=e)
    except Exception as e:
        logging.critical("A task has failed.", exc_info=e)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    asyncio.run(main())
