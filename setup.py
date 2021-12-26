import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='metadata-kobo-python',
    version='1.1.2',
    packages=setuptools.find_packages(),
    scripts=[
        'scripts/export_metadata',
        'scripts/init_metadata',
    ],
    author="Martin Jacquet",
    author_email="martin.jacquet@posteo.net",
    description="Exports the metadata from a customized yaml file to the kobo database.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sedith/metadata-kobo-python",
    license='The Unlicense',
)
