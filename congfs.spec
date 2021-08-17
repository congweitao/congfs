%define VER %(echo '%{CONGFS_VERSION}' | cut -d - -f 1)

%define CONGFS_MAJOR_VERSION %(echo '%{CONGFS_VERSION}' | cut -d . -f 1)
%define CLIENT_DIR /opt/congfs/src/client/client_module_%{CONGFS_MAJOR_VERSION}
%define CLIENT_COMPAT_DIR /opt/congfs/src/client/client_compat_module_%{CONGFS_MAJOR_VERSION}

%define is_sles %(test -f /etc/SUSEConnect && echo 1 || echo 0)

%define _binaries_in_noarch_packages_terminate_build   0

%if %is_sles
%define distver %(release="`rpm -qf --queryformat='%%{VERSION}' /etc/os-release 2> /dev/null | tr . : | sed s/:.*$//g`" ; if test $? != 0 ; then release="" ; fi ; echo "$release")
%define RELEASE sles%{distver}

%else
%if %{defined ?dist}
%define RELEASE %(tr -d . <<< %{?dist})

%else
%define RELEASE generic

%endif
%endif

%define FULL_VERSION %{EPOCH}:%{VER}-%{RELEASE}

%define post_package() if [ "$1" = 1 ] \
then \
	output=$(systemctl is-system-running 2> /dev/null) \
	if [ "$?" == 127 ] \
	then \
		chkconfig %1 on \
	elif [ "$?" == 0 ] || ( [ "$output" != "offline" ] && [ "$output" != "unknown" ] ) \
	then \
		systemctl enable %1.service \
	else \
		chkconfig %1 on \
	fi \
fi

%define preun_package() if [ "$1" = 0 ] \
then \
	output=$(systemctl is-system-running 2> /dev/null) \
	if [ "$?" == 127 ] \
	then \
		chkconfig %1 off \
	elif [ "$?" == 0 ] || ( [ "$output" != "offline" ] && [ "$output" != "unknown" ] ) \
	then \
		systemctl disable %1.service \
	else \
		chkconfig %1 off \
	fi \
fi


Name: congfs
Summary: ConGFS parallel file system
License: ConGFS EULA
Version: %{VER}
Release: %{RELEASE}
URL: http://www.congfs.com
Source: congfs-%{CONGFS_VERSION}.tar
Vendor: Fraunhofer ITWM
BuildRoot: %{_tmppath}/congfs-root
Epoch: %{EPOCH}

%description

Distribution of the ConGFS parallel filesystem.

%clean
rm -rf %{buildroot}

%prep
%setup -c

%define make_j %{?MAKE_CONCURRENCY:-j %{MAKE_CONCURRENCY}}

%build

export CONGFS_VERSION=%{CONGFS_VERSION}
export WITHOUT_COMM_DEBUG=1

make %make_j daemons utils

# disabled, doesn't build
#make -C conond_thirdparty/build %make_j
make -C conond_thirdparty_gpl/build %make_j
make -C utils/build %make_j java_lib

%install

export CONGFS_VERSION=%{CONGFS_VERSION}
export WITHOUT_COMM_DEBUG=1

# makefiles need some adjustments still
mkdir -p \
   ${RPM_BUILD_ROOT}/opt/congfs/sbin \
   ${RPM_BUILD_ROOT}/opt/congfs/lib \
   ${RPM_BUILD_ROOT}/usr/bin \
   ${RPM_BUILD_ROOT}/usr/include \
   ${RPM_BUILD_ROOT}/sbin \
   ${RPM_BUILD_ROOT}/usr/share/doc/congfs-client-devel/examples/ \
   ${RPM_BUILD_ROOT}/usr/share/doc/congfs-utils-devel/examples/congfs-event-listener/build \
   ${RPM_BUILD_ROOT}/usr/share/doc/congfs-utils-devel/examples/congfs-event-listener/source \
   ${RPM_BUILD_ROOT}/opt/congfs/thirdparty/parallel \
   ${RPM_BUILD_ROOT}/etc/bash_completion.d

