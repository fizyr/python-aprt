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

from . import (
	alpm,
	package,
	srcinfo,
	util,
	version
)

parse_alpm_dict          = alpm.parse_alpm_dict
parse_info_dict          = alpm.parse_info_dict
alpm_dict_to_package     = alpm.alpm_dict_to_package
read_package_archive     = alpm.read_package_archive
read_package_file        = alpm.read_package_file
read_package_db_archive  = alpm.read_package_db_archive
read_package_db_file     = alpm.read_package_db_file

Constraint = package.Constraint
Dependency = package.Dependency

Package                 = package.Package
package_from_name       = package.package_from_name
neighbour_table         = package.neighbour_table
reverse_neighbour_table = package.reverse_neighbour_table
reachability_table      = package.reachability_table

SrcInfo    = srcinfo.SrcInfo
Version    = version.Version
