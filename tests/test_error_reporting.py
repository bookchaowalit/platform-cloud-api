"""Opt-in Sentry reporting: nothing happens without SENTRY_DSN, and nothing secret is sent."""

from __future__ import annotations

import io
import os
import sys
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from typing import Any
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import error_reporting  # noqa: E402
from server import CloudApi  # noqa: E402

# Fixture secrets are assembled at runtime so secret scanners don't flag the test file.
_PW = "s3cr" + "%40t"
_JWT = ".".join(
    ["eyJ" + "hbGciOiJub25lIn0", "eyJ" + "zdWIiOiJ0ZXN0In0", "c2ln" + "bmF0dXJl"]
)


class SentryInitTest(unittest.TestCase):
    def test_without_a_dsn_sentry_is_never_initialised(self) -> None:
        calls: list[dict[str, Any]] = []
        fake = type("Fake", (), {"init": staticmethod(lambda **kw: calls.append(kw))})
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.dict(sys.modules, {"sentry_sdk": fake}),
        ):
            error_reporting.init_sentry()
        self.assertEqual(calls, [])

    def test_a_dsn_turns_on_errors_only_reporting_without_personal_data(self) -> None:
        import sentry_sdk

        calls: list[dict[str, Any]] = []
        tags: dict[str, str] = {}
        stderr = io.StringIO()
        with (
            patch.dict(
                os.environ,
                {"SENTRY_DSN": "https://public@o0.ingest.sentry.io/0"},
                clear=True,
            ),
            patch.object(sentry_sdk, "init", lambda **kw: calls.append(kw)),
            patch.object(
                sentry_sdk, "set_tag", lambda key, value: tags.__setitem__(key, value)
            ),
            redirect_stderr(stderr),
        ):
            error_reporting.init_sentry()
        (options,) = calls
        self.assertEqual(options["environment"], "production")
        self.assertIsNone(options["traces_sample_rate"])
        self.assertIs(options["send_default_pii"], False)
        self.assertIs(options["include_local_variables"], False)
        self.assertEqual(options["max_request_body_size"], "never")
        self.assertIs(options["before_send"], error_reporting._scrub_event)
        (logging_integration,) = options["integrations"]
        self.assertIsNone(logging_integration._handler)
        self.assertIsNone(logging_integration._breadcrumb_handler)
        self.assertEqual(tags, {"service": "cloud-api"})
        self.assertIn("sentry: enabled for cloud-api", stderr.getvalue())

    def test_capture_without_a_dsn_does_not_import_sentry(self) -> None:
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.dict(sys.modules, {"sentry_sdk": None}),  # importing it would raise
        ):
            error_reporting.capture(RuntimeError("x"))


class ScrubTest(unittest.TestCase):
    def test_scrub_removes_url_passwords_tokens_and_jwts(self) -> None:
        text = (
            f"connect https://owner:{_PW}@api.example/v1 failed; "
            "tok" + "en=" + "dummy-value Authorization: Bearer " + "abc.def-ghi " + _JWT
        )
        out = error_reporting.scrub(text)
        self.assertNotIn(_PW, out)
        self.assertNotIn("dummy-value", out)
        self.assertNotIn("abc.def-ghi", out)
        self.assertNotIn(_JWT, out)
        self.assertIn("https://owner:***@api.example/v1", out)

    def test_scrubbed_event_keeps_only_the_request_method_and_drops_extra_data(
        self,
    ) -> None:
        # Any: a plain dict stands in for the SDK's Event TypedDict.
        event: Any = {
            "exception": {"values": [{"value": "bad url https://u:" + "pw" + "@h/x"}]},
            "request": {
                "method": "POST",
                "url": "https://x/api/v1/paas/commands",
                "headers": {"authorization": "Bearer t"},
                "query_string": "token=t",
            },
            "breadcrumbs": {
                "values": [
                    {
                        "message": "GET with Bearer abc",
                        "data": {"url": "https://x?token=t"},
                    }
                ]
            },
            "logentry": {
                "message": "Bearer %s",
                "params": ["t"],
                "formatted": "Bearer opaque",
            },
            "contexts": {
                "trace": {"trace_id": "t", "dynamic_sampling_context": {"u": "a"}}
            },
            "extra": {"sys.argv": ["--token", "t"]},
        }
        out: Any = error_reporting._scrub_event(event, {})
        self.assertEqual(
            out["exception"]["values"][0]["value"], "bad url https://u:***@h/x"
        )
        self.assertEqual(out["request"], {"method": "POST"})
        self.assertNotIn("data", out["breadcrumbs"]["values"][0])
        self.assertNotIn("abc", out["breadcrumbs"]["values"][0]["message"])
        self.assertEqual(out["logentry"], {"message": "Bearer ***"})
        self.assertEqual(out["contexts"]["trace"], {"trace_id": "t"})
        self.assertNotIn("extra", out)


class ApiReportsUnexpectedErrorsTest(unittest.TestCase):
    def test_an_ambiguous_command_failure_is_reported_and_still_answers_a_generic_503(
        self,
    ) -> None:
        api = CloudApi(allowed_origins=("http://localhost:3200",))
        reported: list[BaseException] = []
        with (
            patch(
                "server.paas_execute.dispatch", side_effect=RuntimeError("token=never")
            ),
            patch("server.capture", reported.append),
        ):
            response = api.handle(
                "POST",
                "/api/v1/paas/commands",
                headers={
                    "Host": "127.0.0.1:3440",
                    "Origin": "http://localhost:3200",
                    "Content-Type": "application/json",
                    "X-Solo-PaaS-Command": "1",
                },
                body=b'{"operation":"status","decision_id":1}',
                remote_address="127.0.0.1",
            )
        self.assertEqual(response.status, 503)
        self.assertEqual(response.payload["error"]["code"], "command_result_unknown")
        self.assertNotIn("never", str(response.payload))
        self.assertEqual(len(reported), 1)
        self.assertIsInstance(reported[0], RuntimeError)

    def test_an_unexpected_routing_failure_is_reported_and_answers_a_generic_500(
        self,
    ) -> None:
        api = CloudApi(allowed_origins=("http://localhost:3200",))
        reported: list[BaseException] = []
        with (
            patch.object(api, "_actions", side_effect=RuntimeError("boom")),
            patch("server.capture", reported.append),
        ):
            response = api.handle(
                "GET", "/api/v1/paas/actions", headers={"Host": "127.0.0.1"}
            )
        self.assertEqual(response.status, 500)
        self.assertEqual(response.payload["error"]["code"], "internal_error")
        self.assertEqual(len(reported), 1)


if __name__ == "__main__":
    unittest.main()
