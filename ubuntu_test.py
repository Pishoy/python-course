from JumpscaleLibs.sal.ubuntu.Ubuntu import Ubuntu
from Jumpscale import j
from unittest import TestCase
import os
from unittest import skip

class Test_Ubuntu(TestCase):
    j.sal.process.execute("apt update")
    j.sal.process.execute("apt-get install -y python3-distutils-extra python3-dbus python3-apt")

    def setUp(self):
        self.ubuntu = Ubuntu()

    def tearDown(self):
        pass

    def test001_uptime(self):
        with open("/proc/uptime") as f:
            data = f.read()
            uptime, _ = data.split(" ")

        self.assertAlmostEqual(float(uptime), self.ubuntu.uptime(), delta=1000)

    def test002_check(self):
        self.assertTrue(self.ubuntu.check())

    def test003_version_get(self):
        self.assertIn("Ubuntu", self.ubuntu.version_get())

    def test004_apt_install_check(self):
        # if it fails, it will raise an error
        self.ubuntu.apt_install_check("iputils-ping", "ping")

    def test005_apt_install_version(self):
        self.ubuntu.apt_install_version("wget", "1.19.4-1ubuntu2.2")
        rc, out, err = j.sal.process.execute("wget -V", useShell=True)
        self.assertIn("1.19.4", out)

    def test006_deb_install(self):
        j.sal.process.execute(
            "curl  http://security.ubuntu.com/ubuntu/pool/universe/t/tmuxp/python-tmuxp_1.5.0a-1_all.deb > python-tmuxp_1.5.0a-1_all.deb"
        )
        self.ubuntu.deb_install(path="python-tmuxp_1.5.0a-1_all.deb")
        rc, out, err = j.sal.process.execute("dpkg -s python-tmuxp | grep Status", die=False)
        self.assertIn("install ok", out)

    def test007_pkg_list(self):
        """
        no package called ping so output len should equal zero
        the correct package name is iputils-ping        """
        self.assertEqual(len(self.ubuntu.pkg_list("ping")), 0)

    def test008_service_start(self):
        self.ubuntu.service_start("cron")
        rc, out, err = j.sal.process.execute("service cron status")
        if 'cron is running' in out:
            self.assertIn("cron is running", out)
        else:
            self.assertIn("Active: active (running)", out)

    def test009_service_stop(self):
        j.sal.process.execute("service cron start")
        self.ubuntu.service_stop("cron")
        rc, out, err = j.sal.process.execute("service cron status", die=False)
        if 'cron is running' in out:
            self.assertIn("cron is not running", out)
        else:
            self.assertIn("Active: inactive (dead)", out)

    def test010_service_restart(self):
        j.sal.process.execute("service cron start")
        self.ubuntu.service_restart("cron")
        rc, out, err = j.sal.process.execute("service cron status")
        if 'cron is running' in out:
            self.assertIn("cron is running", out)
        else:
            self.assertIn("Active: active (running)", out)

    def test011_service_status(self):
        j.sal.process.execute("service cron start")
        rc, out, err = j.sal.process.execute("service cron status")
        if 'cron is running' in out:
            self.assertIn("cron is running", out)
        else:
            self.assertIn("Active: active (running)", out)

    def test012_apt_find_all(self):
        self.assertIn("wget", self.ubuntu.apt_find_all("wget"))

    def test013_is_pkg_installed(self):
        self.assertTrue(self.ubuntu.is_pkg_installed("wget"))

    def test014_sshkey_generate(self):
        self.ubuntu.sshkey_generate(path="/tmp/id_rsa")
        rc, out, err = j.sal.process.execute("ls /tmp | grep id_rsa")
        self.assertIn("id_rsa", out)

    def test015_apt_get_cache_keys(self):
        """
        this should get the cached packages of ubuntu
        1 - get all cached keys by our tested method
        2 - get a one package from cached packages by apt-cache command
        3 - compare the package name of step2 should be included in keys form step 1
        """
        cache_list = self.ubuntu.apt_get_cache_keys()
        rc1, pkg_name, err1 = j.sal.process.execute("apt-cache search 'Network' | head -1| awk '{print $1}'")
        name = pkg_name.strip()
        self.assertIn(name, cache_list)

    def test016_apt_get_installed(self):
        """
        1 - get length of installed packages from tested method
        2 - get length of installed packages from apt list command
        3 - compare step 1 and 2 should be equal
        """
        sal_count = len(self.ubuntu.apt_get_installed())
        rc1, os_count, err1 = j.sal.process.execute("apt list --installed |grep -v 'Listing...'| wc -l")
        os_int_count = int(os_count.strip())
        self.assertEqual(sal_count, os_int_count)

    def test017_apt_install(self):
        """
        1 - check if speedtest-cli is installed or not
        2 - if installed, remove it and use tested method to install it and verfiy that is installed
        3 - esle so we install speedtest-cli by tested method and verify that is installed successfully and remove it \
         to be as origin status
        """
        if j.sal.ubuntu.is_pkg_installed('speedtest-cli'):
            j.sal.process.execute("apt remove -y speedtest-cli")
            self.ubuntu.apt_install('speedtest-cli')
            rc1, out1, err1 = j.sal.process.execute("dpkg -s speedtest-cli|grep Status")
            self.assertIn('install ok',out1)
        else:
            self.ubuntu.apt_install('speedtest-cli')
            rc2, out2, err2 = j.sal.process.execute("dpkg -s speedtest-cli|grep Status")
            self.assertIn('install ok', out2)
            j.sal.process.execute("apt remove -y speedtest-cli")

    def test018_apt_sources_list(self):
        """
        1 - get all listed apt sources
        2 - get the first line in apt sources list, should contains a keyworod deb
        """
        apt_src_list = self.ubuntu.apt_sources_list()
        first_src = apt_src_list[0]
        self.assertIn('deb', first_src)

    def test019_apt_sources_uri_add(self):
        """
        1 - check if the source link file that am gonna add it exist or not
        2 - if exist move it a /tmp dir so at the end of test we return it back
        check adding url then it create a file under /etc/apt/sources.list.d started with deb and add the url
        you put ony url, method will add deb in starting of it
        """
        if os.path.exists('/etc/apt/sources.list.d/archive.getdeb.net.list'):
            j.sal.process.execute("mv /etc/apt/sources.list.d/archive.getdeb.net.list /tmp")
            self.ubuntu.apt_sources_uri_add('http://archive.getdeb.net/ubuntu wily-getdeb games')
            rc1, os_apt_sources, err1 = j.sal.process.execute(
            "grep 'ubuntu wily-getdeb games' /etc/apt/sources.list.d/archive.getdeb.net.list")
            self.assertIn('deb', os_apt_sources)
            j.sal.process.execute("mv /tmp/archive.getdeb.net.list /etc/apt/sources.list.d/")
        else:
            self.ubuntu.apt_sources_uri_add('http://archive.getdeb.net/ubuntu wily-getdeb games')
            rc2, os_apt_sources2, err2 = j.sal.process.execute(
                "grep 'ubuntu wily-getdeb games' /etc/apt/sources.list.d/archive.getdeb.net.list")
            self.assertIn('deb', os_apt_sources2)
            j.sal.process.execute("rm /etc/apt/sources.list.d/archive.getdeb.net.list")

    def test020_apt_upgrade(self):
        """
        1 - get number of packages that need to be upgraded
        2 - run tested method to upgrade packages
        3 - get number of packages that need to be upgraded again after upgrade
        4 - if upgrade runs successfully then number in step 1 should be greater than one in step3
        5- if all packages are already upgraded before run our tested method and no need to upgrade any packages\
        they should be equal so i used  GreaterEqual
        """
        rc1, upgradable_pack_before_upgrade, err1 = j.sal.process.execute(
            "apt list --upgradable | grep -v 'Listing...'| wc -l")
        upgradable_pack_count_before_upgrade = int(upgradable_pack_before_upgrade.strip())
        self.ubuntu.apt_upgrade()
        rc2, upgradable_pack_after_upgrade, err2 = j.sal.process.execute(
            "apt list --upgradable | grep -v 'Listing...'| wc -l")
        upgradable_pack_count_after_upgrade = int(upgradable_pack_after_upgrade.strip())
        self.assertGreaterEqual(upgradable_pack_count_before_upgrade, upgradable_pack_count_after_upgrade)

    def test021_check(self):
        """
        check is True when the destribution is ubunut or linuxmint
        1 - get os name by lsb_relase command
        2 - if result in step 1 is Ubuntu or linuxmint then our test method should give True
        3 - else should not in Ubuntu nor linuxmint
        """
        rc1, distro_name, err1 = j.sal.process.execute("lsb_release -i | awk '{print $3}'")
        distro1 = distro_name.strip()
        if distro1 in ("Ubuntu", "LinuxMint"):
            self.assertTrue(self.ubuntu.check())
        else:
            self.assertNotIn('Ubuntu', distro1)
            self.assertNotIn('LinuxMint', distro1)

    def test022_deb_download_install(self):
        """
        check download and install the package
        1-check status of tcpdump is installed or not
        2-if tcpdump installed remove it by apt remove before install it, then installed it again by tested method
        3-if tcpdump not installed anymore, then installed it by our tested method and remove it finally
        """
        if j.sal.ubuntu.is_pkg_installed('tcpdump'):
            j.sal.process.execute("apt remove -y tcpdump")
            j.sal.ubuntu.deb_download_install(
                "http://download.unesp.br/linux/debian/pool/main/t/tcpdump/tcpdump_4.9.2-3_amd64.deb")
            rc2, out2, err2 = j.sal.process.execute('dpkg -s tcpdump|grep Status')
            self.assertIn('install ok',out2)
        else:
            j.sal.ubuntu.deb_download_install(
            "http://download.unesp.br/linux/debian/pool/main/t/tcpdump/tcpdump_4.9.2-3_amd64.deb")
            rc3, out3, err3 = j.sal.process.execute('dpkg -s tcpdump|grep Status')
            self.assertIn('install ok', out3)
            j.sal.process.execute("apt remove -y tcpdump")

    def test023_pkg_remove(self):
        """
        1 - check the tcpdummp is installed or not
        2 - if installed remove it by tested method and check that it does not exist by is_pkg_installed \
        finally install it again to return it to orginal state
        3 - if tcpdump not installed, install it, then verify that is installed then remove it with tested method \
        then verify that is removed successfully
        """
        if j.sal.ubuntu.is_pkg_installed('tcpdump'):
            j.sal.ubuntu.pkg_remove('tcpdump')
            self.assertFalse(j.sal.ubuntu.is_pkg_installed('tcpdump'))
            j.sal.process.execute("apt install -y tcpdump")
        else:
            j.sal.process.execute("apt install -y tcpdump")
            rc2, out2, err2 = j.sal.process.execute('dpkg -s tcpdump|grep Status')
            self.assertIn('install ok', out2)
            j.sal.ubuntu.pkg_remove('tcpdump')
            self.assertFalse(j.sal.ubuntu.is_pkg_installed('tcpdump'))

    def test024_service_disable_start_boot(self):
        """
        1- check if service is enabled then disable service and verify that is already disabled and then enable it back
        2- if not enabled, then enable it and disable it and verify that is already disabled
        """
        if os.path.exists('/etc/rc5.d/S01cron'):
            self.ubuntu.service_disable_start_boot('cron')
            self.assertFalse(os.path.exists('/etc/rc5.d/S01cron'))
            self.ubuntu.service_enable_start_boot('cron')
        else:
            self.ubuntu.service_enable_start_boot('cron')
            self.assertTrue(os.path.exists('/etc/rc5.d/S01cron'))
            self.ubuntu.service_disable_start_boot('cron')
            self.assertFalse(os.path.exists('/etc/rc5.d/S01cron'))

    def test025_service_enable_start_boot(self):
        """
        same idea as above
        """
        if os.path.exists('/etc/rc5.d/S01cron'):
            self.ubuntu.service_disable_start_boot('cron')
            self.assertFalse(os.path.exists('/etc/rc5.d/S01cron'))
            self.ubuntu.service_enable_start_boot('cron')
            self.assertTrue(os.path.exists('/etc/rc5.d/S01cron'))
        else:
            self.ubuntu.service_enable_start_boot('cron')
            self.assertTrue(os.path.exists('/etc/rc5.d/S01cron'))
            self.ubuntu.service_disable_start_boot('cron')
            self.assertFalse(j.sal.fs.exists('/etc/rc5.d/S01cron'))

    @skip('https://github.com/threefoldtech/jumpscaleX_libs/issues/5')
    def test026_service_uninstall(self):
        """
        is a service install not a package install which is mean only create a file in /etc/init/ dir
        1 - install psql using builer to run test with it , it should create a psql binary file under /sandbox/bin
        2 - check if the service config file is exist , then we can test our uninstall method and check it removes \
        service config file
        3 - else if service config file does not exist then try to install psql service config file and run uninstall \
        method and verify the service config file does not exist
        """
        if os.path.exists('/etc/init/cron'):
            j.sal.process.execute("cp /etc/init/cron.conf /tmp")
            self.ubuntu.service_uninstall('cron')
            self.assertFale(os.path.exists('/etc/init/cron.conf'))
            j.sal.process.execute("cp /tmp/cron.conf /etc/init/cron.conf ")
        else:
            self.ubuntu.service_install('cron','/etc/init.d')
            self.assertTrue(os.path.exists('/etc/init/cron.conf'))
            self.ubuntu.service_uninstall('cron')
            self.assertFalse(os.path.exists('/etc/init/cron.conf'))

    def test027_whoami(self):
        sal_user = self.ubuntu.whoami()
        rc2, os_user, err2 = j.sal.process.execute("whoami")
        self.assertEquals(os_user.strip(), sal_user)


