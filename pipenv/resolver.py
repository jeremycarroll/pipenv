"""Interal CLI for invoking pip to resolve dependencies"""

import os
import sys
import json
import logging

os.environ["PIP_PYTHON_PATH"] = str(sys.executable)


def _patch_path():
    import site
    pipenv_libdir = os.path.dirname(os.path.abspath(__file__))
    pipenv_site_dir = os.path.dirname(pipenv_libdir)
    site.addsitedir(pipenv_site_dir)
    for _dir in ("vendor", "patched"):
        sys.path.insert(0, os.path.join(pipenv_libdir, _dir))


def which(*args, **kwargs):
    # Note, unclear why using this one rather than pipenv.core.which
    return sys.executable


class ResolverCli(object):
    """This class sets up the environment etc, for invoking pip via entry points in
    pipenv.utils"""
    NAME = "pipenv-resolver"

    def __init__(self):
        _patch_path()
        from pipenv.vendor import colorama
        from pipenv.core import project
        colorama.init()
        self.project = project
        self.parsed = None

    def get_parser(self):
        from argparse import ArgumentParser
        parser = ArgumentParser(self.NAME)
        parser.add_argument("--pre", action="store_true", default=False)
        parser.add_argument("--clear", action="store_true", default=False)
        parser.add_argument("--verbose", "-v", action="count", default=False)
        parser.add_argument("--debug", action="store_true", default=False)
        parser.add_argument("--system", action="store_true", dest='allow_global', default=False)
        parser.add_argument("--requirements-dir", metavar="requirements_dir", action="store",
                            default=os.environ.get("PIPENV_REQ_DIR"))
        parser.add_argument("packages", nargs="*")
        return parser

    def handle_parsed_args(self, parsed):
        if parsed.debug:
            parsed.verbose = max(parsed.verbose, 2)
        if parsed.verbose > 1:
            logging.getLogger("notpip").setLevel(logging.DEBUG)
        elif parsed.verbose > 0:
            logging.getLogger("notpip").setLevel(logging.INFO)
        if "PIPENV_PACKAGES" in os.environ:
            parsed.packages += os.environ.get("PIPENV_PACKAGES", "").strip().split("\n")
        return parsed

    def main(self):
        import warnings
        from pipenv.vendor.vistir.compat import ResourceWarning
        warnings.simplefilter("ignore", category=ResourceWarning)
        import io
        import six
        if six.PY3:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer,encoding='utf8')
        else:
            from pipenv._compat import force_encoding
            force_encoding()

        os.environ["PIP_DISABLE_PIP_VERSION_CHECK"] = str("1")
        os.environ["PYTHONIOENCODING"] = str("utf-8")
        os.environ["PIP_PYTHON_VERSION"] = ".".join([str(s) for s in sys.version_info[:3]])
        os.environ["PIP_PYTHON_PATH"] = str(sys.executable)

        parser = self.get_parser()
        parsed, remaining = parser.parse_known_args()
        # sys.argv = remaining
        self.parsed = self.handle_parsed_args(parsed)

        self.run(self.get_sources())


    def get_sources(self):
        from pipenv.utils import create_mirror_source, replace_pypi_sources

        if "PIPENV_PYPI_MIRROR" in os.environ:
            pypi_mirror_source = create_mirror_source(os.environ["PIPENV_PYPI_MIRROR"])
            return replace_pypi_sources(self.project.pipfile_sources, pypi_mirror_source)
        else:
            return self.project.pipfile_sources

    def run(self, sources):
        from pipenv.utils import ResolverWrapper
        results = ResolverWrapper(self.parsed, self.project, sources).run(which)
        print("RESULTS:")
        if results:
            print(json.dumps(results))
        else:
            print(json.dumps([]))


if __name__ == "__main__":
    ResolverCli().main()
