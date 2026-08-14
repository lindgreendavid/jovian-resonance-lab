import pytest

from jovian_resonance_lab.horizons import (
    build_url,
    element_parameters,
    normalized_sha256,
    parse_elements,
    parse_vectors,
    reported_source,
    vector_parameters,
    vector_series_parameters,
)

ELEMENT = """header {source: JUP365}
$$SOE
2451544.5,A,0.1,0,1,2,3,0,0,4,0,5,0,0,
2451545.5,A,0.2,0,2,3,4,0,0,5,0,6,0,0,
$$EOE"""
VECTOR = """header {source: JUP365}\n$$SOE\n2451544.5,A,1,2,3,4,5,6,\n$$EOE"""


def test_parse_elements_and_vectors() -> None:
    elements = parse_elements(ELEMENT)
    assert elements[0].mean_longitude == 9.0
    assert elements[1].semimajor_axis == 6.0
    vector = parse_vectors(VECTOR)[0]
    assert vector.position == (1.0, 2.0, 3.0)
    assert vector.velocity == (4.0, 5.0, 6.0)
    assert reported_source(ELEMENT) == "jup365"


def test_query_shapes_and_hash_are_stable() -> None:
    elements = element_parameters(501, "2001-01-01", "2002-01-01", "1 d")
    assert "COMMAND=%27501%27" in build_url(elements)
    vector = vector_parameters(501, 2451910.5)
    assert vector["REF_PLANE"] == "'F'"
    series = vector_series_parameters(501, "2001-01-01", "2001-01-02", "6 h")
    assert "TLIST" not in series and series["STEP_SIZE"] == "'6 h'"
    assert normalized_sha256([[1.0, 2.0]]) == normalized_sha256([[1, 2]])


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("none", "one reported source"),
        ("{source: a} {source: b}", "one reported source"),
        ("header only", "no ephemeris"),
        ("$$SOE\n$$EOE", "empty"),
    ],
)
def test_malformed_responses_fail(text: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        reported_source(text) if "source" in message else parse_vectors(text)


def test_bad_columns_and_epoch_order_fail() -> None:
    with pytest.raises(ValueError, match="columns"):
        parse_vectors("$$SOE\n1,A,2\n$$EOE")
    duplicate = VECTOR.replace("$$EOE", "2451544.5,A,1,2,3,4,5,6,\n$$EOE")
    with pytest.raises(ValueError, match="strictly"):
        parse_vectors(duplicate)
    with pytest.raises(ValueError, match="element columns"):
        parse_elements("$$SOE\n1,A,2\n$$EOE")
