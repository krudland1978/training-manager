import pytest
from lib.utils.csv_parser import ParseResult, parse_csv, parse_pipe_list


def csv_bytes(*lines: str) -> bytes:
    return "\n".join(lines).encode("utf-8")


class TestParseCsv:
    def test_valid_csv_returns_all_rows(self):
        content = csv_bytes(
            "name,email,grade_level",
            "Alice,alice@co.com,7",
            "Bob,bob@co.com,5",
        )
        result = parse_csv(content, ["name", "email", "grade_level"])
        assert len(result.rows) == 2
        assert len(result.errors) == 0
        assert result.rows[0]["name"] == "Alice"

    def test_missing_required_column_raises(self):
        content = csv_bytes("name,email", "Alice,alice@co.com")
        with pytest.raises(ValueError, match="grade_level"):
            parse_csv(content, ["name", "email", "grade_level"])

    def test_row_missing_required_value_goes_to_errors(self):
        content = csv_bytes(
            "name,email,grade_level",
            "Alice,,7",
        )
        result = parse_csv(content, ["name", "email", "grade_level"])
        assert len(result.rows) == 0
        assert len(result.errors) == 1
        assert result.errors[0]["row"] == 2
        assert "email" in result.errors[0]["reason"]

    def test_whitespace_stripped_from_values(self):
        content = csv_bytes("name,grade_level", "  Alice  ,  7  ")
        result = parse_csv(content, ["name", "grade_level"])
        assert result.rows[0]["name"] == "Alice"
        assert result.rows[0]["grade_level"] == "7"

    def test_utf8_bom_handled(self):
        content = b"\xef\xbb\xbfname,grade_level\nAlice,7"
        result = parse_csv(content, ["name", "grade_level"])
        assert len(result.rows) == 1

    def test_multiple_errors_collected(self):
        content = csv_bytes(
            "name,grade_level",
            "Alice,7",
            ",",
            ",",
        )
        result = parse_csv(content, ["name", "grade_level"])
        assert len(result.rows) == 1
        assert len(result.errors) == 2

    def test_optional_columns_not_checked(self):
        content = csv_bytes("name,grade_level,notes", "Alice,7,")
        result = parse_csv(content, ["name", "grade_level"])
        assert len(result.rows) == 1


class TestParsePipeList:
    def test_basic_split(self):
        assert parse_pipe_list("aws-cp|aws-saa") == ["aws-cp", "aws-saa"]

    def test_empty_string(self):
        assert parse_pipe_list("") == []

    def test_whitespace_only(self):
        assert parse_pipe_list("   ") == []

    def test_strips_whitespace_around_items(self):
        assert parse_pipe_list(" aws-cp | aws-saa ") == ["aws-cp", "aws-saa"]

    def test_single_item(self):
        assert parse_pipe_list("aws-cp") == ["aws-cp"]

    def test_empty_segments_ignored(self):
        assert parse_pipe_list("aws-cp||aws-saa") == ["aws-cp", "aws-saa"]
