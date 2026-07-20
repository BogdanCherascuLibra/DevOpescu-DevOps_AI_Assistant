# Network troubleshooting

Use this procedure when a host, service, container, endpoint, port, DNS name, or remote dependency cannot be reached.

## Information to request

Ask for:

- the source host;
- the destination hostname or IP;
- the expected port and protocol;
- the exact error, such as timeout, connection refused, DNS failure, or TLS error;
- whether the issue affects one host or multiple hosts;
- whether the environment is development, staging, or production.

## Initial diagnosis

Start with no more than three steps.

### 1. Check local addressing and routes

```bash
ip addr
ip route
```

Use these to verify the local interface, address, default route, and expected network path.

Ask for only the relevant interface and route output when the output is large.

### 2. Test name resolution

For a hostname:

```bash
getent hosts HOSTNAME
```

If DNS-specific details are needed:

```bash
dig HOSTNAME
```

Do not assume that successful DNS resolution means the service is reachable.

### 3. Test the target endpoint

For HTTP or HTTPS:

```bash
curl -v URL
```

For a TCP port:

```bash
nc -vz HOST PORT
```

If `nc` is unavailable, use another installed tool rather than assuming installation.

## Interpret common outcomes

### Connection refused

Usually indicates that:

- the host is reachable;
- nothing is listening on the target port;
- the service is bound to another interface;
- a local firewall actively rejected the connection.

Check the destination host:

```bash
ss -lntup
```

### Timeout

May indicate:

- firewall filtering;
- routing problems;
- an unreachable host;
- security group or network policy restrictions;
- a stalled service.

Do not assume the firewall is the cause without evidence.

### DNS failure

Check:

```bash
resolvectl status
cat /etc/resolv.conf
```

Use the command appropriate for the system.

Compare resolution using the configured resolver and, only when appropriate, a known external resolver.

### HTTP 4xx or 5xx

The network path may already be working.

Inspect:

- response headers;
- reverse proxy logs;
- application logs;
- upstream service status.

### TLS errors

Check:

- hostname mismatch;
- certificate validity;
- certificate chain;
- system time;
- proxy or load balancer configuration.

Do not recommend disabling certificate verification as a permanent fix.

## Follow-up diagnosis

Choose only checks relevant to the evidence.

### Listening ports

```bash
ss -lntup
```

Prefer filtering for a known port:

```bash
ss -lntup | grep ':PORT'
```

### Routing path

```bash
traceroute HOST
```

Or:

```bash
tracepath HOST
```

Explain that intermediate devices may block or ignore tracing packets.

### Firewall

Use the tool configured on the host, such as:

```bash
sudo ufw status
sudo nft list ruleset
sudo iptables -S
```

Do not modify firewall rules before identifying the exact required traffic.

### Containers

Check:

```bash
docker network ls
docker inspect CONTAINER_NAME
docker port CONTAINER_NAME
```

Verify port publishing, network membership, DNS, and service binding.

### Cloud networking

Check:

- security groups;
- network security rules;
- route tables;
- load balancer health checks;
- private versus public addressing;
- network policies.

Do not claim access to cloud configuration unless the user provides it.

## Corrective actions

Make the smallest change supported by evidence.

Potentially disruptive actions include:

- changing firewall rules;
- modifying routes;
- restarting networking;
- changing DNS configuration;
- exposing a new port;
- changing load balancer or security group rules.

Warn the user and request confirmation before changing production networking.

## Verification

Repeat the exact failing test after the change:

```bash
curl -v URL
nc -vz HOST PORT
getent hosts HOSTNAME
```

Also verify the service from the original source host.

Do not claim the issue is fixed until the original connection succeeds.