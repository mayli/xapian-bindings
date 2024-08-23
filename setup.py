import shutil
import venv
from pathlib import Path
from shutil import rmtree
from subprocess import check_call

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext as build_ext_orig

VERSION = "1.4.26"
CORE_URL = f"https://oligarchy.co.uk/xapian/{VERSION}/xapian-core-{VERSION}.tar.xz"
BINDINGS_URL = (
    f"https://oligarchy.co.uk/xapian/{VERSION}/xapian-bindings-{VERSION}.tar.xz"
)


def fetch():
    pass


class build_ext(build_ext_orig):
    def run(self):
        prefix = Path("build")
        target = Path(self.build_lib) / "xapian"

        env = Path(Path(self.build_temp).resolve())
        venv.main([str(env)])

        core_dir = prefix / f"xapian-core-{VERSION}"
        if not core_dir.exists():
            check_call(f"curl {CORE_URL}|tar -xJf -", cwd=prefix, shell=True)
            check_call(
                f"./configure --prefix={env.resolve()}",
                cwd=core_dir,
                shell=True,
            )
        check_call(
            "make -j $(nproc) && make install",
            cwd=core_dir,
            shell=True,
        )

        check_call([env / "bin" / "pip", "install", "sphinx"])

        bindings_dir = prefix / f"xapian-bindings-{VERSION}"
        if not bindings_dir.exists():
            check_call(f"curl {BINDINGS_URL}|tar -xJf -", cwd=prefix, shell=True)
        activate = env / "bin" / "activate"
        check_call(
            f"""
            . {activate.resolve()};
            ./configure --with-python3 --prefix={env.resolve()} && make -j $(nproc) && make install""",
            cwd=bindings_dir,
            shell=True,
        )

        src = next(env.glob("lib/python*/site-packages/xapian"))
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(src, target)


setup(
    name="xapian-bindings",
    version=VERSION,
    description="A short description of your package",
    author="xapian-bindings dev",
    packages=["xapian"],
    ext_modules=[Extension("xapian", [])],
    cmdclass={"build_ext": build_ext},
    package_data={
        "xapian": ["_xapian.*"],
    },
    setup_requires=[
        "sphinx",
    ],
)
