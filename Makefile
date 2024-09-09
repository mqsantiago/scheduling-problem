run:
	python3 src/main.py > executions/runs/run_$$(date +%Y%m%d%H%M%S).txt

experiment_sa:
	python3 src/experiments/sa.py > executions/experiments/sa/sa_$$(date +%Y%m%d%H%M%S).txt

experiment_sr:
	python3 src/experiments/sr.py > executions/experiments/sr/sr_$$(date +%Y%m%d%H%M%S).txt

experiment_hybrid:
	python3 src/experiments/hybrid.py > executions/experiments/hybrid/hybrid_$$(date +%Y%m%d%H%M%S).txt

test:
	python3 src/test.py

profile:
	python3 -m kernprof -lv -p src/main.py src/main.py > profile/profile_$$(date +%Y%m%d%H%M%S).txt

sat:
	./savilerow -sat -sat-family kissat -run-solver examples/main-pb/main-pb.eprime examples/main-pb/j3060_1.param 

sum_experiment_sa:
	awk '/Instance:/ {print $0} /Chains:/ {print $0} /Steps:/ {print $0} /Neighbours Initial N:/ {print $0} /Neighbours Increase Coefficient:/ {print $0} /Temperature Max:/ {print $0} /Temperature Increase Coefficient:/ {print $0} /elapsed/ {print $0}' executions/experiments/sa/* > executions/experiments/sa/info.txt
