%global  _hardened_build     1
%global  nginx_user          nginx

Name:              nginx
Version:           1.10.3
Release:           1%{?dist}

Summary:           A high performance web server and reverse proxy server
Group:             System Environment/Daemons
# BSD License (two clause)
# http://www.freebsd.org/copyright/freebsd-license.html
License:           BSD
URL:               http://nginx.org/
%if 0%{?rhel} == 5
BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%endif

Source0:           http://nginx.org/download/nginx-%{version}.tar.gz
Source1:           http://nginx.org/download/nginx-%{version}.tar.gz.asc
Source10:          nginx.init
Source11:          nginx.logrotate
Source12:          nginx.conf
Source13:          default.conf
Source14:          ssl.conf
Source15:          virtual.conf
Source16:          nginx.sysconfig
Source100:         index.html
Source101:         poweredby.png
Source102:         nginx-logo.png
Source103:         404.html
Source104:         50x.html
Source200:         README.dynamic
Source210:         UPGRADE-NOTES-0.8-to-1.10
Source211:         UPGRADE-NOTES-1.0-to-1.10

# removes -Werror in upstream build scripts.  -Werror conflicts with
# -D_FORTIFY_SOURCE=2 causing warnings to turn into errors.
Patch0:            nginx-auto-cc-gcc.patch

BuildRequires:     openssl-devel
BuildRequires:     pcre-devel
BuildRequires:     zlib-devel

Requires:          nginx-filesystem = %{version}-%{release}
# Introduced at 1.10.1-1 to ease upgrade path. To be removed later.
Requires:          nginx-all-modules = %{version}-%{release}

Requires:          openssl
Requires:          pcre
Requires(pre):     nginx-filesystem
Requires(post):    chkconfig
Requires(preun):   chkconfig, initscripts
Requires(postun):  initscripts
Provides:          webserver

%description
Nginx is a web server and a reverse proxy server for HTTP, SMTP, POP3 and
IMAP protocols, with a strong focus on high concurrency, performance and low
memory usage.

%package all-modules
Group:             System Environment/Daemons
Summary:           A meta package that installs all available Nginx modules
%if 0%{?rhel} > 5
BuildArch:         noarch
%endif

Requires:          nginx-mod-http-geoip = %{version}-%{release}
Requires:          nginx-mod-http-image-filter = %{version}-%{release}
Requires:          nginx-mod-http-perl = %{version}-%{release}
Requires:          nginx-mod-http-xslt-filter = %{version}-%{release}
Requires:          nginx-mod-mail = %{version}-%{release}
Requires:          nginx-mod-stream = %{version}-%{release}

%description all-modules
%{summary}.
The main nginx package depends on this to ease the upgrade path. After a grace
period of several months, modules will become optional.

%package filesystem
Group:             System Environment/Daemons
Summary:           The basic directory layout for the Nginx server
%if 0%{?rhel} > 5
BuildArch:         noarch
%endif
Requires(pre):     shadow-utils

%description filesystem
The nginx-filesystem package contains the basic directory layout
for the Nginx server including the correct permissions for the
directories.

%package mod-http-geoip
Group:             System Environment/Daemons
Summary:           Nginx HTTP geoip module
BuildRequires:     GeoIP-devel
Requires:          nginx
Requires:          GeoIP

%description mod-http-geoip
%{summary}.

%package mod-http-image-filter
Group:             System Environment/Daemons
Summary:           Nginx HTTP image filter module
BuildRequires:     gd-devel
Requires:          nginx
Requires:          gd

%description mod-http-image-filter
%{summary}.

%package mod-http-perl
Group:             System Environment/Daemons
Summary:           Nginx HTTP perl module
%if 0%{?rhel} > 5
BuildRequires:     perl-devel
%endif
BuildRequires:     perl(ExtUtils::Embed)
Requires:          nginx
Requires:          perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

%description mod-http-perl
%{summary}.

%package mod-http-xslt-filter
Group:             System Environment/Daemons
Summary:           Nginx XSLT module
BuildRequires:     libxslt-devel
Requires:          nginx

%description mod-http-xslt-filter
%{summary}.

%package mod-mail
Group:             System Environment/Daemons
Summary:           Nginx mail modules
Requires:          nginx

