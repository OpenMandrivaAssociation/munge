%define major	2
%define libname %mklibname %{name} %{major}
%define devname %mklibname -d %{name}

Summary:	Enables uid & gid authentication across a host cluster
Name:		munge
Version:	0.5.10
Release:	10
Group:		System/Servers
License:	GPLv2+
Url:		http://munge.googlecode.com/
Source0:	http://munge.googlecode.com/files/%{name}-%{version}.tar.bz2
Source1:	create-munge-key
Source2:	munge.logrotate
# Check the key exists in the init.d script rather than failing 
Patch1:		check-key-exists.patch
# Run as munge rather than deamon.
Patch2:		runas-munge-user.patch
Patch3:		munge_configure.ac_disable-AM_PATH_LIBGCRYPT.patch

BuildRequires:	bzip2-devel
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(zlib)
Requires(post,preun):	chkconfig
Requires(pre):	shadow-utils
Requires(preun,postun):	initscripts

%description
MUNGE (MUNGE Uid 'N' Gid Emporium) is an authentication service for creating 
and validating credentials. It is designed to be highly scalable for use 
in an HPC cluster environment. 

It allows a process to authenticate the UID and GID of another local or 
remote process within a group of hosts having common users and groups. 
These hosts form a security realm that is defined by a shared cryptographic 
key. Clients within this security realm can create and validate credentials 
without the use of root privileges, reserved ports, or platform-specific 
methods.

%package -n     %{libname}
Summary:	Runtime libs for uid * gid authentication acrosss a host cluster
Group:		System/Libraries

%description -n %{libname}
This package contains the shared libraries (*.so*) which certain languages and
applications need to dynamically load and use Munge.

%package -n %{devname}
Summary:	Development files for uid * gid authentication acrosss a host cluster
Group:		Development/Other
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description -n %{devname}
Header files for developing using MUNGE.

%prep
%setup -q
%apply_patches

%build
./bootstrap
%configure  --disable-static
# Get rid of some rpaths for /usr/sbin
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
%make

%install
%makeinstall_std

# mv init.d script form /etc/init.d to %{_initddir}
mkdir -p %{buildroot}/%{_initddir}
mv  %{buildroot}/%{_sysconfdir}/init.d/munge %{buildroot}/%{_initddir}/munge
#  
chmod 644 %{buildroot}/%{_sysconfdir}/sysconfig/munge

install -p -m 755 %{SOURCE1} %{buildroot}/%{_sbindir}/create-munge-key
install -p -D -m 644 %{SOURCE2} %{buildroot}/%{_sysconfdir}/logrotate.d/munge

# Fix a few permissions
chmod 700 %{buildroot}%{_var}/lib/munge %{buildroot}%{_var}/log/munge
chmod 700 %{buildroot}%{_sysconfdir}/munge

# Create and empty key file and pid file to be marked as a ghost file below.
# i.e it is not actually included in the rpm, only the record 
# of it is.
touch %{buildroot}%{_sysconfdir}/%{name}/%{name}.key
chmod 400 %{buildroot}%{_sysconfdir}/%{name}/%{name}.key
touch %{buildroot}%{_var}/run/%{name}/%{name}d.pid

%postun 
if [ "$1" -ge "1" ] ; then
    /sbin/service munge condrestart >/dev/null 2>&1 || :
fi

%preun
if [ $1 = 0 ]; then
    /sbin/service munge stop > /dev/null 2>&1 || :
    /sbin/chkconfig --del munge || :
fi

%pre
getent group munge >/dev/null || groupadd -r munge
getent passwd munge >/dev/null || \
useradd -r -g munge -d %{_var}/run/munge -s /sbin/nologin \
  -c "Runs Uid 'N' Gid Emporium" munge
exit 0

%post
/sbin/chkconfig --add munge || :

%files
%doc COPYING AUTHORS BUGS ChangeLog    
%doc JARGON META NEWS QUICKSTART README 
%doc doc
%{_initddir}/munge
%{_bindir}/munge
%{_bindir}/remunge
%{_bindir}/unmunge
%{_sbindir}/munged
%{_sbindir}/create-munge-key
%{_mandir}/man1/munge.1.*
%{_mandir}/man1/remunge.1.*
%{_mandir}/man1/unmunge.1.*
%{_mandir}/man7/munge.7.*
%{_mandir}/man8/munged.8.*
%attr(-,munge,munge) %ghost %dir  %{_var}/run/munge
%attr(0700,munge,munge) %dir  %{_var}/log/munge
%attr(0700,munge,munge) %dir %{_sysconfdir}/munge
%attr(0400,munge,munge) %ghost %{_sysconfdir}/%{name}/%{name}.key
%attr(-,munge,munge)    %ghost %{_var}/run/%{name}/%{name}d.pid
%attr(0700,munge,munge) %dir  %{_var}/lib/munge
%config(noreplace) %{_sysconfdir}/sysconfig/munge
%config(noreplace) %{_sysconfdir}/logrotate.d/munge

%files -n %{libname}
%{_libdir}/libmunge.so.%{major}*

%files -n %{devname}
%{_includedir}/munge.h
%{_libdir}/libmunge.so
%{_mandir}/man3/munge.3.*
%{_mandir}/man3/munge_ctx.3.*
%{_mandir}/man3/munge_ctx_copy.3.*
%{_mandir}/man3/munge_ctx_create.3.*
%{_mandir}/man3/munge_ctx_destroy.3.*
%{_mandir}/man3/munge_ctx_get.3.*
%{_mandir}/man3/munge_ctx_set.3.*
%{_mandir}/man3/munge_ctx_strerror.3.*
%{_mandir}/man3/munge_decode.3.*
%{_mandir}/man3/munge_encode.3.*
%{_mandir}/man3/munge_enum.3.*
%{_mandir}/man3/munge_enum_int_to_str.3.*
%{_mandir}/man3/munge_enum_is_valid.3.*
%{_mandir}/man3/munge_enum_str_to_int.3.*
%{_mandir}/man3/munge_strerror.3.*

