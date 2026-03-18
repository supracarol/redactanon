from setuptools import find_packages, setup

dev_requirements = [
    "pytest",
    "black",
    "mypy",
    "flake8",
    "isort",
    "bandit",
    "pre-commit",
]

extras_require = {
    "dev": dev_requirements,
}

setup(
    name="redactanon",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "Faker>=40.0.0",
    ],
    entry_points={
        "console_scripts": [
            "redactanon=redactanon.cli:main",
        ],
    },
    extras_require=extras_require,  # type: ignore
)
