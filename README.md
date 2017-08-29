# Arch Linux package repository tools

This git repository contains tools to maintain a repository of binary pacman packages.

Note that these tools never read `PKGBUILD`, instead they use `.SRCINFO` files to get their data.
That means they do not execute any code in the `PKGBUILD`,
but it also means you must make sure to update the matching `.SRCINFO` file after modifying a `PKGBUILD`.

For each command, see `command --help` for more information.

## bump-pkgrel
Bump the `pkgrel` of selected `PKGBUILD` and `.SRCINFO` files to one above the value in a binary repository.
If the `pkgver` of the `PKGBUILD` is higher than the version in the binary repository, the `pkgrel` is set to 1.

## list-unbuilt
List all directories containing a PKGBUILD that builds one or more packages that are not currently in the repository.
If the `PKGBUILD` builds a newer version, it is also listed.

## list-outdated
List all packages from a specific repository that have dependencies that were build more recently than the package itself.
Reverse dependencies of the packages can also be listed.
