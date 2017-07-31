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

import functools

def _split_if(string, condition):
	start  = 0
	triggered = False
	for index, val in enumerate(string):
		if condition(val):
			yield string[start:index]
			start = index + 1
	yield string[start:]

def _cmp(a, b):
	return (a > b) - (a < b)

def _strcmp(a, b):
	for char_a, char_b in zip(a, b):
		if a == b: continue
		return _cmp(a, b)
	return _cmp(len(a), len(b))


@functools.total_ordering
class VersionComponent:
	"""
	A version component which consists of a list of parts.
	"""

	def __init__(self, component):
		self.original = component;
		self.parts    = list(self.__class__.split_parts(component));

	@staticmethod
	def split_parts(component):
		"""
		Split a version component into alphabetical and decimal parts.
		The function is a string generator.
		"""
		if not component:
			yield ""
			return

		start   = 0
		numeric = component[0].isdecimal();
		for index, value in enumerate(component):
			if numeric != value.isdecimal():
				yield component[start:index]
				start   = index
				numeric = not numeric
		yield component[start:]

	def __str__(self):
		return ''.join(self.parts)

	def __repr__(self):
		return repr(self.parts)

	def __cmp__(self, other):
		for me, him in zip(self.parts, other.parts):
			# If the parts are equal, defer decision.
			if me == him: continue

			me_decimal  = me.isdecimal();
			him_decimal = him.isdecimal();

			# If not both are decimal, the the decimal one is higher.
			if me_decimal != him_decimal: return me_decimal - him_decimal

			# If both are decimal of unequal length, the longer one is higher.
			if me_decimal and len(me) != len(him): return _cmp(len(me), len(him))

			# In other cases, defer to lexicographical sorting.
			return _strcmp(me, him)

		# If the tested parts are all equal, the shorter component wins.
		return -1 * _cmp(len(self.parts), len(other.parts))

	def __eq__(self, other):
		return self.__cmp__(other) == 0

	def __lt__(self, other):
		return self.__cmp__(other) < 0


def _format_pkgver(pkgver):
	return '.'.join(map(lambda x: str(x), pkgver))

@functools.total_ordering
class Version:
	"""
	Versions consist of an optional epoch, a pkgver and an optional pkgrel.
	The pkgver and pkgrel each consist of alphanumerical components,
	which each consist of alphabetical and decimal parts.
	"""
	def __init__(self, pkgver, pkgrel, epoch = 0):
		self.pkgver_original = pkgver;
		self.pkgrel_original = pkgrel;
		self.pkgver = list(self.__class__.split_components(pkgver))
		self.pkgrel = list(self.__class__.split_components(pkgrel)) if pkgrel is not None else None
		self.epoch  = int(epoch) if epoch is not None else 0

	@staticmethod
	def parse(string):
		"""
		Parse a version string.
		"""
		# Parse optional epoch.
		epoch, sep, rest = string.partition(':')
		if sep:
			epoch = int(epoch)
		else:
			rest  = epoch
			epoch = 0

		# Split the remainder in pkgver and optional pkgrel.
		pkgver, sep, pkgrel = rest.rpartition('-')
		if not sep:
			pkgver = pkgrel
			pkgrel = None

		return Version(pkgver, pkgrel, epoch)

	@staticmethod
	def split_components(component):
		"""
		Split a version component into alphanumerical parts.
		"""
		start  = 0
		for index, val in enumerate(component):
			if not val.isalnum():
				yield VersionComponent(component[start:index])
				start = index + 1
		yield VersionComponent(component[start:])

	def withPkgrel(self, pkgrel):
		if pkgrel is not None:
			return Version(self.pkgver_original, str(pkgrel), self.epoch)
		else:
			return Version(self.pkgver_original, None, self.epoch)

	def withoutPkgrel(self):
		return self.withPkgrel(None)

	def __str__(self):
		if self.epoch == 0:
			if self.pkgrel is None:
				return '{}'.format(_format_pkgver(self.pkgver))
			else:
				return '{}-{}'.format(_format_pkgver(self.pkgver), _format_pkgver(self.pkgrel))
		else:
			if self.pkgrel is None:
				return '{}:{}'.format(self.epoch, _format_pkgver(self.pkgver))
			else:
				return '{}:{}-{}'.format(self.epoch, _format_pkgver(self.pkgver), _format_pkgver(self.pkgrel))

	def __repr__(self):
		return repr((self.pkgver, self.pkgrel, self.epoch))

	def __cmp__(self, other):
		# Epoch trumps everything.
		if self.epoch != other.epoch: return _cmp(self.epoch, other.epoch)

		# The pkgver is the next deciding factor,
		pkgver_dif = _cmp(self.pkgver, other.pkgver)
		if pkgver_dif != 0: return pkgver_dif

		# The pkgrel only weighs in if both version have the pkgrel specified.
		if self.pkgrel is None or other.pkgrel is None: return 0
		return _cmp(self.pkgrel, other.pkgrel);

	def __eq__(self, other):
		return self.__cmp__(other) == 0

	def __lt__(self, other):
		return self.__cmp__(other) < 0
