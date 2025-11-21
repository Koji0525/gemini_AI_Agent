import psutil # Requires: pip install psutil
import re
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SystemMetricsCollector:
    """
    Collects real-time system metrics (CPU, Memory, Disk).
    Requires 'psutil' library.
    """
    def get_cpu_percent(self, interval=0.1):
        """Returns the current CPU utilization as a percentage."""
        try:
            return psutil.cpu_percent(interval=interval)
        except Exception as e:
            logger.error(f"Failed to get CPU percent: {e}")
            return 0.0

    def get_memory_info(self):
        """Returns memory usage information (total, available, percent, used, free)."""
        try:
            mem = psutil.virtual_memory()
            return {
                'total': mem.total,
                'available': mem.available,
                'percent': mem.percent,
                'used': mem.used,
                'free': mem.free
            }
        except Exception as e:
            logger.error(f"Failed to get memory info: {e}")
            return {'total': 0, 'available': 0, 'percent': 0, 'used': 0, 'free': 0}

    def get_disk_info(self, path='/'):
        """Returns disk usage information for a given path (total, used, free, percent)."""
        try:
            disk = psutil.disk_usage(path)
            return {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            }
        except Exception as e:
            logger.error(f"Failed to get disk info for {path}: {e}")
            return {'total': 0, 'used': 0, 'free': 0, 'percent': 0}