def main(self=None):
    """
    to run:
    kosmos 'j.sal.ubuntu._test(name="ubuntu")'
    """
    test_ubuntu = Test_Ubuntu()
    test_ubuntu.setUp()
    test_ubuntu.test001_uptime()
    test_ubuntu.test002_check()
    test_ubuntu.test003_version_get()
    test_ubuntu.test004_apt_install_check()
    test_ubuntu.test005_apt_install_version()
    test_ubuntu.test006_deb_install()
    test_ubuntu.test007_pkg_list()
    test_ubuntu.test008_service_start()
    test_ubuntu.test009_service_stop()
    test_ubuntu.test010_service_restart()
    test_ubuntu.test011_service_status()
    test_ubuntu.test012_apt_find_all()
    test_ubuntu.test013_is_pkg_installed()
    test_ubuntu.test014_sshkey_generate()
    test_ubuntu.test015_apt_get_cache_keys()
    test_ubuntu.test016_apt_get_installed()
    test_ubuntu.test017_apt_install()
    test_ubuntu.test018_apt_sources_list()
    test_ubuntu.test019_apt_sources_uri_add()
    test_ubuntu.test020_apt_upgrade()
    test_ubuntu.test021_check()
    test_ubuntu.test022_deb_download_install()
    test_ubuntu.test023_pkg_remove()
    test_ubuntu.test024_service_disable_start_boot()
    test_ubuntu.test025_service_enable_start_boot()
    test_ubuntu.test026_service_uninstall()
    test_ubuntu.test027_whoami()
    test_ubuntu.tearDown()
