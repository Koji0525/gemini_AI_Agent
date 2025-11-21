import json
import os
import time
import logging
from datetime import datetime, timedelta
import psutil  # Requires: pip install psutil

from utils import SystemMetricsCollector, LogParser, APITracker, ReportGenerator

# Configure logging for the validator itself
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutonomousSystemValidator:
    """
    Validator for a 24-hour autonomous system, designed for pre-production final checks.
    It analyzes system logs and performs real-time sanity checks to ensure readiness.
    """
    def __init__(self, config_path="config.json"):
        """
        Initializes the validator with configuration from a JSON file.

        Args:
            config_path (str): Path to the configuration file.
        """
        self.config = self._load_config(config_path)
        self.log_directory = self.config.get("log_directory", "logs/")
        os.makedirs(self.log_directory, exist_ok=True) # Ensure log directory exists
        self.validation_results = {}
        logger.info(f"Validator initialized with config from {config_path}")

        # Initialize utility classes
        self.metrics_collector = SystemMetricsCollector()
        self.log_parser = LogParser(self.log_directory)
        self.api_tracker = APITracker()
        self.report_generator = ReportGenerator()

    def _load_config(self, config_path):
        """Loads configuration from a JSON file."""
        if not os.path.exists(config_path):
            logger.error(f"Configuration file not found: {config_path}")
            raise FileNotFoundError(f"Configuration file not found at {config_path}")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            # Validate essential config parameters
            if not all(k in config for k in ["log_directory", "cpu_threshold_percent", 
                                             "memory_threshold_percent", "disk_threshold_percent"]):
                raise ValueError("Missing essential configuration parameters.")
            return config
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding config.json: {e}")
            raise
        except ValueError as e:
            logger.error(f"Invalid configuration: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred loading config: {e}")
            raise

    def _validate_system_stability(self):
        """
        Validates system stability by analyzing past logs for resource usage
        and performs a short real-time check.
        """
        logger.info("Starting system stability validation...")
        results = {"status": "PASS", "details": []}
        
        # 1. Real-time snapshot of current system resources
        try:
            current_cpu = self.metrics_collector.get_cpu_percent()
            current_memory = self.metrics_collector.get_memory_info()
            current_disk = self.metrics_collector.get_disk_info(self.log_directory)

            results["details"].append(f"Current CPU Usage: {current_cpu:.2f}%")
            results["details"].append(f"Current Memory Usage: {current_memory['percent']:.2f}% (Total: {current_memory['total']/(1024**3):.2f} GB)")
            results["details"].append(f"Current Disk Usage ({self.log_directory}): {current_disk['percent']:.2f}% (Free: {current_disk['free']/(1024**3):.2f} GB)")

            if current_cpu > self.config.get("cpu_threshold_percent", 80):
                results["status"] = "WARN"
                results["details"].append(f"WARNING: Current CPU usage {current_cpu:.2f}% exceeds threshold {self.config['cpu_threshold_percent']}%")
            if current_memory['percent'] > self.config.get("memory_threshold_percent", 90):
                results["status"] = "WARN"
                results["details"].append(f"WARNING: Current Memory usage {current_memory['percent']:.2f}% exceeds threshold {self.config['memory_threshold_percent']}%")
            if current_disk['percent'] > self.config.get("disk_threshold_percent", 95):
                results["status"] = "WARN"
                results["details"].append(f"WARNING: Current Disk usage {current_disk['percent']:.2f}% exceeds threshold {self.config['disk_threshold_percent']}%")
            
        except Exception as e:
            results["status"] = "FAIL"
            results["details"].append(f"ERROR during real-time system metrics collection: {e}")
            logger.error(f"Error collecting real-time system metrics: {e}")

        # 2. Analyze past system logs for long-term stability
        system_log_files = self.log_parser.find_log_files(self.config.get("system_log_prefix", "system_"))
        if not system_log_files:
            results["status"] = "FAIL"
            results["details"].append("ERROR: No system log files found to analyze long-term stability.")
            logger.warning("No system log files found.")
        else:
            logger.info(f"Analyzing {len(system_log_files)} system log files for stability...")
            metrics_data = self.log_parser.parse_system_metrics_from_logs(system_log_files)
            
            if metrics_data:
                # Check for 6 hours continuous operation
                start_time = min(m['timestamp'] for m in metrics_data)
                end_time = max(m['timestamp'] for m in metrics_data)
                duration = end_time - start_time
                required_duration = timedelta(hours=self.config.get("long_run_test_duration_hours", 6))

                results["details"].append(f"Logged operation duration: {duration} (Required: {required_duration})")
                if duration < required_duration:
                    results["status"] = "WARN" if results["status"] == "PASS" else results["status"]
                    results["details"].append(f"WARNING: System logs indicate less than {self.config['long_run_test_duration_hours']} hours of continuous operation.")
                else:
                    results["details"].append(f"System operated continuously for {duration}. Meets {required_duration} requirement.")

                # Check for resource usage spikes and memory leaks from logs
                cpu_usages = [m['cpu_percent'] for m in metrics_data if 'cpu_percent' in m]
                mem_usages = [m['mem_percent'] for m in metrics_data if 'mem_percent' in m]
                disk_usages = [m['disk_percent'] for m in metrics_data if 'disk_percent' in m]

                if cpu_usages:
                    max_cpu = max(cpu_usages)
                    if max_cpu > self.config.get("cpu_threshold_percent", 80):
                        results["status"] = "WARN" if results["status"] == "PASS" else results["status"]
                        results["details"].append(f"WARNING: Max logged CPU usage {max_cpu:.2f}% exceeded threshold {self.config['cpu_threshold_percent']}%")
                    results["details"].append(f"Max logged CPU usage: {max_cpu:.2f}%")
                
                if mem_usages:
                    max_mem = max(mem_usages)
                    if max_mem > self.config.get("memory_threshold_percent", 90):
                        results["status"] = "WARN" if results["status"] == "PASS" else results["status"]
                        results["details"].append(f"WARNING: Max logged Memory usage {max_mem:.2f}% exceeded threshold {self.config['memory_threshold_percent']}%")
                    results["details"].append(f"Max logged Memory usage: {max_mem:.2f}%")
                    
                    # Basic memory leak detection: check for consistent upward trend
                    if self.log_parser.detect_memory_leaks_signatures(metrics_data):
                        results["status"] = "FAIL"
                        results["details"].append("CRITICAL: Potential memory leak detected from log analysis (consistent upward trend).")
                
                if disk_usages:
                    max_disk = max(disk_usages)
                    if max_disk > self.config.get("disk_threshold_percent", 95):
                        results["status"] = "WARN" if results["status"] == "PASS" else results["status"]
                        results["details"].append(f"WARNING: Max logged Disk usage {max_disk:.2f}% exceeded threshold {self.config['disk_threshold_percent']}%")
                    results["details"].append(f"Max logged Disk usage: {max_disk:.2f}%")

            else:
                results["status"] = "FAIL"
                results["details"].append("ERROR: No parseable system metrics found in logs.")

        self.validation_results["System Stability"] = results
        logger.info(f"System Stability validation completed with status: {results['status']}")


    def _verify_error_handling(self):
        """
        Verifies error handling mechanisms (F7, retry, F9) by analyzing error logs.
        """
        logger.info("Starting error handling verification...")
        results = {"status": "PASS", "details": []}
        
        error_log_files = self.log_parser.find_log_files(self.config.get("error_log_prefix", "error_"))
        if not error_log_files:
            results["status"] = "WARN"
            results["details"].append("WARNING: No error log files found. Cannot fully verify error handling.")
            logger.warning("No error log files found for error handling verification.")
            self.validation_results["Error Handling"] = results
            return

        error_events = self.log_parser.parse_error_events_from_logs(error_log_files)
        
        f7_count = len([e for e in error_events if e.get('event_type') == 'F7_ACTION'])
        retry_count = len([e for e in error_events if e.get('event_type') == 'RETRY_ATTEMPT'])
        f9_count = len([e for e in error_events if e.get('event_type') == 'F9_NOTIFICATION'])
        
        results["details"].append(f"F7 (Self-healing) actions logged: {f7_count}")
        results["details"].append(f"Retry attempts logged: {retry_count}")
        results["details"].append(f"F9 (Human notification) events logged: {f9_count}")
        
        if f7_count == 0 and retry_count == 0 and f9_count == 0:
            results["details"].append("No error handling events (F7, Retry, F9) observed. This might be good if no errors occurred, but cannot fully confirm functionality without trigger.")
        else:
            # Check if F7 or F9 were triggered following an ERROR
            errors = [e for e in error_events if e.get('level') == 'ERROR']
            if errors:
                results["details"].append(f"Total ERRORs logged: {len(errors)}")
                f7_triggered_after_error = False
                f9_triggered_after_error = False
                retry_triggered_after_error = False

                for error_event in errors:
                    error_time = error_event['timestamp']
                    # Look for F7, Retry, F9 events within a short window after the error
                    for event in error_events:
                        if error_time < event['timestamp'] < error_time + timedelta(minutes=5): # within 5 min
                            if event.get('event_type') == 'F7_ACTION':
                                f7_triggered_after_error = True
                            if event.get('event_type') == 'RETRY_ATTEMPT':
                                retry_triggered_after_error = True
                            if event.get('event_type') == 'F9_NOTIFICATION':
                                f9_triggered_after_error = True
                
                if f7_triggered_after_error:
                    results["details"].append("F7 (Self-healing) observed following at least one error.")
                else:
                    results["status"] = "WARN" if results["status"] == "PASS" else results["status"]
                    results["details"].append("WARNING: No F7 (Self-healing) action observed immediately after any logged ERROR. Check if F7 logic is appropriate.")
                
                if retry_triggered_after_error:
                    results["details"].append("Retry mechanism observed following at least one error.")
                else:
                    results["status"] = "WARN" if results["status"] == "PASS" else results["status"]
                    results["details"].append("WARNING: No Retry attempt observed immediately after any logged ERROR. Check if retry logic is appropriate.")

                if f9_triggered_after_error:
                    results["details"].append("F9 (Human notification) observed following at least one error.")
                else:
                    # This check is tricky. F9 should trigger after multiple failures/retries
                    # For a simple check, we look for F9 after any error
                    results["details"].append("NOTE: F9 (Human notification) not observed immediately after all errors. This might be expected if F9 has specific trigger conditions (e.g., after max retries).")

            else:
                results["details"].append("No 'ERROR' level events found in logs, indicating stable operation during the logged period.")

        self.validation_results["Error Handling"] = results
        logger.info(f"Error Handling verification completed with status: {results['status']}")

    def _verify_learning_cycle(self):
        """
        Verifies the autonomous system's learning cycle (F8, knowledge accumulation, pattern learning).
        """
        logger.info("Starting learning cycle verification...")
        results = {"status": "PASS", "details": []}

        learning_log_files = self.log_parser.find_log_files(self.config.get("learning_log_prefix", "learning_"))
        if not learning_log_files:
            results["status"] = "WARN"
            results["details"].append("WARNING: No learning log files found. Cannot verify F8 and learning cycle.")
            logger.warning("No learning log files found for learning cycle verification.")
            self.validation_results["Learning Cycle"] = results
            return
        
        learning_events = self.log_parser.parse_learning_events_from_logs(learning_log_files)
        
        f8_triggers = [e for e in learning_events if e.get('event_type') == 'F8_TRIGGERED']
        knowledge_added = [e for e in learning_events if e.get('event_type') == 'KNOWLEDGE_ADDED']
        patterns_learned = [e for e in learning_events if e.get('event_type') == 'PATTERN_LEARNED']

        results["details"].append(f"F8 (Self-evolution) triggers logged: {len(f8_triggers)}")
        results["details"].append(f"Knowledge accumulation events logged: {len(knowledge_added)}")
        results["details"].append(f"Pattern learning events logged: {len(patterns_learned)}")

        if not f8_triggers:
            results["status"] = "WARN" if results["status"] == "PASS" else results["status"]
            results["details"].append("WARNING: No F8 (Self-evolution) triggers observed. Check if conditions for F8 (e.g., 6h/50 errors) were met.")
        else:
            results["details"].append("F8 (Self-evolution) triggers were observed.")
        
        if not knowledge_added:
            results["status"] = "WARN" if results["status"] == "PASS" else results["status"]
            results["details"].append("WARNING: No knowledge accumulation events observed. Ensure F8 is correctly accumulating knowledge.")
        else:
            results["details"].append("Knowledge accumulation events were observed.")

        if not patterns_learned:
            results["status"] = "WARN" if results["status"] == "PASS" else results["status"]
            results["details"].append("WARNING: No pattern learning events observed. Ensure F8 is correctly performing pattern learning.")
        else:
            results["details"].append("Pattern learning events were observed.")

        self.validation_results["Learning Cycle"] = results
        logger.info(f"Learning Cycle verification completed with status: {results['status']}")

    def _monitor_api_usage(self):
        """
        Monitors API usage (Claude, Google Sheets) and checks against rate limits.
        """
        logger.info("Starting API usage monitoring...")
        results = {"status": "PASS", "details": []}
        
        api_log_files = self.log_parser.find_log_files(self.config.get("api_log_prefix", "api_"))
        if not api_log_files:
            results["status"] = "WARN"
            results["details"].append("WARNING: No API log files found. Cannot monitor API usage.")
            logger.warning("No API log files found for monitoring.")
            self.validation_results["API Usage"] = results
            return
        
        api_usage_data = self.log_parser.parse_api_usage_from_logs(api_log_files)
        
        claude_usage = self.api_tracker.calculate_total_usage(api_usage_data, 'Claude')
        g_sheets_usage = self.api_tracker.calculate_total_usage(api_usage_data, 'GoogleSheets')

        results["details"].append(f"Claude API Total Tokens Used: {claude_usage.get('tokens', 0)}")
        results["details"].append(f"Claude API Total Cost Est.: ${claude_usage.get('cost', 0):.4f}")
        results["details"].append(f"Google Sheets API Total Requests: {g_sheets_usage.get('requests', 0)}")

        # Check Claude rate limits
        max_claude_daily = self.config.get("max_api_calls_claude_daily")
        if max_claude_daily is not None:
            claude_rate_status = self.api_tracker.check_rate_limits(claude_usage, max_claude_daily, 'tokens')
            results["details"].append(f"Claude API Daily Token Limit ({max_claude_daily}): {claude_rate_status}")
            if "EXCEEDED" in claude_rate_status:
                results["status"] = "FAIL"
        else:
            results["details"].append("No 'max_api_calls_claude_daily' config for Claude API. Skipping rate limit check.")

        # Check Google Sheets rate limits
        max_g_sheets_daily = self.config.get("max_api_calls_g_sheets_daily")
        if max_g_sheets_daily is not None:
            g_sheets_rate_status = self.api_tracker.check_rate_limits(g_sheets_usage, max_g_sheets_daily, 'requests')
            results["details"].append(f"Google Sheets API Daily Request Limit ({max_g_sheets_daily}): {g_sheets_rate_status}")
            if "EXCEEDED" in g_sheets_rate_status:
                results["status"] = "FAIL"
        else:
            results["details"].append("No 'max_api_calls_g_sheets_daily' config for Google Sheets API. Skipping rate limit check.")

        # Rate limit messages from logs (if any)
        rate_limit_warnings = self.log_parser.find_patterns(api_log_files, [r"RATE_LIMIT_EXCEEDED", r"API_ERROR:429"])
        if rate_limit_warnings:
            results["status"] = "FAIL"
            results["details"].append(f"CRITICAL: Rate limit errors detected in API logs ({len(rate_limit_warnings)} occurrences).")
            for warning in rate_limit_warnings[:5]: # Show first 5
                results["details"].append(f"  - {warning}")
        
        self.validation_results["API Usage"] = results
        logger.info(f"API Usage monitoring completed with status: {results['status']}")

    def _check_log_management(self):
        """
        Confirms proper log management, including rotation and critical event logging.
        """
        logger.info("Starting log management verification...")
        results = {"status": "PASS", "details": []}

        log_files = self.log_parser.find_log_files("") # Find all logs
        if not log_files:
            results["status"] = "FAIL"
            results["details"].append("CRITICAL: No log files found in the log directory. Log management cannot be verified.")
            logger.error("No log files found in the specified directory.")
            self.validation_results["Log Management"] = results
            return

        # Log rotation check (assuming daily rotation and retention)
        retention_days = self.config.get("log_retention_days", 7)
        rotation_status = self.log_parser.check_log_rotation(self.log_directory, "system_", retention_days)
        results["details"].append(f"Log rotation check (for 'system_' logs, retention {retention_days} days): {rotation_status}")
        if "FAIL" in rotation_status:
            results["status"] = "WARN" if results["status"] == "PASS" else results["status"]

        # Check for critical events (example: "CRITICAL", "FAILURE", "FATAL")
        critical_event_patterns = self.config.get("critical_log_patterns", ["CRITICAL", "FATAL", "FAILURE", "OUT_OF_MEMORY"])
        all_logs_data = []
        for log_file in log_files:
            all_logs_data.extend(self.log_parser._read_log_file(os.path.join(self.log_directory, log_file)))

        critical_events = []
        for pattern in critical_event_patterns:
            critical_events.extend(self.log_parser.find_patterns_in_data(all_logs_data, [pattern]))

        if critical_events:
            results["status"] = "FAIL"
            results["details"].append(f"CRITICAL: {len(critical_events)} critical events detected in logs.")
            for event in critical_events[:10]: # Log first 10 critical events
                results["details"].append(f"  - {event.strip()}")
        else:
            results["details"].append("No critical events detected in logs.")
        
        # Check for error log notification patterns (e.g. "ERROR_NOTIFICATION_SENT")
        notification_patterns = self.config.get("error_notification_patterns", ["ERROR_NOTIFICATION_SENT", "ALERT_TRIGGERED"])
        notification_events = self.log_parser.find_patterns_in_data(all_logs_data, notification_patterns)
        if notification_events:
            results["details"].append(f"Error notification events logged: {len(notification_events)}")
        else:
            results["status"] = "WARN" if results["status"] == "PASS" else results["status"]
            results["details"].append("WARNING: No error notification patterns found. Ensure critical errors are being notified.")

        self.validation_results["Log Management"] = results
        logger.info(f"Log Management verification completed with status: {results['status']}")

    def _generate_report(self):
        """Generates a final report summarizing all validation results."""
        logger.info("Generating final validation report...")
        overall_status = "PASS"
        report_summary = []

        for category, result in self.validation_results.items():
            report_summary.append(f"--- {category} --- Status: {result['status']}")
            for detail in result['details']:
                report_summary.append(f"  {detail}")
            if result['status'] == "FAIL":
                overall_status = "FAIL"
            elif result['status'] == "WARN" and overall_status == "PASS":
                overall_status = "WARN"
        
        final_report = self.report_generator.generate_summary(self.validation_results)
        final_report.append(f"\n--- Overall Validation Status: {overall_status} ---")
        
        self.validation_results["Final Report"] = {"status": overall_status, "details": final_report}
        logger.info(f"Final report generated. Overall status: {overall_status}")
        print("\n" + "="*80)
        print("                 AUTONOMOUS SYSTEM PRE-PRODUCTION VALIDATION REPORT")
        print("="*80)
        for line in final_report:
            print(line)
        print("="*80)

    def run_validation(self):
        """
        Executes all validation steps required for pre-production final check.
        """
        logger.info("Starting comprehensive autonomous system validation...")
        try:
            self._validate_system_stability()
            self._verify_error_handling()
            self._verify_learning_cycle()
            self._monitor_api_usage()
            self._check_log_management()
            self._generate_report()
            logger.info("Autonomous system validation completed.")
        except Exception as e:
            logger.critical(f"A critical error occurred during validation: {e}", exc_info=True)
            self.validation_results["Critical Error"] = {"status": "FATAL", "details": [f"Validation failed due to a critical error: {e}"]}
            self._generate_report() # Generate report even on critical failure

