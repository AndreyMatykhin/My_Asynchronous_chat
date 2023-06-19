from setuptools import setup, find_packages

setup(name="my_messanger_client",
      version="0.0.1",
      description="messenger_client",
      author="Andrey Matyukhin ",
      author_email="matykhinand2021@gmail.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )