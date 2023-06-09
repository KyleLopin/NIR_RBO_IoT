from setuptools import setup
setup(
    name="NIR Rice Bran Oil monitor",
    version="1.09",
    author="Kyle Vitautas Lopin",
    description="Monitor the Oryzanol and Acid values of Rice Bran oil",
    url="https://github.com/KyleLopin/NIR_RBO_IoT",
    python_requires='>=3.7, <4',
    packages=find_packages(include=["GUI", "tests"]),
    install_requries = [

    ]
)
