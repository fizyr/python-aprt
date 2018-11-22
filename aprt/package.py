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

from enum import Enum, unique
import operator

from . import util
from .version import Version

@unique
class Constraint(Enum):
	eq = 0
	gt = 1
	lt = 2
	ge = 3
	le = 4

	@classmethod
	def parse(cls, string):
		if string == "=":  return cls.eq
		if string == ">":  return cls.gt
		if string == "<":  return cls.lt
		if string == ">=": return cls.ge
		if string == "<=": return cls.le
		if string == "==": return cls.eq # Sigh... stupid people
		raise ValueError("Invalid constraint `{}'.".format(string))

	def __str__(self):
		if self is self.__class__.eq: return "="
		if self is self.__class__.gt: return ">"
		if self is self.__class__.lt: return "<"
		if self is self.__class__.ge: return ">="
		if self is self.__class__.le: return "<="
		raise ValueError("Invalid constraint value `{}'.".format(self.value))

	def functor(self):
		if self is self.__class__.eq: return operator.eq
		if self is self.__class__.gt: return operator.gt
		if self is self.__class__.lt: return operator.lt
		if self is self.__class__.ge: return operator.ge
		if self is self.__class__.le: return operator.le

class Dependency:
	"""
	A dependency on a package.
	Consists of a name, a contraint and a version.
	"""
	def __init__(self, name, constraint = None, version = None):
		self.name       = name;
		self.version    = version
		self.constraint = constraint

	def satisfiedBy(self, package):
		if self.constraint is None: return self.name == package.name
		return self.name == package.name and self.constraint.toFunctor(package.version(), self.version)

	@classmethod
	def parse(cls, blob):
		constraint_start = util.find_if(blob, lambda x: util.is_one_of(x, ['=', '>', '<']))
		if constraint_start < 0:
			return cls(blob)

		version_start = util.find_if(blob[constraint_start + 1:], lambda x: not util.is_one_of(x, ['=', '>', '<']))
		if version_start < 0: raise ValueError("Failed to parse dependency: constraint specified without version in `{}'".format(blob))
		version_start += constraint_start + 1

		name       = blob[0:constraint_start]
		constraint = blob[constraint_start:version_start]
		version    = blob[version_start:]

		return cls(name, Constraint.parse(constraint), Version.parse(version))

	def __str__(self):
		if self.constraint is None: return self.name
		return "{}{}{}".format(self.name, self.constraint, self.version);

	def __repr__(self):
		return self.__str__()

class Package:
	"""
	Holds package metadata.
	node.name holds the name of the node.
	node.children holds the data as a dictionary with each key having a list of values.
	"""
	def __init__(self, name):
		self.name = name
		self.data = {
			'pkgname': [name],
		}

	def __make_key(self, key):
		if not key in self.data:
			self.data[key] = []

	def add_value(self, key, value):
		self.__make_key(key)
		self.data[key].append(value);

	def add_values(self, key, values):
		self.__make_key(key)
		self.data[key] += values;

	def get_value(self, key):
		if not key in self.data: return None
		return self.data[key][0]

	def get_values(self, key):
		if not key in self.data: return []
		return self.data[key]

	def version(self):
		return Version(self.get_value('pkgver'), self.get_value('pkgrel'), self.get_value('epoch'))

	def depends(self):
		return map(Dependency.parse, self.get_values('depends'))

	def optdepends(self):
		return map(Dependency.parse, self.get_values('optdepends'))

	def makedepends(self):
		return map(Dependency.parse, self.get_values('makedepends'))

	def checkdepends(self):
		return map(Dependency.parse, self.get_values('checkdepends'))

	def alldepends(self):
		yield from self.depends()
		yield from self.makedepends()
		yield from self.checkdepends()
		#yield from self.optdepends()

	def installed(self):
		return map(package_from_name_guess, self.get_values('installed'))

	def provides(self):
		result = set(map(Dependency.parse, self.get_values('provides')))
		result.add(Dependency.parse(self.name))
		return result

	def providesName(self, name):
		for provide in self.provides():
			if provide.name == name: return True
		return False

	def conflicts(self):
		return map(Dependency.parse, self.get_values('conflicts'))

	def replaces(self):
		return map(Dependency.parse, self.get_values('replaces'))

	def hasOption(self, option):
		return option in self.get_values('options')

	def __str__(self):
		return '{}-{}'.format(self.name, str(self.version()))

	def __repr__(self):
		return '{{Package: {}, version: {}}}'.format(self.name, str(self.version()))

	def split_debug_package(self) -> 'Package':
		"""
		Generate a split debug package based on an existing package.

		This creates a package definition as created by makepkg when
		the debug and split options are given.
		"""
		use_fields = (
			'pkgbase',
			'pkgver',
			'url',
			'builddate',
			'packager',
			'size',
			'arch',
			'license',
			'makedepends',
			'checkdepends',
		)

		package = Package(self.name + '-debug')
		package.add_value('pkgdesc', 'Detached debugging symbols for {}'.format(self.name))

		for key, values in self.data.items():
			if key not in use_fields:
				continue
			package.add_values(key, values)

		return package