##########
########## common files
##########

install -D common_package/scripts/etc/congfs/lib/start-stop-functions \
   ${RPM_BUILD_ROOT}/etc/congfs/lib/start-stop-functions
install -D common_package/scripts/etc/congfs/lib/init-multi-mode \
   ${RPM_BUILD_ROOT}/etc/congfs/lib/init-multi-mode

##########
########## libcongfs-ib files
##########

install -D common/build/libcongfs_ib.so \
   ${RPM_BUILD_ROOT}/opt/congfs/lib/libcongfs_ib.so

##########
########## daemons, utils
##########

make DESTDIR=${RPM_BUILD_ROOT} daemons-install utils-install

##########
########## common directories for extra files
##########
mkdir -p \
   ${RPM_BUILD_ROOT}/etc/congfs \
   ${RPM_BUILD_ROOT}/etc/init.d \
   ${RPM_BUILD_ROOT}/opt/congfs/scripts/grafana

##########
########## meta extra files
##########

cp -a meta/build/dist/etc/*.conf ${RPM_BUILD_ROOT}/etc/congfs

# we use the redhat script for all rpm distros, as we now provide our own
# daemon() and killproc() function library (derived from redhat)
install -D meta/build/dist/etc/init.d/congfs-meta.init \
   ${RPM_BUILD_ROOT}/etc/init.d/congfs-meta

#add the genric part of the init script from the common package
cat common_package/build/dist/etc/init.d/congfs-service.init >> ${RPM_BUILD_ROOT}/etc/init.d/congfs-meta

#install systemd unit description
install -D -m644 meta/build/dist/usr/lib/systemd/system/congfs-meta.service \
	${RPM_BUILD_ROOT}/usr/lib/systemd/system/congfs-meta.service
install -D -m644 meta/build/dist/usr/lib/systemd/system/congfs-meta@.service \
	${RPM_BUILD_ROOT}/usr/lib/systemd/system/congfs-meta@.service

install -D meta/build/dist/sbin/congfs-setup-meta \
	${RPM_BUILD_ROOT}/opt/congfs/sbin/congfs-setup-meta

install -D meta/build/dist/etc/default/congfs-meta ${RPM_BUILD_ROOT}/etc/default/congfs-meta

##########
########## mgmtd extra files
##########

cp -a mgmtd/build/dist/etc/*.conf ${RPM_BUILD_ROOT}/etc/congfs/

# we use the redhat script for all rpm distros, as we now provide our own
# daemon() and killproc() function library (derived from redhat)
install -D mgmtd/build/dist/etc/init.d/congfs-mgmtd.init \
   ${RPM_BUILD_ROOT}/etc/init.d/congfs-mgmtd

#add the genric part of the init script from the common package
cat common_package/build/dist/etc/init.d/congfs-service.init >> ${RPM_BUILD_ROOT}/etc/init.d/congfs-mgmtd

#install systemd unit description
install -D -m644 mgmtd/build/dist/usr/lib/systemd/system/congfs-mgmtd.service \
	${RPM_BUILD_ROOT}/usr/lib/systemd/system/congfs-mgmtd.service
install -D -m644 mgmtd/build/dist/usr/lib/systemd/system/congfs-mgmtd@.service \
	${RPM_BUILD_ROOT}/usr/lib/systemd/system/congfs-mgmtd@.service

install -D mgmtd/build/dist/sbin/congfs-setup-mgmtd \
	${RPM_BUILD_ROOT}/opt/congfs/sbin/congfs-setup-mgmtd

install -D mgmtd/build/dist/etc/default/congfs-mgmtd ${RPM_BUILD_ROOT}/etc/default/congfs-mgmtd

##########
########## storage extra files
##########

cp -a storage/build/dist/etc/*.conf ${RPM_BUILD_ROOT}/etc/congfs/
mkdir -p ${RPM_BUILD_ROOT}/etc/init.d/

# we use the redhat script for all rpm distros, as we now provide our own
# daemon() and killproc() function library (derived from redhat)
install -D storage/build/dist/etc/init.d/congfs-storage.init \
   ${RPM_BUILD_ROOT}/etc/init.d/congfs-storage

#add the genric part of the init script from the common package
cat common_package/build/dist/etc/init.d/congfs-service.init >> ${RPM_BUILD_ROOT}/etc/init.d/congfs-storage

#install systemd unit description
install -D -m644 storage/build/dist/usr/lib/systemd/system/congfs-storage.service \
	${RPM_BUILD_ROOT}/usr/lib/systemd/system/congfs-storage.service
install -D -m644 storage/build/dist/usr/lib/systemd/system/congfs-storage@.service \
	${RPM_BUILD_ROOT}/usr/lib/systemd/system/congfs-storage@.service

install -D storage/build/dist/sbin/congfs-setup-storage \
	${RPM_BUILD_ROOT}/opt/congfs/sbin/congfs-setup-storage

install -D storage/build/dist/etc/default/congfs-storage ${RPM_BUILD_ROOT}/etc/default/congfs-storage

##########
########## helperd extra files
##########

cp -a helperd/build/dist/etc/*.conf ${RPM_BUILD_ROOT}/etc/congfs/

# we use the redhat script for all rpm distros, as we now provide our own
# daemon() and killproc() function library (derived from redhat)
install -D helperd/build/dist/etc/init.d/congfs-helperd.init \
   ${RPM_BUILD_ROOT}/etc/init.d/congfs-helperd

#add the genric part of the init script from the common package
cat common_package/build/dist/etc/init.d/congfs-service.init >> ${RPM_BUILD_ROOT}/etc/init.d/congfs-helperd

#install systemd unit description
install -D -m644 helperd/build/dist/usr/lib/systemd/system/congfs-helperd.service \
	${RPM_BUILD_ROOT}/usr/lib/systemd/system/congfs-helperd.service
install -D -m644 helperd/build/dist/usr/lib/systemd/system/congfs-helperd@.service \
	${RPM_BUILD_ROOT}/usr/lib/systemd/system/congfs-helperd@.service

install -D helperd/build/dist/etc/default/congfs-helperd ${RPM_BUILD_ROOT}/etc/default/congfs-helperd

##########
########## mon extra files
##########

cp -a mon/build/dist/etc/*.conf ${RPM_BUILD_ROOT}/etc/congfs/

# we use the redhat script for all rpm distros, as we now provide our own
# daemon() and killproc() function library (derived from redhat)
install -D mon/build/dist/etc/init.d/congfs-mon.init \
   ${RPM_BUILD_ROOT}/etc/init.d/congfs-mon

#add the genric part of the init script from the common package
cat common_package/build/dist/etc/init.d/congfs-service.init >> ${RPM_BUILD_ROOT}/etc/init.d/congfs-mon

#install systemd unit description
install -D -m644 mon/build/dist/usr/lib/systemd/system/congfs-mon.service \
	${RPM_BUILD_ROOT}/usr/lib/systemd/system/congfs-mon.service
install -D -m644 mon/build/dist/usr/lib/systemd/system/congfs-mon@.service \
	${RPM_BUILD_ROOT}/usr/lib/systemd/system/congfs-mon@.service

install -D mon/build/dist/etc/default/congfs-mon ${RPM_BUILD_ROOT}/etc/default/congfs-mon
install -D mon/scripts/grafana/* ${RPM_BUILD_ROOT}/opt/congfs/scripts/grafana

##########
########## utils
##########

cp -a utils/scripts/fsck.congfs ${RPM_BUILD_ROOT}/sbin/

ln -s /opt/congfs/sbin/congfs-ctl ${RPM_BUILD_ROOT}/usr/bin/congfs-ctl
ln -s /opt/congfs/sbin/congfs-fsck ${RPM_BUILD_ROOT}/usr/bin/congfs-fsck

cp -a utils/scripts/congfs-* ${RPM_BUILD_ROOT}/usr/bin/
cp utils/build/libjcongfs.so utils/build/jcongfs.jar \
   ${RPM_BUILD_ROOT}/opt/congfs/lib/
cp -a utils/scripts/etc/bash_completion.d/congfs-ctl \
   ${RPM_BUILD_ROOT}/etc/bash_completion.d/

##########
########## utils-devel
##########

cp -a event_listener/include/* ${RPM_BUILD_ROOT}/usr/include/
cp -a event_listener/build/Makefile \
   ${RPM_BUILD_ROOT}/usr/share/doc/congfs-utils-devel/examples/congfs-event-listener/build/
cp -a event_listener/source/congfs-event-listener.cpp \
   ${RPM_BUILD_ROOT}/usr/share/doc/congfs-utils-devel/examples/congfs-event-listener/source/

##########
########## client
##########

make -C client_module/build %make_j \
   RELEASE_PATH=${RPM_BUILD_ROOT}/opt/congfs/src/client KDIR="%{KDIR}" V=1 \
   prepare_release
cp client_module/build/dist/etc/*.conf ${RPM_BUILD_ROOT}/etc/congfs/
cp client_module/build/dist/etc/congfs-client-build.mk ${RPM_BUILD_ROOT}/etc/congfs/congfs-client-build.mk


# compat files
cp -a ${RPM_BUILD_ROOT}/%{CLIENT_DIR} ${RPM_BUILD_ROOT}/%{CLIENT_COMPAT_DIR}

echo congfs-%{CONGFS_MAJOR_VERSION} | tr -d . > ${RPM_BUILD_ROOT}/%{CLIENT_COMPAT_DIR}/build/congfs.fstype

# we use the redhat script for all rpm distros, as we now provide our own
# daemon() and killproc() function library (derived from redhat)
install -D client_module/build/dist/etc/init.d/congfs-client.init ${RPM_BUILD_ROOT}/etc/init.d/congfs-client

#install systemd unit description
install -D -m644 client_module/build/dist/usr/lib/systemd/system/congfs-client.service \
   ${RPM_BUILD_ROOT}/usr/lib/systemd/system/congfs-client.service

install -D -m644 client_module/build/dist/usr/lib/systemd/system/congfs-client@.service \
   ${RPM_BUILD_ROOT}/usr/lib/systemd/system/congfs-client@.service


install -D client_module/build/dist/etc/default/congfs-client ${RPM_BUILD_ROOT}/etc/default/congfs-client

install -D client_module/scripts/etc/congfs/lib/init-multi-mode.congfs-client \
   ${RPM_BUILD_ROOT}/etc/congfs/lib/init-multi-mode.congfs-client

install -D client_module/build/dist/sbin/congfs-setup-client \
   ${RPM_BUILD_ROOT}/opt/congfs/sbin/congfs-setup-client

install -D client_module/build/dist/etc/congfs-client-mount-hook.example \
   ${RPM_BUILD_ROOT}/etc/congfs/congfs-client-mount-hook.example

##########
########## client-dkms
##########

cp client_module/build/dist/etc/*.conf ${RPM_BUILD_ROOT}/etc/congfs/

mkdir -p ${RPM_BUILD_ROOT}/usr/src/congfs-%{VER}

cp -r client_module/build ${RPM_BUILD_ROOT}/usr/src/congfs-%{VER}
cp -r client_module/source ${RPM_BUILD_ROOT}/usr/src/congfs-%{VER}

rm -Rf ${RPM_BUILD_ROOT}/usr/src/congfs-%{VER}/build/dist


install -D client_module/build/dist/sbin/congfs-setup-client \
   ${RPM_BUILD_ROOT}/opt/congfs/sbin/congfs-setup-client

sed -e 's/__VERSION__/%{VER}/g' -e 's/__NAME__/congfs/g' -e 's/__MODNAME__/congfs/g' \
	 < client_module/dkms.conf.in \
	 > ${RPM_BUILD_ROOT}/usr/src/congfs-%{VER}/dkms.conf

##########
########## client-devel
##########

cp -a client_devel/include/congfs \
   ${RPM_BUILD_ROOT}/usr/include/
cp -a client_devel/build/dist/usr/share/doc/congfs-client-devel/examples/* \
   ${RPM_BUILD_ROOT}/usr/share/doc/congfs-client-devel/examples/

##########
########## conond
##########

install -D conond/source/conond ${RPM_BUILD_ROOT}/opt/congfs/sbin/conond
install -D conond/source/conond-cp ${RPM_BUILD_ROOT}/opt/congfs/sbin/conond-cp
cp conond/scripts/lib/* ${RPM_BUILD_ROOT}/opt/congfs/lib/
ln -s /opt/congfs/sbin/conond ${RPM_BUILD_ROOT}/usr/bin/conond
ln -s /opt/congfs/sbin/conond-cp ${RPM_BUILD_ROOT}/usr/bin/conond-cp

# disabled, doesn't build
###########
########### conond-thirdparty
###########
#
#install -D conond_thirdparty/build/pcopy/pcp.bin \
#   ${RPM_BUILD_ROOT}/opt/congfs/thirdparty/pcopy
#install -D conond_thirdparty/build/pcopy/pcp_cleanup \
#   ${RPM_BUILD_ROOT}/opt/congfs/thirdparty/pcopy
#install -D conond_thirdparty/build/pcopy/pcp_run \
#   ${RPM_BUILD_ROOT}/opt/congfs/thirdparty/pcopy
#install -D conond_thirdparty/build/pcopy/ssh.spawner \
#   ${RPM_BUILD_ROOT}/opt/congfs/thirdparty/pcopy
#cp conond_thirdparty/build/pcopy/README.txt \
#   ${RPM_BUILD_ROOT}/opt/congfs/thirdparty/pcopy/

##########
########## conond-thirdparty-gpl
##########

install -D conond_thirdparty_gpl/build/parallel \
   ${RPM_BUILD_ROOT}/opt/congfs/thirdparty/parallel/
cp conond_thirdparty_gpl/build/COPYING \
   ${RPM_BUILD_ROOT}/opt/congfs/thirdparty/parallel/



%package common

Summary: ConGFS common files
Group: Software/Other
BuildArch: noarch

%description common
The package contains files required by all ConGFS daemons

%files common
%defattr(-,root,root)
%dir /etc/congfs/lib/
/etc/congfs/lib/init-multi-mode
/etc/congfs/lib/start-stop-functions



%package -n libcongfs-ib

Summary: ConGFS InfiniBand support
Group: Software/Other
Buildrequires: librdmacm-devel, libibverbs-devel

%description -n libcongfs-ib
This package contains support libraries for InfiniBand.

%files -n libcongfs-ib
/opt/congfs/lib/libcongfs_ib.so



%package meta

Summary: ConGFS meta server daemon
Group: Software/Other
requires: congfs-common = %{FULL_VERSION}

%description meta
This package contains the ConGFS meta server binaries.

%post meta
%post_package congfs-meta

%preun meta
%preun_package congfs-meta

%files meta
%defattr(-,root,root)
%config(noreplace) /etc/congfs/congfs-meta.conf
%config(noreplace) /etc/default/congfs-meta
/etc/init.d/congfs-meta
/opt/congfs/sbin/congfs-meta
/opt/congfs/sbin/congfs-setup-meta
/usr/lib/systemd/system/congfs-meta.service
/usr/lib/systemd/system/congfs-meta@.service



%package mgmtd

Summary: ConGFS management daemon
Group: Software/Other
requires: congfs-common = %{FULL_VERSION}

%description mgmtd
The package contains the ConGFS management daemon.

%post mgmtd
%post_package congfs-mgmtd

%preun mgmtd
%preun_package congfs-mgmtd

%files mgmtd
%defattr(-,root,root)
%config(noreplace) /etc/congfs/congfs-mgmtd.conf
%config(noreplace) /etc/default/congfs-mgmtd
/etc/init.d/congfs-mgmtd
/opt/congfs/sbin/congfs-mgmtd
/opt/congfs/sbin/congfs-setup-mgmtd
/usr/lib/systemd/system/congfs-mgmtd.service
/usr/lib/systemd/system/congfs-mgmtd@.service



%package storage

Summary: ConGFS storage server daemon
Group: Software/Other
requires: congfs-common = %{FULL_VERSION}

%description storage
This package contains the ConGFS storage server binaries.

%post storage
%post_package congfs-storage

%preun storage
%preun_package congfs-storage

%files storage
%defattr(-,root,root)
%config(noreplace) /etc/congfs/congfs-storage.conf
%config(noreplace) /etc/default/congfs-storage
/etc/init.d/congfs-storage
/opt/congfs/sbin/congfs-storage
/opt/congfs/sbin/congfs-setup-storage
/usr/lib/systemd/system/congfs-storage.service
/usr/lib/systemd/system/congfs-storage@.service



%package helperd

Summary: ConGFS client helper daemon
Group: Software/Other
requires: congfs-common = %{FULL_VERSION}

%description helperd
The package contains the ConGFS helper daemon.

%post helperd
%post_package congfs-helperd

%preun helperd
%preun_package congfs-helperd

%files helperd
%defattr(-,root,root)
%config(noreplace) /etc/congfs/congfs-helperd.conf
%config(noreplace) /etc/default/congfs-helperd
/etc/init.d/congfs-helperd
/opt/congfs/sbin/congfs-helperd
/usr/lib/systemd/system/congfs-helperd.service
/usr/lib/systemd/system/congfs-helperd@.service



%package mon

Summary: ConGFS mon server daemon
Group: Software/Other
requires: congfs-common = %{FULL_VERSION}

%description mon
This package contains the ConGFS mon server binaries.

%post mon
%post_package congfs-mon

%preun mon
%preun_package congfs-mon

%files mon
%defattr(-,root,root)
%config(noreplace) /etc/congfs/congfs-mon.conf
%config(noreplace) /etc/default/congfs-mon
/etc/init.d/congfs-mon
/opt/congfs/sbin/congfs-mon
/usr/lib/systemd/system/congfs-mon.service
/usr/lib/systemd/system/congfs-mon@.service



%package mon-grafana

Summary: ConGFS mon dashboards for Grafana
Group: Software/Other
BuildArch: noarch

%description mon-grafana
This package contains the ConGFS mon dashboards to display monitoring data in Grafana.

The default dashboard setup requires both Grafana, and InfluxDB.

%post mon-grafana
%post_package congfs-mon-grafana

%preun mon-grafana
%preun_package congfs-mon-grafana

%files mon-grafana
%defattr(-,root,root)
/opt/congfs/scripts/grafana/



%package utils

Summary: ConGFS utilities
Group: Software/Other
requires: congfs-common = %{FULL_VERSION}

%description utils
This package contains ConGFS utilities.

%files utils
%defattr(-,root,root)
%attr(0755, root, root) /opt/congfs/sbin/congfs-fsck
%attr(4755, root, root) /opt/congfs/sbin/congfs-ctl
/opt/congfs/lib/jcongfs.jar
/opt/congfs/lib/libjcongfs.so
/usr/bin/congfs-check-servers
/usr/bin/congfs-ctl
/usr/bin/congfs-df
/usr/bin/congfs-fsck
/usr/bin/congfs-net
/etc/bash_completion.d/congfs-ctl
/sbin/fsck.congfs
/opt/congfs/sbin/congfs-event-listener



%package utils-devel

Summary: ConGFS utils devel files
Group: Software/Other
BuildArch: noarch

%description utils-devel
This package contains ConGFS utils development files and examples.

%files utils-devel
%defattr(-,root,root)
/usr/include/congfs/congfs_file_event_log.hpp
/usr/share/doc/congfs-utils-devel/examples/congfs-event-listener/*



%package client

Summary: ConGFS client kernel module
License: GPL v2
Group: Software/Other
BuildArch: noarch
requires: make, gcc, gcc-c++
conflicts: congfs-client-dkms

%description client
This package contains scripts, config and source files to build and
start congfs-client.

%post client
%post_package congfs-client

# make the script to run autobuild
mkdir -p /var/lib/congfs/client
touch /var/lib/congfs/client/force-auto-build

%preun client
%preun_package congfs-client

%files client
%defattr(-,root,root)
%config(noreplace) /etc/congfs/congfs-client-autobuild.conf
%config(noreplace) /etc/congfs/congfs-client-mount-hook.example
%config(noreplace) /etc/congfs/congfs-client.conf
%config(noreplace) /etc/congfs/congfs-client-build.mk
%config(noreplace) /etc/congfs/congfs-mounts.conf
%dir /etc/congfs/lib/
%config(noreplace) /etc/congfs/lib/init-multi-mode.congfs-client
%config(noreplace) /etc/default/congfs-client
/etc/init.d/congfs-client
/opt/congfs/sbin/congfs-setup-client
/usr/lib/systemd/system/congfs-client.service
/usr/lib/systemd/system/congfs-client@.service
%{CLIENT_DIR}



%package client-dkms

Summary: ConGFS client kernel module (DKMS version)
License: GPL v2
Group: Software/Other
BuildArch: noarch
requires: make, dkms
conflicts: congfs-client
provides: congfs-client

%description client-dkms
This package contains scripts, config and source files to build and
start congfs-client. It uses DKMS to build the kernel module.

%post client-dkms
dkms install congfs/%{VER}

%preun client-dkms
dkms remove congfs/%{VER} --all

%files client-dkms
%defattr(-,root,root)
%config(noreplace) /etc/congfs/congfs-client.conf
/usr/src/congfs-%{VER}



%package client-compat

Summary: ConGFS client compat module, allows to run two different client versions.
License: GPL v2
Group: Software/Other
requires: make, gcc, gcc-c++
BuildArch: noarch

%description client-compat
This package allows to build and to run a compatbility congfs-client kernel module
on a system that has a newer congfs-client version installed.

%files client-compat
%defattr(-,root,root)
%{CLIENT_COMPAT_DIR}



%package client-devel

Summary: ConGFS client devel files
Group: Software/Other
BuildArch: noarch

%description client-devel
This package contains ConGFS client development files.

%files client-devel
%defattr(-,root,root)
%dir /usr/include/congfs
/usr/include/congfs/congfs.h
/usr/include/congfs/congfs_ioctl.h
/usr/include/congfs/congfs_ioctl_functions.h
/usr/share/doc/congfs-client-devel/examples/createFileWithStripePattern.cpp
/usr/share/doc/congfs-client-devel/examples/getStripePatternOfFile.cpp



%package -n conond

Summary: BeeOND
Group: Software/Other
requires: conond-thirdparty-gpl = %{FULL_VERSION}, congfs-utils = %{FULL_VERSION}, congfs-mgmtd = %{FULL_VERSION}, congfs-meta = %{FULL_VERSION}, congfs-storage = %{FULL_VERSION}, congfs-client = %{FULL_VERSION}, congfs-helperd = %{FULL_VERSION}, psmisc

%description -n conond
This package contains BeeOND.

%files -n conond
%defattr(-,root,root)
/opt/congfs/sbin/conond
/usr/bin/conond
/opt/congfs/sbin/conond-cp
/usr/bin/conond-cp
/opt/congfs/lib/conond-lib
/opt/congfs/lib/congfs-ondemand-stoplocal



## disabled, doesn't build
#%package -n conond-thirdparty
#
#Summary: BeeOND Thirdparty
#Group: Software/Other
#
#%description -n conond-thirdparty
#This package contains thirdparty software needed to run BeeOND.
#
#%files -n conond-thirdparty
#%defattr(-,root,root)
#/opt/congfs/thirdparty/pcopy/*



%package -n conond-thirdparty-gpl

Summary: BeeOND Thirdparty GPL
Group: Software/Other

%description -n conond-thirdparty-gpl
This package contains thirdparty software (licensed under GPL) needed to run BeeOND.

%files -n conond-thirdparty-gpl
%defattr(-,root,root)
/opt/congfs/thirdparty/parallel/parallel
/opt/congfs/thirdparty/parallel/COPYING
