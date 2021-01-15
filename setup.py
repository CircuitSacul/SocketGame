import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="socketgame-CircuitSacul",
    version="0.0.1",
    author="Lucas D",
    author_email="circuitsacul@gmail.com",
    description="A package for creating easy LAN games with asyncio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CircuitSacul/SocketGame",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
