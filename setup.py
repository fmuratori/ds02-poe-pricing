from setuptools import setup, find_packages

# "psycopg2==2.8.4",

setup(
    name = "poe-price",
    version = "1.0.0",
    packages = find_packages("src"),
    package_dir = {"": "src"},
    include_package_data = True,
    install_requires = [
        "numpy==1.18.1",
        "psycopg2-binary==2.8.5",
        "configparser==3.7.4",
        "smart-open==1.9.0",
        "pandas==0.25.3",
        "scikit-learn==0.22.2",
        "click==7.1.2"
    ],
    entry_points = {
        "console_scripts": [
            "poe-price = poe_price.main:main"
        ]
    }
)
