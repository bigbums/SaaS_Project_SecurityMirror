import logging
import json
from django.test import TestCase, Client

class LoggingTestSuite(TestCase):
    def setUp(self):
        self.client = Client()
        # Capture logs from the "audit" logger
        self.audit_output = []
        audit_logger = logging.getLogger("audit")

        class AuditListHandler(logging.Handler):
            def emit(inner_self, record):
                self.audit_output.append(record.getMessage())

        self.audit_handler = AuditListHandler()
        audit_logger.addHandler(self.audit_handler)
        audit_logger.setLevel(logging.INFO)

        # Capture logs from the "security" logger
        self.security_output = []
        security_logger = logging.getLogger("security")

        class SecurityListHandler(logging.Handler):
            def emit(inner_self, record):
                self.security_output.append(record.getMessage())

        self.security_handler = SecurityListHandler()
        security_logger.addHandler(self.security_handler)
        security_logger.setLevel(logging.WARNING)

    def tearDown(self):
        logging.getLogger("audit").removeHandler(self.audit_handler)
        logging.getLogger("security").removeHandler(self.security_handler)

    def test_audit_log_contains_correlation_id(self):
        # Hit a non-skipped endpoint
        response = self.client.get("/accounts/login/")
        self.assertIn(response.status_code, [200, 302])

        # Verify audit log entry captured
        self.assertTrue(len(self.audit_output) > 0)

        log_entry = json.loads(self.audit_output[-1])
        self.assertIn("correlation_id", log_entry)
        self.assertNotEqual(log_entry["correlation_id"], "none")
        self.assertEqual(log_entry["path"], "/accounts/login/")

    def test_security_log_on_failed_login(self):
        # Simulate failed login
        response = self.client.post("/accounts/login/", {"username": "bad", "password": "wrong"})
        self.assertIn(response.status_code, [200, 302, 403])

        # Verify security log entry captured
        self.assertTrue(len(self.security_output) > 0)

        # Parse last security log entry
        log_entry = json.loads(self.security_output[-1])
        self.assertIn("correlation_id", log_entry)
        self.assertNotEqual(log_entry["correlation_id"], "none")
        self.assertIn("failed", log_entry["message"].lower())
