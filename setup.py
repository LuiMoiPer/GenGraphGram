from setuptools import setup, find_packages

setup(
    name = 'gengraphgen',
    version = '0.0.1',
    description = 'A package for making and using generative graph grammars',
    py_modules = find_packages('gengraphgram'),
    package_dir = {'' : 'gengraphgram'},
    install_requires = [
        'networkx >= 2.4',
    ],
    url = 'https://github.com/LuiMoiPer/GenGraphGram',
    author = 'Luis M. Perez',
    email = 'luimoiper@outlook.com'
)