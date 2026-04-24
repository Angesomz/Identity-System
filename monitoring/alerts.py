class AlertSystem:
    def trigger_alert(self, alert_type: str, details: str):
        print(f"[ALERT] {alert_type}: {details}")
        # Integration with PagerDuty/Slack/Email would go here

    def notify_security_breach(self, source_ip):
        self.trigger_alert("SECURITY_BREACH", f"Suspicious activity from {source_ip}")
