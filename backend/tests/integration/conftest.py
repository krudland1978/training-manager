import pytest
from unittest.mock import patch


class MockLambdaContext:
    function_name = "test-function"
    function_version = "$LATEST"
    invoked_function_arn = "arn:aws:lambda:eu-west-1:123456789012:function:test-function"
    memory_limit_in_mb = 128
    aws_request_id = "test-request-id"
    log_group_name = "/aws/lambda/test-function"
    log_stream_name = "2026/05/12/[$LATEST]test"

    def get_remaining_time_in_millis(self):
        return 30000


CONTEXT = MockLambdaContext()


def _noop_inject_lambda_context(fn=None, **kwargs):
    """Replace @logger.inject_lambda_context with identity decorator."""
    def decorator(f):
        return f
    if fn is not None:
        return fn
    return decorator


@pytest.fixture(autouse=True)
def patch_lambda_context():
    with patch(
        "aws_lambda_powertools.logging.logger.Logger.inject_lambda_context",
        side_effect=_noop_inject_lambda_context,
    ):
        yield