def split_pkgname(name):
	"""
		Split a package name in four fields:
		(name, pkgver, pkgrel, epoch)
	"""
	base,  sep, pkgrel = name.rpartition('-')
	name,  sep, pkgver = base.rpartition('-')
	epoch, sep, pkgver = pkgver.partition(':')
	if not sep:
		epoch, pkgver = None, epoch
	else:
		epoch = int(epoch)
	return name, pkgver, pkgrel, epoch

def split_pkgname_arch(name):
	"""
		Split a package name with architecture in five fields:
		(name, pkgver, pkgrel, epoch, arch)
	"""
	rest, sep, arch = name.rpartition('-')
	name, pkgver, pkgrel, epoch = split_pkgname(rest)
	return name, pkgver, pkgrel, epoch, arch

def package_from_name(name):
	name, pkgver, pkgrel, epoch = split_pkgname(name)
	package = Package(name)
	package.add_value('pkgver', pkgver)
	package.add_value('pkgrel', pkgrel)
	package.add_value('epoch',  epoch)
	return package

def package_from_name_arch(name):
	name, pkgver, pkgrel, epoch, arch = split_pkgname_arch(name)
	package = Package(name)
	package.add_value('pkgver', pkgver)
	package.add_value('pkgrel', pkgrel)
	package.add_value('epoch',  epoch)
	package.add_value('arch',   arch)
	return package

def package_from_name_guess(name):
	# makepkg before pacman 5.0.1 didn't store architecture in installed = ...
	# so here we guess if the last field is the architecture or not....
	# Ewww!
	_, _, arch = name.rpartition('-')
	if arch in ('any', 'x86_64', 'i686'):
		return package_from_name_arch(name)
	return package_from_name(name)

def neighbour_table(packages):
	"""
	Build a neighbour table for dependencies.
	"""
	table = {}
	for package in packages:
		table[package.name] = [x.name for x in package.alldepends()]
		for name in map(lambda x: x.name, package.provides()):
			table[package.name] = list(table[package.name])
	return table

def reverse_neighbour_table(packages):
	"""
	Build a neighbour table for reverse dependencies.
	"""
	table = {}
	for package in packages:
		if not package.name in table: table[package.name] = set()
		for dependency in package.alldepends():
			if not dependency.name in table: table[dependency.name] = set()
			for provides in [package.name] + [x.name for x in package.provides()]:
				table[dependency.name].add(package.name)
	return table

def reachability_table(neighbours):
	"""
	Build a reachability table from a neighbour table.
	"""
	reachable = neighbours.copy()
	for a in reachable:
		for b in reachable:
			if a in reachable[b]: reachable[b].update(reachable[a])
	return reachable


def reverse_dependencies(database, packages, recursive = True):
	"""
	Get a set of reverse dependencies for a list of packages.
	If recursive is true indirect reverse dependencies are also given.
	"""
	reverse_dependencies = build_reverse_neighbour_table(database)
	if recursive: reverse_dependencies = reachability_table(reverse_dependencies)

	result = set()
	for package in packages:
		result.update(reverse_dependencies[package])
	return result
