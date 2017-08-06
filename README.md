# Arch Linux package repository tools

This git repository contains tools to maintain a repository of binary pacman packages.

Note that these tools never read `PKGBUILD`, instead they use `.SRCINFO` files to get their data.
That means they do not execute any code in the `PKGBUILD`,
but it also means you must make sure to update the matching `.SRCINFO` file after modifying a `PKGBUILD`.

For each command, see `command --help` for more information.

## bump-pkgrel
Bump the `pkgrel` of a selection of PKGBUILDs to one above the value in a binary repository (or to 1 if the PKGBUILD `pkgver` is newer than the version in the binary repository).

The `.SRCINFO` is not automatically updated.

## list-unbuilt
List all directories containing a PKGBUILD that builds one or more packages that are not currently in the repository.
If the PKGBUILD builds a newer version, it is also listed.

## list-outdated
List all packages (and optionally their reverse depencendies) that have dependencies that were build more recently than the package itself.
