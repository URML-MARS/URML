"""Bundled rulebooks (RFC-0702, Draft).

This subpackage exists so rulebook YAML files ship as installable package
data. The Python import surface is empty; load rulebook files via
``importlib.resources.files("urml_validator.rulebooks")``. The format is
specified in spec/layer-1-hal/rulebook.md. The validator does not read these
files until the RFC-0702 implementation lands.
"""
