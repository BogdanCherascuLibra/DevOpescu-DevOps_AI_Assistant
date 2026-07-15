# Docker container troubleshooting

When a Docker container is not working:

1. List all containers:

   docker ps -a

2. Check the container status.

3. Inspect container logs:

   docker logs CONTAINER_NAME

4. Inspect the last 100 log lines:

   docker logs --tail 100 CONTAINER_NAME

5. Inspect the container configuration:

   docker inspect CONTAINER_NAME

6. Check resource usage:

   docker stats

7. Check Docker networks:

   docker network ls

8. Verify environment variables and mounted volumes.

9. Restart the container only after identifying a probable cause:

   docker restart CONTAINER_NAME

10. Verify the container after the restart:

   docker ps
   docker logs --tail 50 CONTAINER_NAME