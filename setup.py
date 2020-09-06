from setuptools import find_packages, setup

setup(
    name="Parser",
    version="06.09",
    packages=find_packages(),
    description='Scrapy Proxies: random proxy middleware for Scrapy',
    author='Alexey Korshakov',
    author_email='korshakov_07@mail.ru',
    url='https://github.com/AlexKorshakov/Parser_YD_GOO',
    zip_safe=True,

    include_package_data=True,
    exclude_package_data={"": ["*_Log.txt"]},
)
