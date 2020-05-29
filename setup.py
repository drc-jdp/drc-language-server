from setuptools import setup


requires = [
    "pygls",
]

extras = {}

setup(name='drc-language-server',
      version='1.0',
      description='DRC pygls Language Server',
      author='Benno Lin',
      author_email='blueworrybear@gmail.com',
      license='MIT',
      packages=['server'],
      scripts=[],
      include_package_data=True,
      install_requires=requires,
      extras_require=extras,
      zip_safe=False)