%description mod-mail
%{summary}.

%package mod-stream
Group:             System Environment/Daemons
Summary:           Nginx stream modules
Requires:          nginx

%description mod-stream
%{summary}.


%prep
%setup -q
%patch0 -p0
cp %{SOURCE200} .
cp %{SOURCE210} .
cp %{SOURCE211} .

%if 0%{?rhel} < 6
# OpenSSL on RHEL 5 is too old for HTTP/2 support.
sed -i -e 's/http2 //g' %{SOURCE14}
%endif

%build
# nginx does not utilize a standard configure script.  It has its own
# and the standard configure options cause the nginx configure script
# to error out.  This is is also the reason for the DESTDIR environment
# variable.
export DESTDIR=%{buildroot}
./configure \
    --prefix=%{_datadir}/nginx \
    --sbin-path=%{_sbindir}/nginx \
    --modules-path=%{_libdir}/nginx/modules \
    --conf-path=%{_sysconfdir}/nginx/nginx.conf \
    --error-log-path=%{_localstatedir}/log/nginx/error.log \
    --http-log-path=%{_localstatedir}/log/nginx/access.log \
    --http-client-body-temp-path=%{_localstatedir}/lib/nginx/tmp/client_body \
    --http-proxy-temp-path=%{_localstatedir}/lib/nginx/tmp/proxy \
    --http-fastcgi-temp-path=%{_localstatedir}/lib/nginx/tmp/fastcgi \
    --http-uwsgi-temp-path=%{_localstatedir}/lib/nginx/tmp/uwsgi \
    --http-scgi-temp-path=%{_localstatedir}/lib/nginx/tmp/scgi \
    --pid-path=%{_localstatedir}/run/nginx.pid \
    --lock-path=%{_localstatedir}/lock/subsys/nginx \
    --user=%{nginx_user} \
    --group=%{nginx_user} \
    --with-file-aio \
    --with-ipv6 \
    --with-http_ssl_module \
    --with-http_v2_module \
    --with-http_realip_module \
    --with-http_addition_module \
    --with-http_xslt_module=dynamic \
    --with-http_image_filter_module=dynamic \
    --with-http_geoip_module=dynamic \
    --with-http_sub_module \
    --with-http_dav_module \
    --with-http_flv_module \
    --with-http_mp4_module \
    --with-http_gunzip_module \
    --with-http_gzip_static_module \
    --with-http_random_index_module \
    --with-http_secure_link_module \
    --with-http_degradation_module \
    --with-http_slice_module \
    --with-http_stub_status_module \
    --with-http_perl_module=dynamic \
    --with-mail=dynamic \
    --with-mail_ssl_module \
    --with-pcre \
    --with-pcre-jit \
    --with-stream=dynamic \
    --with-stream_ssl_module \
    --with-debug \
    --with-cc-opt="%{optflags} $(pcre-config --cflags)" \
    --with-ld-opt="$RPM_LD_FLAGS -Wl,-E" # so the perl module finds its symbols

make %{?_smp_mflags}


%install
make install DESTDIR=%{buildroot} INSTALLDIRS=vendor

find %{buildroot} -type f -name .packlist -exec rm -f '{}' \;
find %{buildroot} -type f -name perllocal.pod -exec rm -f '{}' \;
find %{buildroot} -type f -empty -exec rm -f '{}' \;
find %{buildroot} -type f -iname '*.so' -exec chmod 0755 '{}' \;

install -p -D -m 0755 %{SOURCE10} \
    %{buildroot}%{_initrddir}/nginx
install -p -D -m 0644 %{SOURCE11} \
    %{buildroot}%{_sysconfdir}/logrotate.d/nginx
install -p -D -m 0644 %{SOURCE16} \
    %{buildroot}%{_sysconfdir}/sysconfig/nginx

install -p -d -m 0755 %{buildroot}%{_sysconfdir}/nginx/conf.d
install -p -d -m 0755 %{buildroot}%{_sysconfdir}/nginx/default.d

install -p -d -m 0700 %{buildroot}%{_localstatedir}/lib/nginx
install -p -d -m 0700 %{buildroot}%{_localstatedir}/lib/nginx/tmp
install -p -d -m 0700 %{buildroot}%{_localstatedir}/log/nginx

