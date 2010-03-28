''' 
setuptools setup script.
'''

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup

setup(name='waferslim', 
      version='1.0.2',
      packages=['waferslim', 'waferslim.specs', 'waferslim.examples'],
      data_files=[('waferslim', ['waferslim/logging.conf']),
                  ('', ['README.txt', 'COPYING', 'COPYING.LESSER'])],
      provides=['waferslim'],
      requires=['lancelot'],
      install_requires=['lancelot'],
      license='GNU Lesser General Public License v3 (LGPL v3)',
      description='A python port of the fitnesse slim server and protocols',
      long_description='''WaferSlim is a python port of the fitnesse slim 
server and protocols -- see http://fitnesse.org/FitNesse.SliM for more details.
''',
      platforms = ["Windows", "Linux", "Solaris", "Mac OS-X", "Unix"],
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities'],
      author='tim bacon',
      author_email='timbacon at gmail dotcom',
      url='http://withaherring.blogspot.com/',
#Development Status :: 5 - Production/Stable
#Development Status :: 6 - Mature
      )
