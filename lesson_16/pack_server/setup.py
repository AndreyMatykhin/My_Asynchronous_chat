from setuptools import setup, find_packages

setup(name="my_messanger_server",
      version="0.0.0",
      description="messenger_server",
      author="Andrey Matyukhin ",
      author_email="matykhinand2021@gmail.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )