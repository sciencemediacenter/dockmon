<div id="header" align="center">
  <img src="https://media.sciencemediacenter.de/static/img/logos/smc/smc-logo-typo-bw-big.png" width="300"/>

  <div id="badges" style="padding-top: 20px">
    <a href="https://www.sciencemediacenter.de">
      <img src="https://img.shields.io/badge/Website-orange?style=plastic" alt="Website Science Media Center"/>
    </a>
    <a href="https://lab.sciencemediacenter.de">
      <img src="https://img.shields.io/badge/Website (SMC Lab)-grey?style=plastic" alt="Website Science Media Center Lab"/>
    </a>
    <a href="https://twitter.com/smc_germany_lab">
      <img src="https://img.shields.io/badge/Twitter-blue?style=plastic&logo=twitter&logoColor=white" alt="Twitter SMC Lab"/>
    </a>
  </div>
</div>



<h1>
  DockMon
</h1>

DockMon is a simple logfile monitoring solution for applications in Docker containers. It enables efficient monitoring of applications in containers based on keywords. Alerts are sent to a desired channel via the Slack API. 

We developed this software because we were less interested in the metrics of the containers and more interested in the state of the applications within the containers. We have a lot of small services running in our infrastructure, most of which we developed ourselves. We therefore needed a way to provide simple monitoring for these services. 

DockMon will of course not replace a full monitoring solution and should therefore be used with caution in small Docker environments as a supplement. 

## Usage

To monitor containers, DockMon uses Docker Labels, which allow individual monitoring of individual containers.
DockMon itself uses the Docker socket and runs as a daemon. Its configuration runs via environment variables.

DockMon searches for containers with the appropriate DockMon labels every 60 seconds and adds them to the active monitoring cycle or removes them if the container disappears. 

### Build

Build DockMon using the provided Dockerfile. 

```shell
docker build -t dockmon:latest .
```

### Supported environment variables for DockMon configuration

DockMon is configured via environment variables. They must be available when the container is started. All variables are required. 

```
DOCKMON_CONFIG_GRACEPERIOD=3600                          # Grace Periord for Alerts in Seconds
DOCKMON_CONFIG_SLACK_TOKEN="SLACKTOKEN"                  # Slack-API Token
DOCKMON_CONFIG_SLACK_CHANNEL="SLACKCHANNEL"              # Slack Channel to alert to.
```

### Supported Labels for monitored containers

These are the container labels you can use to monitor a container through DockMon. 

```
io.smclab.dockmon.enabled: true                          # Enables Dockmon Monitoring for this Container

io.smclab.dockmon.monitoring.logs: true                  # Enables Logfile Monitoring
io.smclab.dockmon.monitoring.logs.include: "error, ..."  # Words to look for in the Log, COMMA SEPERATED!
io.smclab.dockmon.monitoring.logs.exclude: "test, ..."   # Do not alert, if one of theses words are included
io.smclab.dockmon.monitoring.logs.since: 60              # Get the Logs of the last X seconds, defaults to 60
io.smclab.dockmon.monitoring.logs.casesensitive: true    # Case Sensitive Monitoring
io.smclab.dockmon.monitoring.logs.checkinterval: 60      # Check Logs every X seconds, defaults to 60
```

### Run

```shell
docker run -d  \
    --restart unless-stopped \
    --name "dockmon" \
    -v "/var/run/docker.sock:/var/run/docker.sock" \
    -e DOCKMON_CONFIG_GRACEPERIOD=3600 \
    -e DOCKMON_CONFIG_SLACK_TOKEN="SLACKTOKEN" \
    -e DOCKMON_CONFIG_SLACK_CHANNEL="SLACKCHANNEL" \  
    dockmon:latest python3.8 /opt/dockmon/src/run.py
```

### Sample Docker-Compose File

If you want to try DockMon, you can find a Docker Compose file below that creates a small test environment. This also helps as a template for configuring a production deployment. 

You can provoke an alert using _docker exec dockmon_bash bash -c 'echo error > /proc/1/fd/1'_

```
version: '3'

services:
  dockmon_test:
    build:
      context: .
    container_name: dockmon_test
    environment:
      - DOCKMON_CONFIG_GRACEPERIOD=3600
      - DOCKMON_CONFIG_SLACK_TOKEN=SLACKTOKEN
      - DOCKMON_CONFIG_SLACK_CHANNEL=#SLACKCHANNEL           # Note: The # must be supplied
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command: >
      python3.8 /opt/dockmon/dockmon.py

  bash_test:
    image: bash:4.4
    container_name: dockmon_bash
    labels:
      io.smclab.dockmon.enabled: true                          # Enables Dockmon Monitoring for this Container
      io.smclab.dockmon.monitoring.logs: true                  # Enables Logfile Monitoring
      io.smclab.dockmon.monitoring.logs.include: "error, ..."  # Words to look for in the Log
      io.smclab.dockmon.monitoring.logs.exclude: "test, ..."   # Do not alert, if one of theses words are included
      io.smclab.dockmon.monitoring.logs.since: 60              # Get the Logs of the last X seconds, defaults to 60
      io.smclab.dockmon.monitoring.logs.casesensitive: true    # Case Sensitive Monitoring, defaults to true
      io.smclab.dockmon.monitoring.logs.checkinterval: 60      # Check Logs every X seconds, defaults to 60
      
    command: sleep infinity
```

## Known Issues

Currently, DockMon only monitors log files inside containers that write via stdout. So everything that is readable via _docker logs_. 
Therefore, all containers or their applications must write to stdout in order to be monitored effectively. 

## Planned Features

We would like to extend DockMon with additional monitoring methods. Imaginable would be methods for monitoring container size or network traffic. We would also like to extend the reporting capabilities to send alerts via email, for example.

Sadly, we currently do not have full test coverage. We would like to cover DockMon with full tests soon to prove the functionality and to be able to develop extensions in a more stable way. DockMon should still be safe to use. 

## Contribute

If you would like to participate in the development of DockMon, we would be very happy to hear from you. Unfortunately our resources are limited, so we can't fully maintain this app. Bug fixes and the like will of course still be taken care of by us, as we also use DockMon in our own systems. 

For development, we use Visual Studio Code Remote Containers for which you can find a configuration file inside this repo. Also use the _locale.sh_ script to generate new i18n files (We use pybabel for this). 

We are looking forward to your pull request. 

## Licence

DockMon is licensed under GPL-3 and a copy of this license is included in the repository. 
