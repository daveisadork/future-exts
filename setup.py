from setuptools import setup

with open("future_exts/__init__.py", "r") as f:
    version_marker = "__version__ = "
    for line in f:
        if line.startswith(version_marker):
            _, version = line.split(version_marker)
            version = version.strip().strip('"')
            break
    else:
        raise RuntimeError("Version marker not found.")


def parse_dependencies(filename):
    with open(filename) as reqs:
        for line in reqs:
            if line.startswith("#"):
                continue

            yield line.strip()


dependencies = list(parse_dependencies("requirements.txt"))

setup(
    name="future-exts",
    version=version,
    packages=["future_exts"],
    install_requires=dependencies,
)
