from dataclasses import dataclass

import py
import pytest


FIXTURE = "fixture"


@dataclass
class Key:
    fixtures = "fixtures"


def pytest_collect_file(parent, path):
    if path.ext == ".yaml":  # and path.basename.startswith("test"):
        return YamlFile.from_parent(fspath=path, parent=parent)
    # if path.ext == ".py":
    #     return pytest.Module.from_parent(parent=parent, fspath=path)


# -- https://docs.pytest.org/en/stable/parametrize.html#basic-pytest-generate-tests-example


def pytest_generate_tests(metafunc):
    if "variant_1" in metafunc.fixturenames:
        metafunc.parametrize("variant_1", ["injected #1", "injected #2"])


# -- inject fixture programmatically
# -- https://github.com/pytest-dev/pytest/issues/2424


def generate_fixture(scope, name, value):
    @pytest.fixture(scope=scope)
    def my_fixture():
        print(f"fixture: scope '{scope}', name '{name}', value '{value}'")
        return value

    assert scope in ("session", "module", "function")
    return my_fixture


def inject_fixture(scope, name, value):
    globals()[name] = generate_fixture(scope, name, value)


inject_fixture("function", "variant_2", 100)


# -- YAML


class YamlFile(pytest.File):
    def __init__(self, parent, fspath: py.path.local):
        import yaml

        super().__init__(fspath, parent)
        self._doc = yaml.safe_load(self.fspath.open())
        self._fixtures = self._doc.pop(FIXTURE) if FIXTURE in self._doc else []

    def collect(self):
        for name, spec in sorted(self._doc.items()):
            if name == FIXTURE:
                for fixture in spec:
                    inject_fixture(
                        scope=fixture["scope"],
                        name=fixture["name"],
                        value=fixture["value"],
                    )
            else:
                yield YamlItem.from_parent(self, name=name, spec=spec)


class YamlItem(pytest.Item):
    def __init__(self, name, parent, spec):
        super().__init__(name, parent)
        self.spec = spec

    def runtest(self):
        for name, value in sorted(self.spec.items()):
            if name != value:
                raise YamlException(self, name, value)

    def repr_failure(self, excinfo, **kwargs):
        """called when self.runtest() raises an exception"""
        if isinstance(excinfo.value, YamlException):
            return "\n".join(
                [
                    "use case execution failed",
                    "   spec failed: {1!r}: {2!r}".format(*excinfo.value.args),
                    "   no further details known at this point.",
                ]
            )

    def reportinfo(self):
        return self.fspath, 0, "usecase: {}".format(self.name)


class YamlException(Exception):
    """ custom exception for error reporting. """  # "Python in a Nutshell" suggests using a docstring