install -p -d -m 0755 %{buildroot}%{_datadir}/nginx/html
install -p -d -m 0755 %{buildroot}%{_datadir}/nginx/modules
install -p -d -m 0755 %{buildroot}%{_libdir}/nginx/modules

install -p -m 0644 %{SOURCE12} \
    %{buildroot}%{_sysconfdir}/nginx
install -p -m 0644 %{SOURCE13} %{SOURCE14} %{SOURCE15} \
    %{buildroot}%{_sysconfdir}/nginx/conf.d
install -p -m 0644 %{SOURCE100} \
    %{buildroot}%{_datadir}/nginx/html
install -p -m 0644 %{SOURCE101} %{SOURCE102} \
    %{buildroot}%{_datadir}/nginx/html
install -p -m 0644 %{SOURCE103} %{SOURCE104} \
    %{buildroot}%{_datadir}/nginx/html

install -p -D -m 0644 %{_builddir}/nginx-%{version}/man/nginx.8 \
    %{buildroot}%{_mandir}/man8/nginx.8

for i in ftdetect indent syntax; do
    install -p -D -m644 contrib/vim/${i}/nginx.vim \
        %{buildroot}%{_datadir}/vim/vimfiles/${i}/nginx.vim
done

echo 'load_module "%{_libdir}/nginx/modules/ngx_http_geoip_module.so";' \
    > %{buildroot}%{_datadir}/nginx/modules/mod-http-geoip.conf
echo 'load_module "%{_libdir}/nginx/modules/ngx_http_image_filter_module.so";' \
    > %{buildroot}%{_datadir}/nginx/modules/mod-http-image-filter.conf
echo 'load_module "%{_libdir}/nginx/modules/ngx_http_perl_module.so";' \
    > %{buildroot}%{_datadir}/nginx/modules/mod-http-perl.conf
echo 'load_module "%{_libdir}/nginx/modules/ngx_http_xslt_filter_module.so";' \
    > %{buildroot}%{_datadir}/nginx/modules/mod-http-xslt-filter.conf
echo 'load_module "%{_libdir}/nginx/modules/ngx_mail_module.so";' \
    > %{buildroot}%{_datadir}/nginx/modules/mod-mail.conf
echo 'load_module "%{_libdir}/nginx/modules/ngx_stream_module.so";' \
    > %{buildroot}%{_datadir}/nginx/modules/mod-stream.conf

%pre filesystem
getent group %{nginx_user} > /dev/null || groupadd -r %{nginx_user}
getent passwd %{nginx_user} > /dev/null || \
    useradd -r -d %{_localstatedir}/lib/nginx -g %{nginx_user} \
    -s /sbin/nologin -c "Nginx web server" %{nginx_user}
exit 0

%post
if [ $1 -eq 1 ]; then
    /sbin/chkconfig --add %{name}
fi
if [ $1 -eq 2 ]; then
    # Make sure these directories are not world readable.
    chmod 700 %{_localstatedir}/lib/nginx
    chmod 700 %{_localstatedir}/lib/nginx/tmp
    chmod 700 %{_localstatedir}/log/nginx
fi

%preun
if [ $1 -eq 0 ]; then
    /sbin/service %{name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name}
fi

%postun
if [ $1 -eq 2 ]; then
    /sbin/service %{name} upgrade || :
fi

