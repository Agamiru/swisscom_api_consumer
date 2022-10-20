## A CONSISTENT API CONSUMER
This application implements a safe API consumer on an eventually conistent system.

## How It Works
- It stores inconsitent group Id's (key) and hosts (value) on a Redis database i.e. {groupId: [host1, host2, host3]}.
- It then uses this data to decide how to make GET and POST requests.
- A scheduler runs a task every 10s to attempt to delete inconsistent group Id's on Redis.
- API consumer will always get a consistent response across all nodes even when the system
is in an inconsistent state.

## Components
- A Connector class (for making requests).
- A task scheduler and worker.
- A Flask server that uses multiple endpoints and databases to mimic different nodes.

## Depenedencies
- Docker
- Python >= 3.8

## How To Run Application using Docker
- Ensure docker exists on your machine.
- Change directory to root (of this application).
- if necessary, run `chmod u+x test.sh` to enable permissions to run this script.
- Run `./test.sh`

## How To Run Application without Docker
- Open two terminals, one for the test script and the other for the server.
- Change directory to root folder based on the terminal your in.
- Create a virtual enviornment `python3 -m venv venv` and install packages `pip install -r requirements.txt`.
- Do this on both terminals.
- On the server terminal run `make runserver`.
- On the test script terminal run `make run-test-local`

