#!/usr/bin/env python

from setuptools import setup


setup(
	name = "webmedia",
	version = "0.1",

    packages = ['webmedia'],
	package_dir = { 'webmedia': 'webmedia', },
	include_package_data = True,    # include everything in source control

	install_requires = [],


	# metadata for upload to PyPI
	author = "orangotoe",
	author_email = "contato@orangotoe.com.br",
	description = "webmedia is a tool to manage static files usage on templates",
	license = "Private",
    url = "http://www.orangotoe.com.br",
)
