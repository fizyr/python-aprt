from setuptools import setup

from glob import glob

setup(
	name='aprt',
	version='0.1.17',
	description='Arch Linux Package Repository Tools',
	url='https://github.com/fizyr/python-aprt',
	author='Maarten de Vries',
	author_email='maarten@de-vri.es',
	license='BSD',
	packages=['aprt'],
	scripts=glob('bin/*'),
	include_package_data=True,
	zip_safe=True
)
