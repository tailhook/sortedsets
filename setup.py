from distutils.core import setup

setup(name='sortedsets',
      version='1.0',
      description="SortedSet structure closely modelled after Redis' sorted sets",
      author='Paul Colomiets',
      author_email='paul@colomiets.name',
      url='http://github.com/tailhook/sortedsets',
      classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        ],
      py_modules=[
        'sortedsets',
        ],
    )
