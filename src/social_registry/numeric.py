"""Strict exact-numeric and JSON input validation."""
from fractions import Fraction

def require(condition, message):
    if not condition:
        raise ValueError(message)


def number(value):
    require(type(value) in (str, int), "numbers must be integers or strings")
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError, OverflowError) as error:
        raise ValueError("invalid finite rational number") from error


def fields(value, required, optional=()):
    require(type(value) is dict, "expected an object")
    require(set(required) <= set(value), "missing required fields")
    require(set(value) <= set(required) | set(optional), "unknown fields")


def name(value):
    require(type(value) is str and bool(value.strip()), "expected nonempty text")
    return value


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON field")
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError("nonfinite JSON constant")


