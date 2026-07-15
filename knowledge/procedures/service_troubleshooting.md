# Linux service troubleshooting

When a Linux service is not working, follow these steps:

1. Ask for the exact service name.

2. Check the service status:

   systemctl status SERVICE_NAME

3. Inspect recent logs:

   journalctl -u SERVICE_NAME --since "30 minutes ago"

4. Check whether the service process is running:

   ps aux | grep SERVICE_NAME

5. Check whether the expected port is listening:

   ss -lntup

6. Check available system resources:

   free -h
   df -h

7. Validate the service configuration before restarting it.

8. Restart the service only after identifying a probable cause:

   sudo systemctl restart SERVICE_NAME

9. Verify the service again after the restart.

Do not claim that the service is fixed unless the user provides the command output.