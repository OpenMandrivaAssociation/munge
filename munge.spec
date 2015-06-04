%define libname %mklibname %{name}
%define develname %mklibname -d %{name}

Name:           munge
Version:        0.5.11
Release:       	1
Summary:        Enables uid & gid authentication across a host cluster

Group:          System/Servers
License:        GPLv2+
URL:            http://munge.googlecode.com/
Source0:        http://munge.googlecode.com/files/munge-%{version}.tar.bz2
Source1:        create-munge-key
Source2:        munge.logrotate

BuildRequires:	zlib-devel
BuildRequires:	bzip2-devel
BuildRequires:	openssl-devel
Requires:       %{libname} = %{EVRD}

Requires(post):   systemd
Requires(pre):    shadow-utils
Requires(preun):  systemd
Requires(postun): systemd


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

%package -n %{develname}
Summary:        Development files for uid * gid authentication acrosss a host cluster
Group:          Development/Other
Requires:       %{libname} = %{version}-%{release}
Provides:       munge-devel = %{version}-%{release}
Provides:       %{libname}-devel = %{version}-%{release}


%description -n %{develname}
Header files for developing using MUNGE.

%package -n     %{libname}
Summary:        Runtime libs for uid * gid authentication acrosss a host cluster
Group:          System/Libraries

%description -n %{libname}
This package contains the shared libraries (*.so*) which certain languages and
applications need to dynamically load and use Munge.


%prep
%setup -q

%build
./bootstrap
%configure  --disable-static
# Get rid of some rpaths for /usr/sbin
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
%make


%install
%makeinstall_std

chmod 644 %{buildroot}/%{_sysconfdir}/sysconfig/munge

rm -rf %{buildroot}%{_initddir}

install -p -m 755 %{SOURCE1} %{buildroot}/%{_sbindir}/create-munge-key
install -p -D -m 644 %{SOURCE2} %{buildroot}/%{_sysconfdir}/logrotate.d/munge

# Fix a few permissions
chmod 700 %{buildroot}%{_var}/lib/munge %{buildroot}%{_var}/log/munge
chmod 700 %{buildroot}%{_sysconfdir}/munge

# Create and empty key file 
touch %{buildroot}%{_sysconfdir}/%{name}/%{name}.key
chmod 400 %{buildroot}%{_sysconfdir}/%{name}/%{name}.key

%postun
%systemd_postun_with_restart munge.service

%preun
%systemd_preun munge.service

%pre
getent group munge >/dev/null || groupadd -r munge
getent passwd munge >/dev/null || \
useradd -r -g munge -d %{_var}/run/munge -s /sbin/nologin \
  -c "Runs Uid 'N' Gid Emporium" munge
exit 0


%post
%tmpfiles_create munge.conf
%systemd_post munge.service

%files
%{_unitdir}/munge.service
%{_tmpfilesdir}/*
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
%attr(0700,munge,munge) %dir  %{_var}/lib/munge
%config(noreplace) %{_sysconfdir}/sysconfig/munge
%config(noreplace) %{_sysconfdir}/logrotate.d/munge
%doc AUTHORS JARGON META NEWS QUICKSTART README
%doc doc

%files -n %{libname}
%{_libdir}/libmunge.so.2
%{_libdir}/libmunge.so.2.0.0
%doc COPYING

%files -n %{develname}
%{_includedir}/munge.h
%{_libdir}/libmunge.so
%{_libdir}/pkgconfig/*
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
