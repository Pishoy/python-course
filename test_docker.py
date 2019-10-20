from JumpscaleLibs.sal.docker.Doker import Docker
from Jumpscale import j
from unittest import TestCase
import os
from unittest import skip
from loguru import logger

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

    def test001_container_list_all(self):
       """
       lists (all) containers

        #. Get number of containers from tested method
        #. Get number of containers from docker ps -a command
        #. both step1 and step2 should be equal
        """

        running_cont_method = int (len(self.docker.containers))
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
    def test005_build(self):
        """

        :param self:
        :return:
        """

    def test006_container_get(self):
        """
        get a container by name

        #. start a container test called testubuntu
        #. Get the container by name

        """
        if not j.sal.docker.exists('testubuntu'):
            j.sal.process.execute("docker run -dit --name=testubuntu bash")
        self.assertIn('testubuntu',j.sal.docker.container_get('testubunut'))

        if not j.sal.docker.exists('container_not_exist'):
            with self.assertRaises(j.exceptions.RuntimeError) as myexcept:
                j.sal.docker.container_get('container_not_exist')
                self.info("Container with name %s doesn't exists")
                self.assertIn("Container with name %s doesn't exists", myexcept.exception.args[0])
            self.assertIsNone(j.sal.docker.container_get('container_not_exist',die=False))
