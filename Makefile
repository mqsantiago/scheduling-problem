profile:
	python3 -m kernprof -lv -p src/main.py src/main.py > profile/profile_$$(date +%Y%m%d%H%M%S).txt

run:
	python3 src/main.py > profile/current.txt

test:
	python3 src/test.py

run_mrcpsp:
	python3 src/mrcpsp.py

profile_mrcpsp:
	python3 -m kernprof -lv -p src/mrcpsp.py src/mrcpsp.py > profile/mrcpsp/profile_$$(date +%Y%m%d%H%M%S).txt