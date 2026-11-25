import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import LexerError, tokenize
from parser import ParserError, parse
from semantic import SemanticError, analyze
from intermediate import generate as generate_intermediate
from optimizer import optimize
from code_generator import generate as generate_assembly


PHASE_ORDER = [
    "lexical",
    "syntax",
    "semantic",
    "intermediate",
    "optimization",
    "assembly",
]


def _empty_phases():
    return {
        name: {"status": "skipped"}
        for name in PHASE_ORDER
    }


def _error_payload(exc, error_type, phase_key):
    return {
        "phase": getattr(exc, "phase", phase_key),
        "type": error_type,
        "description": str(exc),
        "line": getattr(exc, "line", None),
        "column": getattr(exc, "column", None),
    }


def compile_code(source):
    phases = _empty_phases()

    try:
        tokens = tokenize(source)
    except LexerError as exc:
        phases["lexical"] = {
            "status": "error",
            "tokens": [],
        }
        return {
            "success": False,
            "error": _error_payload(exc, "ERROR LÉXICO", "lexical"),
            "phases": phases,
        }

    phases["lexical"] = {
        "status": "ok",
        "tokens": [token.to_dict() for token in tokens],
    }

    try:
        tree = parse(tokens)
    except ParserError as exc:
        phases["syntax"] = {
            "status": "error",
            "tree": None,
        }
        return {
            "success": False,
            "error": _error_payload(exc, "ERROR SINTÁCTICO", "syntax"),
            "phases": phases,
        }

    phases["syntax"] = {
        "status": "ok",
        "tree": str(tree),
    }

    try:
        symbol_table = analyze(tree)
    except SemanticError as exc:
        phases["semantic"] = {
            "status": "error",
            "symbol_table": [],
        }
        return {
            "success": False,
            "error": _error_payload(exc, "ERROR SEMÁNTICO", "semantic"),
            "phases": phases,
        }

    phases["semantic"] = {
        "status": "ok",
        "symbol_table": symbol_table.to_rows(),
    }

    intermediate = generate_intermediate(tree)
    phases["intermediate"] = {
        "status": "ok",
        "code": intermediate.to_lines(),
    }

    optimized = optimize(intermediate)
    phases["optimization"] = {
        "status": "ok",
        "before": optimized.before.to_lines(),
        "after": optimized.after.to_lines(),
        "applied": [
            {
                "technique": item.technique,
                "before": item.before,
                "after": item.after,
            }
            for item in optimized.applied
        ],
    }

    assembly = generate_assembly(optimized.after)
    phases["assembly"] = {
        "status": "ok",
        "architecture": assembly.architecture,
        "code": assembly.to_lines(),
    }

    return {
        "success": True,
        "error": None,
        "phases": phases,
    }
