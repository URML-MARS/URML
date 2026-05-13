"""Bundled compliance policies (RFC-0004).

This subpackage exists so policy YAML files ship as installable package
data. The Python import surface is empty; load policy files via
``importlib.resources.files("urml_validator.policies")``.
"""
