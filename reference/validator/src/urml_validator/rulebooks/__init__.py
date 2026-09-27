"""Bundled rulebooks (RFC-0702, Draft).

This subpackage exists so rulebook YAML files ship as installable package
data. The Python import surface is empty; the rulebook pass
(``urml_validator.rulebook_engine``) loads every ``*.yaml`` here with
``importlib.resources.files("urml_validator.rulebooks")``, sorted by file
name, and applies each one whose ``applies_to`` matches the validation. The
format is specified in spec/layer-1-hal/rulebook.md.
"""
