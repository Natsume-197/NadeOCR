from setuptools import setup, find_namespace_packages

setup(
    name="nadeocr",
    version="1.0.1",
    author="Natsume",
    author_email="jonathan.197ariza@gmail.com",
    license="GPLv3",
    packages=find_namespace_packages(),
    include_package_data=True,
    install_requires=[
        "google-cloud-vision",
        "manga_ocr",
        "pynput",
        "pyperclip",
        "PyQt5",
        "PySide6",
    ],
    entry_points={
        "console_scripts": [
            "nadeocr = nadeocr.main:run",
        ]
    },
)
