import setuptools

setuptools.setup(
    name="tagcounter",
    version="0.0.1",
    author="ragumix",
    packages=['tagcounter'],
    description="An application which can help to count html tags on the webpage",
    package_data={'': ['*.yaml']},
    install_requires=['requests','click','urllib3','PyYAML','pytest','loguru'],
    entry_points={'console_scripts': ['tagcounter = tagcounter.main:main']}
)