%global debug_package %{nil}

Name:    storj
Version: 1.37.2
Release: 5%{?dist}
Summary: Storj is building a decentralized cloud storage network

License: AGPLv3
URL:     https://storj.io/

Source0:  https://github.com/storj/storj/archive/refs/tags/v%{version}.tar.gz

Source2: storj-storagenode.conf

Source11: storj-storagenode@.service
Source12: storj-storagenode-setup@.service

BuildRequires: go
BuildRequires: git

BuildRequires: npm
BuildRequires: unzip
BuildRequires: systemd-rpm-macros
%{?systemd_requires}

%description
Storj is an S3-compatible platform and suite of decentralized applications that
allows you to store data in a secure and decentralized manner. Your files are
encrypted, broken into little pieces and stored in a global decentralized
network of computers. Luckily, we also support allowing you (and only you) to
retrieve those files!

%package storagenode
Summary: Storj Storage Node

%description storagenode
Storj is an S3-compatible platform and suite of decentralized applications that
allows you to store data in a secure and decentralized manner. Your files are
encrypted, broken into little pieces and stored in a global decentralized
network of computers. Luckily, we also support allowing you (and only you) to
retrieve those files!

%package identity
Summary: Storj Identity

%description identity
Storj is an S3-compatible platform and suite of decentralized applications that
allows you to store data in a secure and decentralized manner. Your files are
encrypted, broken into little pieces and stored in a global decentralized
network of computers. Luckily, we also support allowing you (and only you) to
retrieve those files!


%prep
%setup -n storj-%{version}
cp %{SOURCE2} .


%build
export GOPATH="$(pwd)/.godeps"
go install -v ./cmd/...

#web console
cd web/storagenode
npm ci
npm run build

%install
install -dD -m 755 %{buildroot}%{_bindir}
install -m 755 .godeps/bin/storagenode %{buildroot}%{_bindir}/storagenode
install -m 755 .godeps/bin/identity %{buildroot}%{_bindir}/identity


install -D -p -m 0644 %{SOURCE11} %{buildroot}%{_unitdir}/storj-storagenode@.service
install -D -p -m 0644 %{SOURCE12} %{buildroot}%{_unitdir}/storj-storagenode-setup@.service

install -dD -m 0750 %{buildroot}%{_sharedstatedir}/storj-storagenode


install -dD -m 0750 %{buildroot}%{_sysconfdir}/storj-storagenode

#web console
install -dD -m755 %{buildroot}%{_datadir}/%{name}
cp -a web/storagenode/dist %{buildroot}%{_datadir}/%{name}/

%pre storagenode
getent group storj-storagenode >/dev/null || groupadd -r storj-storagenode
getent passwd storj-storagenode >/dev/null || \
  useradd -r -g storj-storagenode -s /sbin/nologin \
    -d %{_sharedstatedir}/storj-storagenode \
    -c 'Storj Storage Node' storj-storagenode
exit 0


%post storagenode
%systemd_post storj-storagenode@.service

%preun storagenode
%systemd_preun storj-storagenode@.service

%postun storagenode
%systemd_postun_with_restart storj-storagenode@\*.service

%files storagenode
%doc storj-storagenode.conf
%config %dir %attr(-,-,storj-storagenode) %{_sysconfdir}/storj-storagenode
%{_bindir}/storagenode
%{_unitdir}/storj-storagenode@.service
%{_unitdir}/storj-storagenode-setup@.service
%attr(0770,storj-storagenode,storj-storagenode) %{_sharedstatedir}/storj-storagenode
%{_datadir}/%{name}

%files identity
%{_bindir}/identity

%changelog
* Sun Sep 05 2021 Jonny Heggheim <hegjon@gmail.com> - 1.37.2-5
- Added storj-identity

* Fri Sep 03 2021 Jonny Heggheim <hegjon@gmail.com> - 1.37.2-4
- Build storagenode from source

* Fri Sep 03 2021 Jonny Heggheim <hegjon@gmail.com> - 1.37.2-3
- Fixed wrong placement of web consile files

* Thu Sep 02 2021 Jonny Heggheim <hegjon@gmail.com> - 1.37.2-2
- Include web console files

* Thu Sep 02 2021 Jonny Heggheim <hegjon@gmail.com> - 1.37.2-1
- Updated to version 1.37.2

* Sun Aug 08 2021 Jonny Heggheim <hegjon@gmail.com> - 1.35.3-1
- Initial package from pre-built binary