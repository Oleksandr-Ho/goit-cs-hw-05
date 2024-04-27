"""
Завдання 1
Напишіть Python-скрипт, який буде читати всі файли у вказаній користувачем вихідній папці (source folder) і 
розподіляти їх по підпапках у директорії призначення (output folder) на основі розширення файлів. Скрипт 
повинен виконувати сортування асинхронно для більш ефективної обробки великої кількості файлів.
"""

import argparse
import asyncio
from aiopath import AsyncPath
from aioshutil import copyfile
import logging

# Створення парсера аргументів
parser = argparse.ArgumentParser(description="Sort files in a folder based on their extensions.")
parser.add_argument("--source", "-s", help="Source folder where files are located.", default="file/picture")
parser.add_argument("--output", "-o", help="Output folder where files will be distributed.", default="file/dist")

args = parser.parse_args()

# Ініціалізація шляхів
source = AsyncPath(args.source)
output = AsyncPath(args.output)

async def read_folder(path: AsyncPath):
    """
    Recursively reads all files in the given directory and its subdirectories.
    """
    async for item in path.iterdir():
        if await item.is_dir():
            await read_folder(item)
        else:
            await copy_file(item)

async def copy_file(file: AsyncPath):
    """
    Copies the file to the appropriate subfolder in the output directory based on its extension.
    """
    extension_folder = output / file.suffix.lstrip('.')
    await extension_folder.mkdir(parents=True, exist_ok=True)
    destination_file = extension_folder / file.name
    try:
        await copyfile(file, destination_file)
        logging.info(f"File {file} copied to {destination_file}")
    except Exception as e:
        logging.error(f"Error copying {file} to {destination_file}: {str(e)}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    asyncio.run(read_folder(source))
    print(f"Files have been sorted from {source} to {output}.")
