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

from . import alpm

def provides_dep(package, other_package):
	""" Check if a package provides a dependency of another package. """
	for dep in other_package.alldepends():
		if package.providesName(dep.name): return True
	return False

def package_path(repository_dir, package, compression = 'xz'):
	return '{}/{}-{}-{}.pkg.tar.{}'.format(
		repository_dir,
		package.name,
		package.version(),
		package.get_value('arch'),
		compression
	)

def find_newer_deps(package, repository_dir, universe, ignore, quick):
	built_package = alpm.read_package_file(package_path(repository_dir, package))
	for installed in built_package.installed():
		if installed.name in ignore: continue
		try:
			if not provides_dep(universe[installed.name], package): continue
		except KeyError:
			# Previously installed dependency doesn't exist anymore, probably safe to ignore.
			continue

		new_version = universe[installed.name].version()
		if installed.version() < new_version:
			yield installed.name, installed.version(), new_version
			if quick: return

def find_outdated(repository, repository_dir, universe, ignore, quick):
	for name, package in repository.items():
		newer_deps = list(find_newer_deps(package, repository_dir, universe, ignore, quick))
		if newer_deps: yield name, newer_deps
