from backend.services.pattern_coverage_service import (
    calculate_pattern_coverage
)


def get_weak_patterns():

    patterns = calculate_pattern_coverage()

    patterns.sort(
        key=lambda x: x["coverage"]
    )

    return patterns[:5]