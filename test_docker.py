from JumpscaleLibs.sal.docker.Docker import Docker
from Jumpscale import j
from unittest import TestCase
import os
from unittest import skip
from loguru import logger
import random as rand
import docker
import os

class Test_Docker(TestCase):

    LOGGER = logger
    LOGGER.add("Config_manager_{time}.log")

    @staticmethod
    def info(message):
        Test_Docker.LOGGER.info(message)

    def setUp(self):
        self.docker = Docker()

    def tearDown(self):
        pass

    def test001_container_list(self):
        """
        lists (all) containers

         #. Get number of containers from tested method
         #. Get number of containers from docker ps -a command
         #. both step1 and step2 should be equal
         """
        running_cont_method = len(self.docker.containers)
        rc, out, err = j.sal.process.execute("docker ps -a --format '{{.Names}}' | wc -l")
        running_cont_command = int(out)
        self.assertEqual(running_cont_method,running_cont_command)

    def test002_containers_names_all(self):
        """
        list containers names, same issue as above only running docker are listed

        #. Get number of containers from tested method
        #. Get number of containers from docker ps -a command
        #. both step1 and step2 should be equal
        """
        running_cont_method = int (len(self.docker.containers_names()))
        rc, out, err = j.sal.process.execute("docker ps -a --format '{{.Names}}' | wc -l")
        running_cont_command = int(out)
        self.assertEqual(running_cont_method,running_cont_command)

    def test003_containers_names_running(self):
        """
        lists only running containers

        #. Get number of containers from tested method
        #. Get number of containers from docker ps command
        #. both step1 and step2 should be equal
        """
        running_cont_method = int (len(self.docker.containers_names_running))
        rc, out, err = j.sal.process.execute("docker ps --format '{{.Names}}' | wc -l")
        running_cont_command = int(out)
        self.assertEqual(running_cont_method,running_cont_command)
    def test004_containers_running(self):
        """
        lists only running containers

        #. Get number of containers from tested method
        #. Get number of containers from docker ps command
        #. both step1 and step2 should be equal
        """
        running_cont_method = int(len(self.docker.containers_names_running))
        rc, out, err = j.sal.process.execute("docker ps --format '{{.Names}}' | wc -l")
        running_cont_command = int(out)
        self.assertEqual(running_cont_method, running_cont_command)

    def test005_docker_host(self):
        """
        gets docker host name

        #. need to be in unix is return localhost , check with MAC

        """

        if "DOCKER_HOST" not in os.environ or os.environ["DOCKER_HOST"] == "":
            base_url = "unix://var/run/docker.sock"
        else:
            base_url = os.environ["DOCKER_HOST"]
            client = docker.APIClient(base_url=self.base_url)
        u = parse.urlparse(base_url)
        if u.scheme == "unix":
            self.info('system is a unix system so DOCKER_HOST will be localhost')
            self.assertIn('localhost',self.docker.docker_host())
        else:
            self.info('system is a not unix system so DOCKER_HOST will be {}'.format(u.hostname))
            self.assertIn(u.hostname,self.docker.docker_host())


    def test006_build(self):
        """
        build an image form a docker file

        #. create file and put contents of it
        #.
        """
        self.info('Delete ubuntu:testBishoy image if exist ')
        self.docker.images_remove('ubuntu:testBishoy')
        mycommand = """
        FROM ubuntu:14.04
        RUN  apt-get update \
        && apt-get install -y wget \
        && rm -rf /var/lib/apt/lists/*
        """
        with open('mydocker.file', 'w') as f:
            f.write(mycommand)
        self.docker.build(path='mydocker.file',tag='ubuntu:testBishoy')
        self.assertIn('ubuntu:testBishoy',self.docker.images_get())
        self.docker.images_remove('ubuntu:testBishoy')
        self.info('remove docker file after test')
        j.sal.process.execute("rm mydocker.file")

    def test007_container_get(self):
        """
        get a container by name

        #. start a container test called testubuntu
        #. Get the container by name
        #. if the container does not exist and die flag is True by default, should trigger a RuntimeError
        #. ff the container does not exist and die flag set to False, should return None

        """
        container_exist = True
        if not j.sal.docker.exists('testubuntu'):
            container_exist = False
            self.info('creating and stating a container test called testubuntu')
            j.sal.process.execute("docker run -dit --name=testubuntu  ubuntu:18.04 bash")
        self.info("verifying getting testubuntu container by it's name")
        self.assertIn('testubuntu',j.sal.docker.container_get('testubunut'))
        if container_exist is False:
            j.sal.process.execute("docker rm -f testubuntu")

        number = rand.randint(1000,2000)
        name ='container_test{}'.format(number)
        if j.sal.docker.exists(name):
            self.info('removing container  {} before testing as it is already exist'.format(name))
            j.sal.process.execute("docker rm -f {} ".format(name))
        else:
            with self.assertRaises(j.exceptions.RuntimeError) as myexcept:
                self.info('container {} does not exist and die flag is True by default'.format(name))
                j.sal.docker.container_get(name)
                self.info("Container with name {} doesn't exists".format(name))
                self.info('verifying container {} does not by tested method while die flag is True '.format(name))
                self.assertIn("Container with name %s doesn't exists", myexcept.exception.args[0])
            self.info('verifying container {} does not by tested method while die flag is False'.format(name))
            self.assertIsNone(j.sal.docker.container_get(name,die=False))


    def test008_container_get_by_id(self):
        """
        get container by id

        #. start a container test called testubuntu
        #. Get the container by id
        #. if the container does not exist and die flag is True by default, should trigger a RuntimeError
        #. ff the container does not exist and die flag set to False, should return None
        #.
        """
        container_exist = True
        container_id = 0
        if j.sal.docker.exists('container_test_id'):
            container_exist = False
            self.info('creating and stating a container test called container_test_id')
            j.sal.process.execute("docker run -dit --name=container_test_id ubuntu:18.04 bash")
        container_id = j.sal.process.execute("docker ps -a | grep container_test_id | awk '{print $1}'")
        self.info("verifying getting container_test_id container by it's id")
        self.assertIn(container_id, j.sal.docker.container_get(container_id))
        if container_exist is False:
            j.sal.process.execute("docker rm -f container_test_id")

        number2 = rand.randint(4000, 5000)
        name2 = 'container_test{}'.format(number2)
        if j.sal.docker.exists(name2):
            j.sal.process.execute("docker rm -f {} ".format(name2))
        else:
            with self.assertRaises(j.exceptions.RuntimeError) as myexcept:
                self.info('container {} does not exist and die flag is True by default'.format(name2))
                j.sal.docker.container_get(name2)
                self.info("Container with name {} doesn't exists".format(name2))
                self.info('verifying container {} does not by tested method while die flag is True'.format(name2))
                self.assertIn("Container with name %s doesn't exists", myexcept.exception.args[0])
            self.info('verifying container {} does not by tested method while die flag is False'.format(name2))
            self.assertIsNone(j.sal.docker.container_get(name2, die=False))

    @skip('https://github.com/threefoldtech/jumpscaleX_libs/issues/29')
    def test009_create_container(self):
        """skip it now due to issue"""

    def test010_container_exist(self):
        """
        Check container exist
        """

        self.info ('create a container called testBishoy_cont')
        rc,out,err = j.sal.process.execute("docker run -dit --name=testBishoy_cont ubuntu:18.04 bash")
        self.assertTrue(self.docker.exists(testBishoy_cont))
        self.info('deleting container testBishoy_cont')
        j.sal.process.execute("docker rm -f testBishoy_cont")
        self.info('verifying exists method while container is deleted')
        self.assertFalse(self.docker.exists(testBishoy_cont))

    def test011_docker_images_get(self):
        """
        lists images all images in docker host

        #.
        #.
        """
        self.info('getting number of images by tested method ')
        method_count = len(self.docker.images_get())
        self.info('getting number of images by docker images command')
        rc, out, err = j.sal.process.execute("docker images -q  | wc -l")
        cmd_count = int(out)
        self.assertEqual(method_count,cmd_count)

    def test012_images_remove(self):
        """
        Delete a certain Docker image using tag

        """
        self.info('checking if ubuntu:TestTag image is exist ')
        myimages = self.docker.images_get()
        if not 'ubuntu:TestTag' in myimages:

            mycommand = """
            FROM ubuntu:16.04
            RUN  apt-get update \
            && apt-get install -y wget \
            && rm -rf /var/lib/apt/lists/*
            """
            with open('mydocker.file', 'w') as f:
                f.write(mycommand)
            self.docker.build(path='mydocker.file', tag='ubuntu:TestTag')
        self.docker.images_remove('ubuntu:TestTag')
        self.info('verifying that images ubuntu:TestTag not exist between images after removing it ')
        self.assertIn('ubuntu:TestTag',self.docker.images_get())

    def test013_docker_ping(self):
        """
        check if docker daemon is running or not
        """
        if  j.sal.ubuntu.service_status('docker'):
            self.assertTrue(self.docker.ping())
        else:
            self.assertFalse(self.docker.ping())


    def test014_image_pull(self):
        """
        pull a certain image.
        """
        self.info('pulling ubuntu:16.04 ')
        j.sal.docker.pull('ubuntu:16.04')
        self.info('verifying that image ubuntu:16.04 is exist')
        self.assertIn('ubuntu:16.04',self.docker.images_get())

    @skip('https://github.com/threefoldtech/jumpscaleX_libs/issues/29')
    def test015_image_push(self):
        """
        push image
        """
    @skip('https://github.com/threefoldtech/jumpscaleX_libs/issues/29')
    def test016_status(self):
        """
        return list docker containers with some info like [name, image, sshport, status]
        """


def main(self=None):
    """
    to run:
    kosmos 'j.sal.ubuntu._test(name="docker")'
    """
    test_docker = Test_Docker()
    test_docker.setUp()
    test_docker.test001_container_list_all()
    test_docker.test002_containers_names_all()
    test_docker.test003_containers_names_running()
    test_docker.test004_containers_running()
    test_docker.test005_docker_host()
    test_docker.test006_build()
    test_docker.test007_container_get()
    test_docker.test008_container_get_by_id()
    test_docker.test009_create_container()
    test_docker.test010_container_exist()
