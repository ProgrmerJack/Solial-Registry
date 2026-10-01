"""Limited additive-score replay and bounded missing-input diagnostics."""
from fractions import Fraction
from bisect import bisect_right
from .numeric import fields, name, number, require

def config(raw):
    fields(raw, ("version", "variables", "thresholds", "labels"))
    name(raw["version"])
    require(type(raw["variables"]) is list and raw["variables"], "no variables")
    variables = {}
    for variable in raw["variables"]:
        fields(variable, ("name", "weight", "min", "max"))
        key = name(variable["name"])
        require(key not in variables, "duplicate variable")
        weight, lower, upper = (number(variable[k]) for k in ("weight", "min", "max"))
        require(lower <= upper, "inverted variable bounds")
        variables[key] = (weight, lower, upper)
    require(type(raw["thresholds"]) is list, "thresholds must be a list")
    thresholds = [number(x) for x in raw["thresholds"]]
    require(all(a < b for a, b in zip(thresholds, thresholds[1:])),
            "thresholds must be strictly increasing")
    require(type(raw["labels"]) is list, "labels must be a list")
    labels = [name(x) for x in raw["labels"]]
    require(len(labels) == len(thresholds) + 1, "wrong number of labels")
    require(len(set(labels)) == len(labels), "duplicate label")
    return variables, thresholds, labels


def calculate(prepared, values):
    variables, thresholds, labels = prepared
    fields(values, variables)
    lower_score = upper_score = Fraction(0)
    unresolved = False
    for key, (weight, allowed_lower, allowed_upper) in variables.items():
        value = values[key]
        if value is None:
            lower, upper = allowed_lower, allowed_upper
            unresolved = True
        else:
            lower = upper = number(value)
            require(allowed_lower <= lower <= allowed_upper, "input outside bounds")
        a, b = weight * lower, weight * upper
        lower_score += min(a, b)
        upper_score += max(a, b)
    low_index = bisect_right(thresholds, lower_score)
    high_index = bisect_right(thresholds, upper_score)
    return {
        "score_lower": str(lower_score),
        "score_upper": str(upper_score),
        "possible_categories": labels[low_index:high_index + 1],
        "category": None if unresolved else labels[low_index],
        "needs_review": unresolved,
    }


def evaluate(payload):
    fields(payload, ("kind", "config", "records"))
    require(payload["kind"] in ("synthetic", "administrative"), "unknown data kind")
    prepared = config(payload["config"])
    require(type(payload["records"]) is list and payload["records"], "empty records")
    counts = {
        "records": len(payload["records"]), "complete": 0,
        "unresolved": 0, "multi_category_intervals": 0,
        "reference_comparable": 0, "reference_mismatches": 0,
        "reference_excluded_unresolved": 0, "no_reference": 0,
    }
    ids = set()
    for row in payload["records"]:
        fields(row, ("id", "values"), ("reference_category",))
        key = name(row["id"])
        require(key not in ids, "duplicate record id")
        ids.add(key)
        if "reference_category" in row:
            require(row["reference_category"] in prepared[2], "unknown reference category")
        result = calculate(prepared, row["values"])
        if result["needs_review"]:
            counts["unresolved"] += 1
        else:
            counts["complete"] += 1
        if len(result["possible_categories"]) > 1:
            counts["multi_category_intervals"] += 1
        if "reference_category" not in row:
            counts["no_reference"] += 1
        elif result["needs_review"]:
            counts["reference_excluded_unresolved"] += 1
        else:
            counts["reference_comparable"] += 1
            counts["reference_mismatches"] += result["category"] != row["reference_category"]
    denominator = counts["reference_comparable"]
    return {
        "data_kind": payload["kind"],
        "model_version": payload["config"]["version"],
        "counts": counts,
        "reference_category_mismatch_fraction": (
            str(Fraction(counts["reference_mismatches"], denominator))
            if denominator else None),
        "interpretation": "Rule diagnostics only; no measured targeting accuracy or policy effect.",
        "public_release": "Requires separate disclosure review; aggregates are not automatically anonymous.",
    }


