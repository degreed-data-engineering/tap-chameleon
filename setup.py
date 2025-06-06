from setuptools import setup, find_packages


setup(name = "tap-chameleon",
    version = 0.1,
    description = "chameleon for Degreed taps in Meltano",

    author = "Degreed",
    author_email = "",
    url = "https://github.com/degreed-data-engineering/tap-chameleon",
    packages = find_packages(),
    package_data = {},
    include_package_data = True,
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Science/Research',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Astronomy'
      ],
      install_requires=[
        "requests>=2.25.1",
        # ... other dependencies ...
    ],
    zip_safe=False
)