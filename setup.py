from setuptools import setup, find_packages

setup(
    name="saas_app",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=4.0",
        "djangorestframework",
        # add other core dependencies here
    ],
)
