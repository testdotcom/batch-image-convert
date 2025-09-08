import argparse
import logging

import trio
from trio import to_thread

import pillow_jxl  # noqa: F401
from PIL import Image


async def process_image(
    input_path: trio.Path, output_dir: trio.Path, format: str
) -> None:
    output_path = output_dir / f"{input_path.stem}.{format}"

    def _img_conversion():
        with Image.open(input_path) as img:
            img.save(output_path, format.upper(), quality=90)

    try:
        await to_thread.run_sync(_img_conversion)
        logging.debug(f"Successfully converted {input_path.name} -> {output_path.name}")
    except Exception as e:
        logging.error(f"Could not process {input_path.name}: {e}.")


async def batch_convertion(
    input_dir: trio.Path, output_dir: trio.Path, format: str
) -> None:
    allowed_extensions = {".jpg", ".jpeg", ".png"}

    async with trio.open_nursery() as nursery:
        for p in await input_dir.iterdir():
            if p.suffix.lower() in allowed_extensions:
                nursery.start_soon(process_image, p, output_dir, format)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    parser = argparse.ArgumentParser(
        description="Batch convert images to WebP or JXL.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--input-dir",
        type=trio.Path,
        required=True,
        help="Path to the source images.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=trio.Path,
        required=True,
        help="Path where the converted images will be saved.",
    )
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        required=True,
        choices=["jxl"],
        help="The target image format. Must be one of: webp, jxl.",
    )

    cli_args = parser.parse_args()

    try:
        trio.run(
            batch_convertion, cli_args.input_dir, cli_args.output_dir, cli_args.format
        )
    except Exception as e:
        logging.critical(f"An unexpected error occurred: {e}")
