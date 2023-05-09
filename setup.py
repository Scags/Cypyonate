import setuptools
import sys

with open("README.md", "r", encoding="utf-8") as f:
	long_description = f.read()

# Separate commands for 32-bit and 64-bit
if sys.maxsize > 2**32:
	entrypoint = "cypy"
else:
	entrypoint = "cypy32"

setuptools.setup(
	name="Cypyonate",
	version="1.3.0.4",
	author="John Mascagni",
	author_email="johnmascagni@gmail.com",
	description="An extendable command-line injector built entirely in Python",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/Scags/Cypyonate",
	project_urls=
	{
		"Bug Tracker": "https://github.com/Scags/Cypyonate/issues",
	},
	entry_points=
	{
		'console_scripts':
		[
			f'{entrypoint} = cypyonate.cypyonate:main'
		]
	},
	classifiers=
	[
		"Programming Language :: Python :: 3",
		"Operating System :: OS Independent",
	],
	package_dir={"": "src"},
	packages=setuptools.find_packages(where="src"),
	python_requires=">=3.6",
)
