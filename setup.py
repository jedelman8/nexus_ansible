from distutils.core import setup
setup(
  name='nexus_ansible',
  packages=['nexus_ansible'],
  version='0.4',
  description='A random test lib',
  author='Jason Edelman',
  author_email='jedelman8@gmail.com',
  url='https://github.com/jedelman8/nexus_ansible',
  download_url='https://github.com/jedelman8/nexus_ansible/tarball/0.4',
  install_requires=[
      'xmltodict',
  ],
)