class LogParser:
    """
    Parses various log files to extract relevant information for validation.
    Assumes log entries have a timestamp at the beginning in '%Y-%m-%d %H:%M:%S' format.
    """
    def __init__(self, log_directory):
        self.log_directory = log_directory
        if not os.path.isdir(self.log_directory):
            logger.warning(f"Log directory '{self.log_directory}' does not exist.")

    def _read_log_file(self, log_path):
        """Reads a log file and returns its lines."""
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.readlines()
        except FileNotFoundError:
            logger.warning(f"Log file not found: {log_path}")
            return []
        except Exception as e:
            logger.error(f"Error reading log file {log_path}: {e}")
            return []

    def find_log_files(self, prefix=""):
        """Finds log files in the configured directory with a given prefix."""
        found_files = []
        try:
            for f_name in os.listdir(self.log_directory):
                if f_name.startswith(prefix) and f_name.endswith(".log"):
                    found_files.append(os.path.join(self.log_directory, f_name))
            found_files.sort() # Ensure chronological order for analysis
        except Exception as e:
            logger.error(f"Error finding log files with prefix '{prefix}': {e}")
        return found_files

    def _parse_timestamp(self, line):
        """Extracts and parses the timestamp from a log line."""
        match = re.match(r'^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line)
        if match:
            return datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
        return None

    def parse_system_metrics_from_logs(self, log_paths):
        """
        Parses system metric logs for CPU, memory, and disk usage.
        Expected format: '[TIMESTAMP] INFO - CPU:XX%, Mem:YY%, Disk:/ZZ%'.
        Also looks for 'Process X memory: YYYMB' for leak detection.
        """
        metrics_data = []
        cpu_pattern = re.compile(r'CPU:(\d+\.?\d*)%')
        mem_pattern = re.compile(r'Mem:(\d+\.?\d*)%')
        disk_pattern = re.compile(r'Disk:[^:]*:(\d+\.?\d*)%')
        process_mem_pattern = re.compile(r'Process \w+ memory: (\d+)MB')

        for path in log_paths:
            for line in self._read_log_file(path):
                timestamp = self._parse_timestamp(line)
                if timestamp:
                    entry = {'timestamp': timestamp}
                    cpu_match = cpu_pattern.search(line)
                    mem_match = mem_pattern.search(line)
                    disk_match = disk_pattern.search(line)
                    process_mem_match = process_mem_pattern.search(line)

                    if cpu_match: entry['cpu_percent'] = float(cpu_match.group(1))
                    if mem_match: entry['mem_percent'] = float(mem_match.group(1))
                    if disk_match: entry['disk_percent'] = float(disk_match.group(1))
                    if process_mem_match: entry['process_memory_mb'] = int(process_mem_match.group(1))
                    
                    if len(entry) > 1: # Only add if some metric was found
                        metrics_data.append(entry)
        
        # Sort by timestamp to ensure chronological order
        metrics_data.sort(key=lambda x: x['timestamp'])
        return metrics_data

    def detect_memory_leaks_signatures(self, metrics_data, min_entries=10, trend_threshold=0.05):
        """
        Detects potential memory leaks by looking for a consistent upward trend
        in memory usage (either total or specific process memory).
        `trend_threshold` is the minimum average percentage increase per entry over the period.
        """
        if len(metrics_data) < min_entries:
            return False

        mem_percent_usages = [m['mem_percent'] for m in metrics_data if 'mem_percent' in m]
        process_mem_usages = [m['process_memory_mb'] for m in metrics_data if 'process_memory_mb' in m]

        def check_trend(usages, usage_type):
            if not usages or len(usages) < min_entries:
                return False
            
            # Simple linear regression check
            total_increase = usages[-1] - usages[0]
            if total_increase <= 0:
                return False
            
            # Calculate average increase per data point, relative to initial value
            relative_increase_per_entry = (total_increase / usages[0]) / len(usages) if usages[0] > 0 else 0

            # Check for a positive trend and significant increase
            if relative_increase_per_entry > trend_threshold:
                logger.warning(f"Potential memory leak detected in {usage_type} data: {total_increase:.2f} increase from {usages[0]:.2f} to {usages[-1]:.2f} over {len(usages)} entries.")
                return True
            return False

        if check_trend(mem_percent_usages, 'total system memory'):
            return True
        if check_trend(process_mem_usages, 'specific process memory'):
            return True
        
        return False


    def parse_error_events_from_logs(self, log_paths):
        """
        Parses error logs for 'ERROR' messages, F7, Retry, and F9 actions.
        Expected patterns:
        - `[TIMESTAMP] ERROR - ...`
        - `[TIMESTAMP] INFO - F7_ACTION: ...`
        - `[TIMESTAMP] INFO - RETRY_ATTEMPT: ...`
        - `[TIMESTAMP] INFO - F9_NOTIFICATION: ...`
        """
        error_events = []
        error_pattern = re.compile(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (ERROR|WARN|INFO) - (F7_ACTION|RETRY_ATTEMPT|F9_NOTIFICATION|.*?)(?:\: (.*))?')

        for path in log_paths:
            for line in self._read_log_file(path):
                match = error_pattern.match(line)
                if match:
                    timestamp_str, level, event_type_or_message, detail = match.groups()
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    
                    entry = {
                        'timestamp': timestamp,
                        'level': level,
                        'full_line': line.strip()
                    }
                    
                    if event_type_or_message in ['F7_ACTION', 'RETRY_ATTEMPT', 'F9_NOTIFICATION']:
                        entry['event_type'] = event_type_or_message
                        entry['message'] = detail if detail else event_type_or_message
                    else:
                        entry['event_type'] = 'GENERIC_ERROR' if level == 'ERROR' else 'GENERIC_LOG'
                        entry['message'] = event_type_or_message + (f": {detail}" if detail else "")
                    
                    error_events.append(entry)
        error_events.sort(key=lambda x: x['timestamp'])
        return error_events

    def parse_learning_events_from_logs(self, log_paths):
        """
        Parses learning cycle logs for F8 triggers, knowledge accumulation, and pattern learning.
        Expected patterns:
        - `[TIMESTAMP] INFO - F8_TRIGGERED: ...`
        - `[TIMESTAMP] INFO - KNOWLEDGE_ADDED: ...`
        - `[TIMESTAMP] INFO - PATTERN_LEARNED: ...`
        """
        learning_events = []
        learning_pattern = re.compile(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] INFO - (F8_TRIGGERED|KNOWLEDGE_ADDED|PATTERN_LEARNED): (.*)')
        
        for path in log_paths:
            for line in self._read_log_file(path):
                match = learning_pattern.match(line)
                if match:
                    timestamp_str, event_type, message = match.groups()
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    learning_events.append({
                        'timestamp': timestamp,
                        'event_type': event_type,
                        'message': message.strip(),
                        'full_line': line.strip()
                    })
        learning_events.sort(key=lambda x: x['timestamp'])
        return learning_events

    def parse_api_usage_from_logs(self, log_paths):
        """
        Parses API usage logs for Claude and Google Sheets API calls.
        Expected patterns:
        - `[TIMESTAMP] INFO - API_CALL: Claude, tokens:X, cost:Y`
        - `[TIMESTAMP] INFO - API_CALL: GoogleSheets, requests:Z`
        """
        api_usage_data = []
        api_call_pattern = re.compile(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] INFO - API_CALL: (Claude|GoogleSheets)(?:, tokens:(\d+))?(?:, cost:(\d+\.?\d*))?(?:, requests:(\d+))?')

        for path in log_paths:
            for line in self._read_log_file(path):
                match = api_call_pattern.match(line)
                if match:
                    timestamp_str, api_name, tokens, cost, requests = match.groups()
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    
                    entry = {
                        'timestamp': timestamp,
                        'api_name': api_name,
                        'full_line': line.strip()
                    }
                    if tokens: entry['tokens'] = int(tokens)
                    if cost: entry['cost'] = float(cost)
                    if requests: entry['requests'] = int(requests)
                    api_usage_data.append(entry)
        api_usage_data.sort(key=lambda x: x['timestamp'])
        return api_usage_data

    def find_patterns(self, log_paths, patterns):
        """
        Searches for specific regex patterns across multiple log files.
        Returns a list of matching lines.
        """
        matches = []
        compiled_patterns = [re.compile(p) for p in patterns]
        for path in log_paths:
            for line in self._read_log_file(path):
                for pattern in compiled_patterns:
                    if pattern.search(line):
                        matches.append(line.strip())
                        break # Only record once per line for any matched pattern
        return matches

    def find_patterns_in_data(self, log_lines_data, patterns):
        """
        Searches for specific regex patterns within a list of log lines.
        Returns a list of matching lines.
        """
        matches = []
        compiled_patterns = [re.compile(p) for p in patterns]
        for line in log_lines_data:
            for pattern in compiled_patterns:
                if pattern.search(line):
                    matches.append(line.strip())
                    break
        return matches

    def check_log_rotation(self, log_directory, prefix, retention_days=7):
        """
        Checks if log rotation seems to be working by inspecting dated log files.
        Assumes daily log files like 'prefix_YYYY-MM-DD.log'.
        """
        expected_log_pattern = re.compile(rf'^{prefix}(\d{{4}}-\d{{2}}-\d{{2}}).log$')
        log_files_in_dir = []
        for f_name in os.listdir(log_directory):
            match = expected_log_pattern.match(f_name)
            if match:
                try:
                    log_date = datetime.strptime(match.group(1), '%Y-%m-%d')
                    log_files_in_dir.append((log_date, f_name))
                except ValueError:
                    continue # Not a valid date format
        
        if not log_files_in_dir:
            return "FAIL: No dated log files found matching pattern."

        # Check for presence of recent logs
        latest_log_date = max(d for d, _ in log_files_in_dir)
        if datetime.now().date() - latest_log_date.date() > timedelta(days=1):
            return "WARN: Latest log file is more than one day old, rotation might be delayed or stopped."

        # Check for old logs that should have been removed
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        old_logs_present = [f for d, f in log_files_in_dir if d < cutoff_date]
        
        if old_logs_present:
            return f"WARN: {len(old_logs_present)} log files older than {retention_days} days are still present. Rotation/cleanup might not be working correctly."
        
        return "PASS: Log rotation appears to be working correctly (recent logs present, old logs absent)."


class APITracker:
    """
    Tracks and aggregates API usage data.
    """
    def calculate_total_usage(self, api_usage_data, api_name):
        """
        Calculates total tokens/requests and estimated cost for a specific API.
        """
        total_tokens = 0
        total_cost = 0.0
        total_requests = 0

        for entry in api_usage_data:
            if entry.get('api_name') == api_name:
                total_tokens += entry.get('tokens', 0)
                total_cost += entry.get('cost', 0.0)
                total_requests += entry.get('requests', 0)
        
        if api_name == 'Claude':
            return {'tokens': total_tokens, 'cost': total_cost}
        elif api_name == 'GoogleSheets':
            return {'requests': total_requests}
        return {}

    def check_rate_limits(self, usage_data, max_limit, usage_type='tokens'):
        """
        Checks if the API usage is within the specified daily rate limit.
        """
        current_usage = usage_data.get(usage_type, 0)
        if current_usage > max_limit:
            return f"EXCEEDED ({current_usage}/{max_limit} {usage_type})"
        else:
            return f"Within Limit ({current_usage}/{max_limit} {usage_type})"


class ReportGenerator:
    """
    Generates structured reports from validation results.
    """
    def generate_summary(self, validation_results):
        """
        Generates a summary report from the validation results dictionary.
        """
        report_lines = []
        report_lines.append(f"Validation Run Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        overall_status = "PASS"
        for category, result in validation_results.items():
            if category == "Final Report": continue # Skip self-referencing
            report_lines.append(f"Category: {category}")
            report_lines.append(f"  Status: {result.get('status', 'N/A')}")
            for detail in result.get('details', []):
                report_lines.append(f"    - {detail}")
            report_lines.append("") # Blank line for readability

            if result.get('status') == "FAIL":
                overall_status = "FAIL"
            elif result.get('status') == "WARN" and overall_status == "PASS":
                overall_status = "WARN"
        
        report_lines.append(f"Overall Validation Result: {overall_status}")
        return report_lines

    def generate_detailed_report(self, validation_results):
        """
        Generates a more detailed report (can be extended with more complex formatting
        or output to different formats like HTML/PDF if needed).
        For this task, it's similar to summary but implies potential for more data.
        """
        return self.generate_summary(validation_results) # Placeholder, can be expanded