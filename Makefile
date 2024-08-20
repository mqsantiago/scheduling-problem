profile:
	python3 -m kernprof -lv -p src/main.py src/main.py > profile/profile_$$(date +%Y%m%d%H%M%S).txt

run:
	python3 src/main.py > profile/current.txt

test:
	python3 src/test.py

run_main:
	python3 src/main.py

profile_main:
	python3 -m kernprof -lv -p src/main.py src/main.py > profile/main/profile_$$(date +%Y%m%d%H%M%S).txt


sat:
	./savilerow -sat -sat-family kissat -run-solver examples/main-pb/main-pb.eprime examples/main-pb/j3060_1.param 
