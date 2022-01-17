# ConGFS Parallel File System
ConGFS is a leading parallel cluster file system,
developed with a strong focus on performance and designed for very easy
installation and management.
If I/O intensive workloads are your problem, ConGFS is the solution.


# Build Instructions

## Prerequisites
Before building ConGFS, install the following dependency packages:

### Red Hat / CentOS
```
$ yum install libuuid-devel libibverbs-devel librdmacm-devel libattr-devel redhat-rpm-config \
  rpm-build xfsprogs-devel zlib-devel ant gcc-c++ gcc \
  redhat-lsb-core java-devel unzip libcurl-devel elfutils-libelf-devel kernel-devel 
  libblkid-devel
```

The `elfutils-libelf-devel` and `kernel-devel` packages can be omitted if you don't intend to
build the client module.

The additional `devtoolset-7` package is also required,
which provides a newer compiler version. The installation steps are outlined here.
Please consult the documentation of your distribution for details.

  1. Install a package with repository for your system:
   - On CentOS, install package centos-release-scl available in CentOS repository:
     ```
     $ sudo yum install centos-release-scl
     ```
   - On RHEL, enable RHSCL repository for you system:
     ```
     $ sudo yum-config-manager --enable rhel-server-rhscl-7-rpms
     ```
  2. Install the collection:
     ```
     $ sudo yum install devtoolset-7
     ```

  3. Start using software collections:
     ```
     $ scl enable devtoolset-7 bash
     ```
  4. Follow the instructions below to build ConGFS.

### For development systems

ConGFS comes with a Makefile capable of building packages for the system on which it is executed.
These include all services, the client module and utilities.

To build RPM packages, run
```
 $ make package-rpm PACKAGE_DIR=packages
```
You may also enable parallel execution with
```
 $ make package-rpm PACKAGE_DIR=packages RPMBUILD_OPTS="-D 'MAKE_CONCURRENCY <n>'"
```
where `<n>` is the number of concurrent processes.

For DEB packages use this command:
```
 $ make package-deb PACKAGE_DIR=packages
```
Or start with `<n>` jobs running in parallel:
```
 $ make package-deb PACKAGE_DIR=packages DEBUILD_OPTS="-j<n>"
```

This will generate individual packages for each service (management, meta-data, storage)
as well as the client kernel module and administration tools.

The above examples use `packages` as the output folder for packages, which must not exist
and will be created during the build process.
You may specify any other non-existent directory instead.

Note, however, that having `PACKAGE_DIR` on a NFS or similar network share may slow down
the build process significantly.

### For production systems, or from source snapshots

By default the packaging system generates version numbers suitable only for development
packages. Packages intended for installation on production systems must be built differently.
All instructions to build development packages (as given above) apply, but additionally the
package version must be explicitly set. This is done by passing `CONGFS_VERSION=<version>`
in the make command line, e.g.
```
 $ make package-deb PACKAGE_DIR=packages DEBUILD_OPTS="-j<n>" CONGFS_VERSION=7.1.4-local1
```

Setting the version explicitly is required to generate packages that can be easily upgraded
with the system package manager.


## Building without packaging
To build the complete project without generating any packages,
simply run
```
$ make
```

The sub-projects have individual make targets, for example `storage-all`,
`meta-all`, etc.

To speed things you can use the `-j` option of `make`.
Additionally, the build system supports `distcc`:
```
$ make DISTCC=distcc
```
