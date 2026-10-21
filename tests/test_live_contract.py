import os
import unittest
from contextlib import redirect_stderr
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from s3_langchain_demo.cli import main
from s3_langchain_demo.live import classify_live


class LiveContractTests(unittest.TestCase):
    def test_classify_live_uses_structured_output_and_checker(self):
        fake_result = SimpleNamespace(
            model_dump=lambda: {
                "route": "facturacion",
                "confidence": "alta",
                "reason": "La solicitud trata de una factura.",
                "escalate": False,
            }
        )

        with patch.dict(
            os.environ,
            {
                "ANTHROPIC_API_KEY": "test-only-placeholder",
                "LANGSMITH_TRACING": "false",
            },
            clear=False,
        ):
            with patch("langchain_anthropic.ChatAnthropic") as chat:
                structured = chat.return_value.with_structured_output.return_value
                structured.invoke.return_value = fake_result

                decision, checked = classify_live(
                    "Necesito corregir el nombre fiscal de mi factura.", version="v1"
                )

        chat.assert_called_once_with(model="claude-haiku-4-5-20251001")
        chat.return_value.with_structured_output.assert_called_once()
        _, kwargs = chat.return_value.with_structured_output.call_args
        self.assertEqual(kwargs["method"], "json_schema")
        self.assertEqual(decision.route, "facturacion")
        self.assertTrue(checked.accepted)
        self.assertFalse(checked.escalate)

    def test_live_provider_failure_is_blocked_without_traceback(self):
        stderr = StringIO()
        with patch(
            "s3_langchain_demo.cli.classify_live",
            side_effect=TimeoutError("provider details must not be shown"),
        ):
            with redirect_stderr(stderr):
                exit_code = main(["live", "--version", "v1", "--case", "E1"])

        message = stderr.getvalue()
        self.assertEqual(exit_code, 2)
        self.assertIn("BLOQUEADO", message)
        self.assertIn("TimeoutError", message)
        self.assertNotIn("Traceback", message)
        self.assertNotIn("provider details must not be shown", message)


if __name__ == "__main__":
    unittest.main()
