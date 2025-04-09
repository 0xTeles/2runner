Many infrastructures have misconfigurations when using GitHub Actions. Some internal hosts — mainly development tools such as Jenkins, Grafana, and GitLab — require connectivity with GitHub Actions. To enable this, GitHub's IP ranges are often allowed through the VPN, exposing these hosts to the internet.

to use, you need to input github token (with read and workflow permissions) in the "tokens" variable and then, *python3 2runner.py <hosts.txt>*
