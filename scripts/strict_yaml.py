"""Parse YAML mappings without silently accepting duplicate keys."""

import re

import yaml


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    loader.flatten_mapping(node)
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in result
        except TypeError as error:
            raise yaml.constructor.ConstructorError(
                None, None, "unhashable mapping key", key_node.start_mark
            ) from error
        if duplicate:
            raise yaml.constructor.ConstructorError(
                None, None, f"duplicate key: {key!r}", key_node.start_mark
            )
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping
)


def load_yaml(text, *, module=False):
    if module:
        lines = text.splitlines()
        sections = [i for i, line in enumerate(lines)
                    if re.fullmatch(r"\[[^\]]+\]", line.strip())]
        if len(sections) != 1 or lines[sections[0]].strip() != "[YAML]":
            raise ValueError("module must contain exactly one [YAML] section")
        header = sections[0]
        if any(line.strip() and not line.lstrip().startswith("#")
               for line in lines[:header]):
            raise ValueError("only comments are allowed before [YAML]")
        # Preserve source line numbers in parser diagnostics.
        text = "\n" * (header + 1) + "\n".join(lines[header + 1:])
    try:
        result = yaml.load(text, Loader=UniqueKeyLoader)
    except yaml.YAMLError as error:
        raise ValueError(str(error)) from error
    if not isinstance(result, dict):
        raise ValueError("YAML root must be a mapping")
    return result
