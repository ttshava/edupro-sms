from setuptools import setup, find_packages

with open("edupro_sms/hooks.py") as f:
    exec(f.read())

setup(
    name="edupro-sms",
    version=globals().get("__version__", "0.0.1"),
    description=app_description,
    author=app_publisher,
    author_email=app_email,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[],
    python_requires=">=3.11",
)
