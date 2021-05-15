import io
import re
from os.path import join, dirname, abspath
from setuptools import setup, find_packages


def read(name):
    here = abspath(dirname(__file__))
    return io.open(
        join(here, name), encoding='utf8'
    ).read()


setup(
    name="vmshepherd",
    version="1.6.3",
    author='Dreamlab - PaaS KRK',
    author_email='paas-support@dreamlab.pl',
    url='https://github.com/Dreamlab/vmshepherd',
    description='Cluster manager',
    long_description='%s\n%s' % (
        read('README.rst'),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    ),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=read('requirements.txt').split('\n'),
    zip_safe=False,
    entry_points={
        'console_scripts': ['vmshepherd = vmshepherd.__main__:main'],
        'vmshepherd.driver.iaas': [
            'DummyIaasDriver = vmshepherd.iaas:DummyIaasDriver',
            'OpenStackDriver = vmshepherd.iaas:OpenStackDriver'
        ],
        'vmshepherd.driver.presets': [
            'DirectoryDriver = vmshepherd.presets:DirectoryDriver',
            'GitRepoDriver = vmshepherd.presets:GitRepoDriver'
        ],
        'vmshepherd.driver.runtime': ['InMemoryDriver = vmshepherd.runtime:InMemoryDriver'],
        'vmshepherd.driver.healthcheck': [
            'HttpHealthcheck = vmshepherd.healthcheck:HttpHealthcheck',
            'DummyHealthcheck = vmshepherd.healthcheck:DummyHealthcheck'
        ]
    },
    keywords=[
        'cluster', 'preset',
        'iaas', 'cloud',
        'openstack', 'nova',
        'aws', 'amazon', 'ec2'
    ],
    dependency_links=['https://pypi.python.org/pypi'],
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: POSIX'
    ]
)
