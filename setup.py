from setuptools import setup, find_packages

p_version = "0.2.0"

with open("README.MD") as f:
    long_description = f.read()

setup(
    name="framedork.py",
    version=p_version,
    author="Antony Redman",
    author_email="RumataYounger@gmail.com",
    packages=find_packages(),
    url="https://github.com/RedmanPlus/framedork.py",
    download_url="https://github.com/RedmanPlus/framedork.py/tarball/v{0}".format(
        p_version
    ),
    license="MIT",
    description="A meme web framework on Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=[
        "web",
        "wsgi",
        "framework",
    ],
)