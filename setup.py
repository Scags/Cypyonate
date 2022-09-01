import setuptools

with open("README.md", "r", encoding="utf-8") as f:
	long_description = f.read()

setuptools.setup(
	name="Cypyonate",
	version="1.0.0.1",
	author="John Mascagni",
	author_email="johnmascagni@gmail.com",
	description="A command-line DLL injector built in Python",
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
			'cypy = cypyonate.cypyonate:main'
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
