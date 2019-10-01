from JumpscaleLibs.sal.ubuntu.Ubuntu import Ubuntu
from Jumpscale import j
from unittest import TestCase
import os

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
            "wget http://security.ubuntu.com/ubuntu/pool/universe/t/tmuxp/python-tmuxp_1.5.0a-1_all.deb"
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
        self.assertIn("cron is running", out)

    def test009_service_stop(self):
        j.sal.process.execute("service cron start")
        self.ubuntu.service_stop("cron")
        rc, out, err = j.sal.process.execute("service cron status", die=False)
        self.assertIn("cron is not running", out)

    def test010_service_restart(self):
        j.sal.process.execute("service cron start")
        self.ubuntu.service_restart("cron")
        rc, out, err = j.sal.process.execute("service cron status")
        self.assertIn("cron is running", out)

    def test011_service_status(self):
        j.sal.process.execute("service cron start")
        self.assertTrue(self.ubuntu.service_status("cron"))

    def test012_apt_find_all(self):
        self.assertIn("wget", self.ubuntu.apt_find_all("wget"))

    def test013_is_pkg_installed(self):
        self.assertTrue(self.ubuntu.is_pkg_installed("wget"))

    def test014_sshkey_generate(self):
        self.ubuntu.sshkey_generate(path="/tmp/id_rsa")
        rc, out, err = j.sal.process.execute("ls /tmp | grep id_rsa")
        self.assertIn("id_rsa", out)

    @skip("https://github.com/threefoldtech/jumpscaleX_libs/issues/5")
    def test015_apt_get_cache_keys(self):
        cache_list = self.ubuntu.apt_get_cache_keys()
        rc1, pkg_name, err1 = j.sal.process.execute("apt-cache search 'Network' | head -1| awk '{print $1}'")
        name = pkg_name.strip()
        self.assertIn(name, cache_list)

    def test016_apt_get_installed(self):
        """
        compare number of packages of os apt list --installed output with sal output
        """
        sal_count = len (self.ubuntu.apt_get_installed())
        rc1, os_count, err1 = j.sal.process.execute("apt list --installed |grep -v 'Listing...'| wc -l")
        os_int_count = int (os_count.strip())
        self.assertEqual(sal_count, os_int_count)

    def test017_apt_install(self):
        self.ubuntu.apt_install('speedtest-cli')
        rc1, os_installed, err1 = j.sal.process.execute("apt list --installed |grep speedtest")
        self.assertIn('speedtest',os_installed)

    def test018_apt_sources_list(self):
        """
        check the first line in apt sources list contains a keyworod deb
        """
        apt_src_list = self.ubuntu.apt_sources_list()
        first_src = apt_src_list.list[0]
        self.assertIn('deb',first_src)

    def test019_apt_sources_uri_add(self):
        """
        check adding url then it create a file under /etc/apt/sources.list.d started with deb and add the url
        you put ony url, method will add deb in starting of it
        :return:
        """
        if os.path.exists('/etc/apt/sources.list.d/archive.getdeb.net.list'):
            file_already_exist = 'True'
        else:
            file_already_exist = 'False'
        self.ubuntu.apt_sources_uri_add('http://archive.getdeb.net/ubuntu wily-getdeb games')
        rc1, os_apt_sources, err1 = j.sal.process.execute("grep 'ubuntu wily-getdeb games' /etc/apt/sources.list.d/archive.getdeb.net.list")
        self.assertIn('deb',os_apt_sources)
        if file_already_exist == 'False' :
        j.sal.process.execute("rm /etc/apt/sources.list.d/archive.getdeb.net.list")

    def test020_apt_upgrade(self):
        """
        check number of packages that need to be upgraded then upgrade them
        then check the number of packages that need to be upgraded again
        should be zero or less than the count of packages that needed to upgrade before doing upgrade
        """
        rc1,upgradable_pack_before_upgrade,err1 = j.sal.process.execute("apt list --upgradable | grep -v 'Listing...'| wc -l")
        upgradable_pack_count_before_upgrade = int (upgradable_pack_before_upgrade.strip())
        self.ubuntu.apt_upgrade()
        rc2, upgradable_pack_after_upgrade, err2 = j.sal.process.execute("apt list --upgradable | grep -v 'Listing...'| wc -l")
        upgradable_pack_count_after_upgrade = int (upgradable_pack_after_upgrade.strip())
        self.assertGreaterEqual(upgradable_pack_count_before_upgrade,upgradable_pack_count_after_upgrade)

    def test021_check(self):
        """
        check is True when the destribution is ubunut or linuxmint
        :return:
        """
        rc1,distro1,err1 = j.sal.process.execute("lsb_release -i | awk '{print $3}'")
        if distro1 in ("Ubuntu","linuxmint"):
            self.assertTrue(self.ubuntu.check())
        else:
            self.assertNotIn('Ubuntu', distro1)
            self.assertNotIn('LinuxMint', distro1)

    def test022_deb_download_install(self):
        """
        check download and install the package
        """
        rc1, out, err1 = j.sal.process.execute('dpkg -s tcpdump|grep Status')
        if self.assertIn('install ok',out):
            tcpdump_is_installed = 'True'
            # can i install it ?
        else:
            tcpdump_is_installed = 'False'
        j.sal.ubuntu.deb_download_install(
            "http://download.unesp.br/linux/debian/pool/main/t/tcpdump/tcpdump_4.9.2-3_amd64.deb")
        

    def test023_pkg_remove(self):
        """
        verify that tcpdump package is installed then remove it
        """
        j.sal.process.execute('apt install tcpdump -y')
        rc1, out, err1  = j.sal.process.execute('dpkg -s tcpdump|grep Status')
        self.assertIn('install ok',out)
        j.sal.ubuntu.pkg_remove('tcpdump')
        self.assertFalse(j.sal.ubuntu.is_pkg_installed('tcpdump'))

    def test024_service_disable_start_boot(self):
        self.ubuntu.service_enable_start_boot('cron')
        self.ubuntu.service_disable_start_boot('cron')
        self.assertFalse(j.sal.fs.exists('/etc/rc5.d/S01cron'))

    def test025_service_enable_start_boot(self):
        self.ubuntu.service_disable_start_boot('cron')
        self.ubuntu.service_enable_start_boot('cron')
        self.assertTrue(j.sal.fs.exists('/etc/rc5.d/S01cron'))

    def test026_service_uninstall(self):
        self.ubuntu.service_uninstall('cron')
        self.assertFalse(self.ubuntu.service_status("cron"))

    def test027_whoami(self):
        sal_user = self.ubuntu.whoami()
        rc2, os_user, err2 = j.sal.process.execute("whoami")
        self.assertEquals(os_user.strip(),sal_user)

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
    #test_ubuntu.test018_apt_sources_list() # skipping it has an issue
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