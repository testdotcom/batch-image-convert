import argparse
import asyncio
import logging
from pathlib import Path

import pillow_jxl  # noqa: F401
from PIL import Image


def blocking_image_conversion(input_path: Path, output_path: Path, format: str) -> str:
    try:
        with Image.open(input_path) as img:
            img.save(output_path, format.upper(), quality=90)
    except Exception as e:
        return f"Could not process {input_path.name}: {e}."

    return ""


async def process_image(input_path: Path, output_dir: Path, format: str) -> str:
    output_path = output_dir / f"{input_path.stem}.jxl"
    msg = await asyncio.to_thread(blocking_image_conversion, input_path, output_path, format)

    return msg


async def batch_convertion(input_dir: Path, output_dir: Path, format: str):
    tasks = []

    allowed_extensions = {".jpg", ".jpeg", ".png"}
    image_paths = [
        p for p in input_dir.iterdir() if p.suffix.lower() in allowed_extensions
    ]

    try:
        async with asyncio.TaskGroup() as tg:
            for path in image_paths:
                task = tg.create_task(process_image(path, output_dir, format))
                tasks.append(task)

        print(f"Results: {' '.join(t.result() for t in tasks)}")
    except asyncio.CancelledError as e:
        logging.critical("A task has been cancelled.", exc_info=e)
    except Exception as e:
        logging.critical("A task has failed.", exc_info=e)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    parser = argparse.ArgumentParser(
        description="Batch convert images to WebP or JXL.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-i", "--input-dir", type=Path, required=True,
        help="Path to the source images."
    )
    parser.add_argument(
        "-o", "--output-dir", type=Path, required=True,
        help="Path where the converted images will be saved."
    )
    parser.add_argument(
        "-f", "--format", type=str, required=True, choices=['webp', 'jxl'],
        help="The target image format. Must be one of: webp, jxl."
    )

    cli_args = parser.parse_args()

    asyncio.run(batch_convertion(cli_args.input_dir, cli_args.output_dir, cli_args.format))
