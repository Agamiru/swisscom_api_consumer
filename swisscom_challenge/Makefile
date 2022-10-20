# Use `run-test-local` to run application locally

clear-logfiles:
	rm -f beat.log
	rm -f worker.log

bootstrap-app:
	celery -A app beat -l info --pidfile beat_pid -f beat.log --detach
	celery -A app worker -l info --pidfile worker_pid -f worker.log --detach

tests:
	python3 tests.py

kill-daemons:
	kill `cat beat_pid`
	kill `cat worker_pid`


run-test-local: clear-logfiles bootstrap-app tests kill-daemons