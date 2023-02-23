# Project 15th Street
Project 15th Street is an MVP Flask Microservice Project to reduce the cost of importing electricity for homes with 
solar and home energy storage solutions.

This solution is intended to address the recent adoption of the [Net Billing Tariff (NEM 3.0)](https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/demand-side-management/net-energy-metering/nem-revisit/net-billing-tariff) 
in California where the net metering compensation was reduced by about 75%.  In addition to NEM 3.0 changes, green 
homes with solar panels, energy storage, and an electric vehicle (EV) already need to export about 3.7 times more 
electricity to the grid than they import from the grid to break even (based on .2291/kWh import vs. .062/kWh export 
rate).

Another problem for green homes with a Tesla Powerwall and Tesla EV, is the disconnect between the two products.  For 
example, a home can export surplus electricity when the Powerwall is full during the day and will import electricity to 
charge their EV in the evening.  In the simplest case the kWh exported and imported could be equal but based on the 
utility rate the owner will be charged for the balance of the imported electricity after the credit for the exported 
electricity is applied. An owner can manually control when the EV charges and how many amps during the charge.  However,
this is set independent of the Powerwall's current energy level and discharge rate and would require constant 
monitoring to minimize unnecessary grid usage.

# Architecture
This microservice is built over [PyMS](https://github.com/python-microservices/pyms) package. PyMS is a [Microservice chassis pattern](https://microservices.io/patterns/microservice-chassis.html)
like Spring Boot (Java) or Gizmo (Golang). PyMS is a collection of libraries, best practices and recommended ways to build
microservices with Python which handles cross-cutting concerns:
- Externalized configuration
- Logging
- Health checks
- Metrics
- Distributed tracing

[![Build Status](https://travis-ci.org/python-microservices/microservices-scaffold.svg?branch=master)](https://travis-ci.org/python-microservices/microservices-scaffold)
[![Coverage Status](https://coveralls.io/repos/github/python-microservices/microservices-scaffold/badge.svg?branch=master)](https://coveralls.io/github/python-microservices/microservices-scaffold?branch=master)
[![Requirements Status](https://requires.io/github/python-microservices/microservices-scaffold/requirements.svg?branch=master)](https://requires.io/github/python-microservices/microservices-scaffold/requirements/?branch=master)
[![Updates](https://pyup.io/repos/github/python-microservices/microservices-scaffold/shield.svg)](https://pyup.io/repos/github/python-microservices/microservices-scaffold/)
[![Python 3](https://pyup.io/repos/github/python-microservices/microservices-scaffold/python-3-shield.svg)](https://pyup.io/repos/github/python-microservices/microservices-scaffold/)

Dependencies:
- Shares a mariaDB DB with another microservice leveraging https://github.com/tdorssers/TeslaPy to 
pull battery and vehicle data.

# How to run the microservice

## Installation

### Install with virtualenv
```bash
virtualenv --python=python[3.7|3.8] venv
source venv/bin/activate
pip install -r requirements.txt
```

### Install with pipenv
```bash
pip install pipenv
pipenv install
```

#### Advantages over plain pip and requirements.txt
[Pipenv](https://pipenv.readthedocs.io/en/latest/) generates two files: a `Pipfile`and a `Pipfile.lock`.
* `Pipfile`: Is a high level declaration of the dependencies of your project. It can contain "dev" dependencies (usually test related stuff) and "standard" dependencies which are the ones you'll need for your project to function
* `Pipfile.lock`: Is the "list" of all the dependencies your Pipfile has installed, along with their version and their hashes. This prevents two things: Conflicts between dependencies and installing a malicious module.

For a more in-depth explanation please refer to  the [official documentation](https://pipenv.readthedocs.io/en/latest/).

## Start the service
```bash
python manage.py runserver
```
optional arguments:
-p 
: port number.  default is 5000

Alternatively:
```bash
make run
```

### Start Polling
This will pull the latest battery and vehicle data, calculate the new charging_amps, and manage the EV accordingly.

Curl
```
curl -X GET --header 'Accept: application/json' 'http://localhost:5001/project_15th_street/start-poll'
```
Request URL
```
http://localhost:5001/project_15th_street/start-poll
```

## Check the default endpoint

Your default endpoints will be in this url:
```bash
http://localhost:5000/project_15th_street/
```

This URL is set in your `config.yml`:

```yaml
pyms:
  config:
    DEBUG: false
    TESTING: false
    APP_NAME: Template
    APPLICATION_ROOT : /project_15th_street # <!---
```

You can access a [swagger ui](https://swagger.io/tools/swagger-ui/) in the next url:
```bash
http://localhost:5000/project_15th_street/ui/
```

This PATH is set in your `config.yml`:

```yaml
pyms:
  services:
    swagger:
      path: "swagger"
      file: "swagger.yaml"
      url: "/ui/" # <!---
```

Read more info in the documentation page: 
https://microservices-scaffold.readthedocs.io/en/latest/

# Docker
You can dockerize this microservice with these steps:
* Create and push the image

    docker build -t project_15th_street -f Dockerfile .
* Run the image:

    docker run -d -p 5000:5000 project_15th_street
