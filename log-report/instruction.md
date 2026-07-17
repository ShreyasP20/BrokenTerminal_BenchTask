Analyze /app/access.log and create /app/report.json.

The output must be a valid JSON object containing exactly these fields:

* total_requests: the number of non-empty log entries.
* unique_ips: the number of distinct client IP addresses.
* top_path: the most frequently requested path.

Use the request path from the HTTP request line, such as /index.html or /api/login.

If multiple paths are tied for the highest request count, choose the lexicographically smallest path.

Do not include any additional fields.