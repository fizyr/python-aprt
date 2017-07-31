# Copyright 2017 Delft Robotics BV
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import libarchive
import os
from .package import Package, package_from_name

def parse_alpm_dict(blob):
	"""
	Parse a blob of text as ALPM file.
	The results are returned as a dictionary with each key having a list of values.
	"""
	result = {}
	key    = None
	values = []
	for line in blob.splitlines():
		if len(line) == 0: continue

		if line[0] == '%' and line[-1] == '%':
			if key is not None: result[key] = values
			key         = line[1:-1]
			values      = []
		else:
			values.append(line)
	if key is not None: result[key] = values
	return result

def parse_info_dict(blob):
	"""
	Parse a blob of text as .PKGINFO or .BUILDINFO file.
	The results are returned as a dictionary with each key having a list of values.
	"""
	result = {}
	for line in blob.splitlines():
		if len(line) == 0 or line[0] == '#': continue

		key, value = line.split('=', 1)
		key        = key.strip();
		value      = value.strip();

		if not key in result:
			result[key] = [value]
		else:
			result[key].append(value)
	return result

def alpm_dict_to_package(data):
	name    = data['NAME'][0]
	package = Package(name)
	for key, values in data.items():
		package.add_values(key.lower(), values)
	return package

def read_package_archive(archive):
	data      = {}
	pkginfo   = False
	buildinfo = False
	for entry in archive:
		if entry.isdir: continue
		if entry.pathname == '.PKGINFO':
			pkginfo= True
		elif entry.pathname == '.BUILDINFO':
			buildinfo = True
		else:
			continue
		data.update(parse_info_dict("".join(map(lambda x: x.decode(), entry.get_blocks()))))
		if pkginfo and buildinfo:
			break
	if not pkginfo:   raise RuntimeError("Found no .PKGINFO in archive.")
	if not buildinfo: raise RuntimeError("Found no .BUILDINFO in archive.")

	package = Package(data.pop('pkgname')[0])
	for key, values in data.items():
		package.add_values(key.lower(), values)

	return package

def read_package_file(filename):
	with libarchive.file_reader(filename) as archive:
		return read_package_archive(archive)

def read_package_db_archive(archive):
	result = {}
	for entry in archive:
		if entry.isdir: continue

		package = package_from_name(os.path.dirname(entry.pathname))
		if package.name not in result:
			result[package.name] = package
		else:
			package = result[package.name]

		data = parse_alpm_dict("".join(map(lambda x: x.decode(), entry.get_blocks())))
		for key, values in data.items():
			package.add_values(key.lower(), values)

	return result

def read_package_db_file(filename):
	with libarchive.file_reader(filename) as archive:
		return read_package_db_archive(archive)
