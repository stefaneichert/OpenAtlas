from typing import Any, Union

from flask import g

from openatlas.api.v03.resources.error import WrongOperatorError
from openatlas.api.v03.resources.search.search_validation import \
    check_if_date, check_if_date_search
from openatlas.api.v03.resources.util import flatten_list_and_remove_duplicates
from openatlas.models.entity import Entity
from openatlas.models.type import Type


def search(
        entities: list[Entity],
        parser: list[dict[str, Any]]) -> list[Entity]:
    parameter = [get_search_parameter(p) for p in parser]
    return [e for e in entities if iterate_through_entities(e, parameter)]


def get_search_parameter(parser: dict[str: Any]) -> dict[str, Any]:
    parameter = {}
    for category, values in parser.items():
        for i in values:
            parameter.update({
                "search_values": get_search_values(category, i["values"]),
                "logical_operator": i['logicalOperator']
                    if 'logicalOperator' in i else 'or',
                "operator": i['operator'],
                "category": category,
                "is_date": check_if_date_search(category)})
    return parameter


def get_search_values(
        category: str,
        values: list[Union[str, int]]) -> list[Union[str, int]]:
    if category in ["typeIDWithSubs"]:
        values += flatten_list_and_remove_duplicates(
            [get_sub_ids(value, []) for value in values])
    return values


def get_sub_ids(id_: int, subs: list[Any]) -> list[Any]:
    new_subs = Type.get_all_sub_ids(g.types[id_])
    subs.extend(new_subs)
    for sub in new_subs:
        get_sub_ids(sub, subs)
    return subs


def iterate_through_entities(
        entity: Entity,
        parameter: list[dict[str, Any]]) -> bool:
    return bool([p for p in parameter if search_result(entity, p)])


def search_result(entity: Entity, parameter: dict[str, Any]) -> bool:
    return bool(search_entity(
        entity_values=value_to_be_searched(entity, parameter['category']),
        operator_=parameter['operator'],
        search_values=parameter['search_values'],
        logical_operator=parameter['logical_operator'],
        is_date=parameter['is_date']))


def search_entity(
        entity_values: Any,
        operator_: str,
        search_values: list[Any],
        logical_operator: str,
        is_date: bool) -> bool:
    if not entity_values and is_date:
        return False
    if operator_ == 'equal':
        if logical_operator == 'or':
            return bool(any(item in entity_values for item in search_values))
        if logical_operator == 'and':
            return bool(all(item in entity_values for item in search_values))
    if operator_ == 'notEqual':
        if logical_operator == 'or':
            return bool(
                not any(item in entity_values for item in search_values))
        if logical_operator == 'and':
            return bool(
                not all(item in entity_values for item in search_values))
    if operator_ == 'greaterThan' and is_date:
        if logical_operator == 'or':
            return bool(any(item < entity_values for item in search_values))
        if logical_operator == 'and':
            return bool(all(item < entity_values for item in search_values))
    if operator_ == 'greaterThanEqual' and is_date:
        if logical_operator == 'or':
            return bool(any(item <= entity_values for item in search_values))
        if logical_operator == 'and':
            return bool(all(item <= entity_values for item in search_values))
    if operator_ == 'lesserThan' and is_date:
        if logical_operator == 'or':
            return bool(any(item > entity_values for item in search_values))
        if logical_operator == 'and':
            return bool(all(item > entity_values for item in search_values))
    if operator_ == 'lesserThanEqual' and is_date:
        if logical_operator == 'or':
            return bool(any(item >= entity_values for item in search_values))
        if logical_operator == 'and':
            return bool(all(item >= entity_values for item in search_values))
    raise WrongOperatorError


def value_to_be_searched(entity: Entity, key: str) -> Any:
    if key == "entityID":
        return [entity.id]
    if key == "entityName":
        return entity.name
    if key == "entityAliases":
        return list(value for value in entity.aliases.values())
    if key == "entityCidocClass":
        return [entity.cidoc_class.code]
    if key == "entitySystemClass":
        return [entity.class_.name]
    if key == "typeName":
        return [node.name for node in entity.types]
    if key in ["typeID", "typeIDWithSubs"]:
        return [node.id for node in entity.types]
    if key == "beginFrom":
        return check_if_date(str(entity.begin_from))
    if key == "beginTo":
        return check_if_date(str(entity.begin_to))
    if key == "endFrom":
        return check_if_date(str(entity.end_from))
    if key == "endTo":
        return check_if_date(str(entity.end_to))
