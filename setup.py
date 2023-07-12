from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in frappe_advanced/__init__.py
from frappe_advanced import __version__ as version

setup(
	name="frappe_advanced",
	version=version,
	description="New ideas and fucntions",
	author="MadCheese",
	author_email="leg.ly@hotmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