if __name__ == "__main__":
    # Create a dummy config.json if it doesn't exist for demonstration
    if not os.path.exists("config.json"):
        dummy_config = {
            "log_directory": "logs/",
            "system_log_prefix": "system_",
            "error_log_prefix": "error_",
            "learning_log_prefix": "learning_",
            "api_log_prefix": "api_",
            "cpu_threshold_percent": 80,
            "memory_threshold_percent": 90,
            "disk_threshold_percent": 95,
            "long_run_test_duration_hours": 6,
            "f8_error_count_threshold": 50,
            "f8_time_threshold_hours": 6,
            "max_api_calls_claude_daily": 100000,
            "max_api_calls_g_sheets_daily": 50000,
            "log_retention_days": 7,
            "critical_log_patterns": ["CRITICAL", "FATAL", "FAILURE", "OUT_OF_MEMORY", "EMERGENCY_SHUTDOWN"],
            "error_notification_patterns": ["ERROR_NOTIFICATION_SENT", "ALERT_TRIGGERED", "EMAIL_SENT_F9"]
        }
        with open("config.json", 'w', encoding='utf-8') as f:
            json.dump(dummy_config, f, indent=4)
        logger.info("Created a dummy config.json. Please adjust to your system's needs.")

    # Create dummy log files for demonstration
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    # Dummy system log for 7 hours
    with open(os.path.join(log_dir, f"system_{today.strftime('%Y-%m-%d')}.log"), 'w', encoding='utf-8') as f:
        for i in range(7): # 7 hours of data
            ts = today - timedelta(hours=7-i)
            f.write(f"[{ts.strftime('%Y-%m-%d %H:%M:%S')}] INFO - CPU:{(i*2)%80}%, Mem:{60+(i*5)%30}%, Disk:/dev/sda1:{50+(i*3)%40}%\n")
            # Simulate a memory leak slowly
            f.write(f"[{ts.strftime('%Y-%m-%d %H:%M:%S')}] INFO - Process X memory: {100 + i*10}MB\n") 
    
    # Dummy error log with F7, Retry, F9 events
    with open(os.path.join(log_dir, f"error_{yesterday.strftime('%Y-%m-%d')}.log"), 'w', encoding='utf-8') as f:
        f.write(f"[{yesterday.strftime('%Y-%m-%d %H:%M:%S')}] ERROR - Database connection lost.\n")
        f.write(f"[{yesterday.strftime('%Y-%m-%d %H:%M:%S')}] INFO - RETRY_ATTEMPT: 1 for DB connection.\n")
        f.write(f"[{yesterday.strftime('%Y-%m-%d %H:%M:%S')}] INFO - RETRY_ATTEMPT: 2 for DB connection.\n")
        f.write(f"[{yesterday.strftime('%Y-%m-%d %H:%M:%S')}] INFO - F7_ACTION: Reconnecting to database.\n")
        f.write(f"[{yesterday.strftime('%Y-%m-%d %H:%M:%S')}] ERROR - Failed to process critical task.\n")
        f.write(f"[{yesterday.strftime('%Y-%m-%d %H:%M:%S')}] INFO - F9_NOTIFICATION: Critical task failed, human intervention required. Email sent.\n")
    
    # Dummy learning log
    with open(os.path.join(log_dir, f"learning_{today.strftime('%Y-%m-%d')}.log"), 'w', encoding='utf-8') as f:
        f.write(f"[{today.strftime('%Y-%m-%d %H:%M:%S')}] INFO - F8_TRIGGERED: Conditions met for self-evolution (6h/50 errors).\n")
        f.write(f"[{today.strftime('%Y-%m-%d %H:%M:%S')}] INFO - KNOWLEDGE_ADDED: New rule 'handle_db_timeout' added to knowledge base.\n")
        f.write(f"[{today.strftime('%Y-%m-%d %H:%M:%S')}] INFO - PATTERN_LEARNED: Identified high-load spike pattern.\n")

    # Dummy API log
    with open(os.path.join(log_dir, f"api_{today.strftime('%Y-%m-%d')}.log"), 'w', encoding='utf-8') as f:
        f.write(f"[{today.strftime('%Y-%m-%d %H:%M:%S')}] INFO - API_CALL: Claude, tokens:1000, cost:0.003\n")
        f.write(f"[{today.strftime('%Y-%m-%d %H:%M:%S')}] INFO - API_CALL: Claude, tokens:2000, cost:0.006\n")
        f.write(f"[{today.strftime('%Y-%m-%d %H:%M:%S')}] INFO - API_CALL: GoogleSheets, requests:10\n")
        f.write(f"[{today.strftime('%Y-%m-%d %H:%M:%S')}] INFO - API_CALL: Claude, tokens:500, cost:0.0015\n")

    validator = AutonomousSystemValidator()
    validator.run_validation()