%files
%doc LICENSE CHANGES README README.dynamic
%if 0%{?rhel} == 5
%doc UPGRADE-NOTES-0.8-to-1.10
%else
%doc UPGRADE-NOTES-1.0-to-1.10
%endif
%{_datadir}/nginx/html/*
%{_sbindir}/nginx
%{_datadir}/vim/vimfiles/ftdetect/nginx.vim
%{_datadir}/vim/vimfiles/syntax/nginx.vim
%{_datadir}/vim/vimfiles/indent/nginx.vim
%{_mandir}/man3/nginx.3pm*
%{_mandir}/man8/nginx.8*
%config(noreplace) %{_sysconfdir}/sysconfig/nginx
%{_initrddir}/nginx
%config(noreplace) %{_sysconfdir}/nginx/fastcgi.conf
%config(noreplace) %{_sysconfdir}/nginx/fastcgi.conf.default
%config(noreplace) %{_sysconfdir}/nginx/fastcgi_params
%config(noreplace) %{_sysconfdir}/nginx/fastcgi_params.default
%config(noreplace) %{_sysconfdir}/nginx/koi-utf
%config(noreplace) %{_sysconfdir}/nginx/koi-win
%config(noreplace) %{_sysconfdir}/nginx/mime.types
%config(noreplace) %{_sysconfdir}/nginx/mime.types.default
%config(noreplace) %{_sysconfdir}/nginx/nginx.conf
%config(noreplace) %{_sysconfdir}/nginx/nginx.conf.default
%config(noreplace) %{_sysconfdir}/nginx/scgi_params
%config(noreplace) %{_sysconfdir}/nginx/scgi_params.default
%config(noreplace) %{_sysconfdir}/nginx/uwsgi_params
%config(noreplace) %{_sysconfdir}/nginx/uwsgi_params.default
%config(noreplace) %{_sysconfdir}/nginx/win-utf
%config(noreplace) %{_sysconfdir}/nginx/conf.d/*.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/nginx
%attr(700,%{nginx_user},%{nginx_user}) %dir %{_localstatedir}/lib/nginx
%attr(700,%{nginx_user},%{nginx_user}) %dir %{_localstatedir}/lib/nginx/tmp
%attr(700,%{nginx_user},%{nginx_user}) %dir %{_localstatedir}/log/nginx
%dir %{_libdir}/nginx/modules

%files all-modules

%files filesystem
%dir %{_datadir}/nginx
%dir %{_datadir}/nginx/html
%dir %{_sysconfdir}/nginx
%dir %{_sysconfdir}/nginx/conf.d
%dir %{_sysconfdir}/nginx/default.d

%files mod-http-geoip
%{_datadir}/nginx/modules/mod-http-geoip.conf
%{_libdir}/nginx/modules/ngx_http_geoip_module.so

%files mod-http-image-filter
%{_datadir}/nginx/modules/mod-http-image-filter.conf
%{_libdir}/nginx/modules/ngx_http_image_filter_module.so

%files mod-http-perl
%{_datadir}/nginx/modules/mod-http-perl.conf
%{_libdir}/nginx/modules/ngx_http_perl_module.so
%dir %{perl_vendorarch}/auto/nginx
%{perl_vendorarch}/nginx.pm
%{perl_vendorarch}/auto/nginx/nginx.so

%files mod-http-xslt-filter
%{_datadir}/nginx/modules/mod-http-xslt-filter.conf
%{_libdir}/nginx/modules/ngx_http_xslt_filter_module.so

%files mod-mail
%{_datadir}/nginx/modules/mod-mail.conf
%{_libdir}/nginx/modules/ngx_mail_module.so

%files mod-stream
%{_datadir}/nginx/modules/mod-stream.conf
%{_libdir}/nginx/modules/ngx_stream_module.so


%changelog
* Tue May 07 2019 Jamie Nguyen <jamielinux@fedoraproject.org> - 1.10.3-1
- Update to upstream release 1.10.3

* Mon Oct 31 2016 Jamie Nguyen <jamielinux@fedoraproject.org> - 1.10.2-1
- update to upstream release 1.10.2

* Sat Jul 02 2016 Jamie Nguyen <jamielinux@fedoraproject.org> - 1.10.1-1
- update to upstream release 1.10.1
- split dynamic modules into subpackages
- spec file cleanup

* Tue Jun 16 2015 Jamie Nguyen <jamielinux@fedoraproject.org> - 1.0.15-12
- fix path to png images in error pages (#1232277)
- optimize png images with optipng

* Tue Nov 11 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1.0.15-11
- fix CVE-2013-4547 security bypass due to whitespace parsing
  (#1032266, #1032270)

* Wed Oct 22 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1.0.15-10
- add vim files (#1142849)

* Wed Oct 22 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1.0.15-9
- use default.d directory

* Wed Oct 08 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1.0.15-8
- fix typo in Requires

* Mon Sep 22 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1.0.15-7
- create nginx-filesystem subpackage (patch from Remi Collet)

* Mon Sep 22 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1.0.15-6
- fix CVE-2014-3616 virtual host confusion (#1142573, #1142576)

* Fri Apr 26 2013 Jamie Nguyen <jamielinux@fedoraproject.org> - 1.0.15-5
- enable debugging (#956845)
- trim changelog

* Fri Feb 22 2013 Jamie Nguyen <jamielinux@fedoraproject.org> - 1.0.15-4
- make sure nginx directories are not world readable (#913734, #913736)

* Sun Oct 28 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1.0.15-3
- add nginx man page (#870738)
- link to official documentation not the community wiki (#870733)
- default.conf: add "default_server" to the "listen" directive (#842738)

* Mon May 14 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1.0.15-2
- fix postrotate script in nginx.logrotate (#705264)

* Thu Apr 19 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1.0.15-1
- update to upstream release 1.0.15
- CVE-2012-2089 (#812093)

* Thu Mar 15 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1.0.14-1
- update to upstream release 1.0.14
- CVE-2012-1180 (#803856)

* Sun Mar 04 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1.0.13-2
- remove incorrect BR

* Sat Mar 03 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1.0.13-1
- update to upstream release 1.0.13
- general spec file cleanup to match rawhide (for easier diff), including:
- replace %%define with %%global
- amend nginx.init and nginx.conf
- amend %%pre scriptlet to match with guidelines
- remove obsolete BuildRoot tag, %%clean section and %%defattr
- remove various unnecessary commands

* Sun Feb 19 2012 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.0.12-1
- Update to 1.0.12

* Wed Dec 14 2011 Keiran "Affix" Smith <fedora@affix.me> - 1.0.10-2
- Fix Build Issue

* Thu Nov 17 2011 Keiran "Affix" Smith <fedora@affix.me> - 1.0.10-1
- Bugfix: a segmentation fault might occur in a worker process if resolver got a big DNS response. Thanks to Ben Hawkes.
- Bugfix: in cache key calculation if internal MD5 implementation wasused; the bug had appeared in 1.0.4.
- Bugfix: the module ngx_http_mp4_module sent incorrect "Content-Length" response header line if the "start" argument was used. Thanks to Piotr Sikora.

* Thu Oct 27 2011 Keiran "Affix" Smith <fedora@affix.me> - 1.0.8-1
- Update to new 1.0.8 stable release

* Fri Aug 26 2011 Keiran "Affix" Smith <fedora@affix.me> - 1.0.5-1
- Update nginx to Latest Stable Release

* Fri Jun 17 2011 Marcela Mašláňová <mmaslano@redhat.com> - 1.0.0-3
- Perl mass rebuild

* Thu Jun 09 2011 Marcela Mašláňová <mmaslano@redhat.com> - 1.0.0-2
- Perl 5.14 mass rebuild

* Wed Apr 27 2011 Jeremy Hinegardner <jeremy at hinegardner dot org> - 1.0.0-1
- Update to 1.0.0

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.53-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Dec 12 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.8.53.5
- Extract out default config into its own file (bug #635776)

* Sun Dec 12 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.8.53-4
- Revert ownership of log dir

* Sun Dec 12 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.8.53-3
- Change ownership of /var/log/nginx to be 0700 nginx:nginx
- update init script to use killproc -p
- add reopen_logs command to init script
- update init script to use nginx -q option

* Sun Oct 31 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.8.53-2
- Fix linking of perl module

* Sun Oct 31 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.8.53-1
- Update to new stable 0.8.53

* Sat Jul 31 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.7.67-2
- add Provides: webserver (bug #619693)

* Sun Jun 20 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.7.67-1
- Update to new stable 0.7.67
- fix bugzilla #591543

* Tue Jun 01 2010 Marcela Maslanova <mmaslano@redhat.com> - 0.7.65-2
- Mass rebuild with perl-5.12.0

* Mon Feb 15 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.7.65-1
- Update to new stable 0.7.65
- change ownership of logdir to root:root
- add support for ipv6 (bug #561248)
- add random_index_module
- add secure_link_module

* Fri Dec 04 2009 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.7.64-1
- Update to new stable 0.7.64
