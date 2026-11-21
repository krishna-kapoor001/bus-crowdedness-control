import os
import sys
import subprocess
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')
PYTHON_EXE = sys.executable

def run_step(step_num, title, script_name):
    print(f"\n==================================================================")
    print(f"  STEP {step_num}: {title}")
    print(f"==================================================================")
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    t0 = time.time()
    res = subprocess.run([PYTHON_EXE, script_path], cwd=BASE_DIR)
    if res.returncode != 0:
        print(f"\n[ERROR] Step {step_num} failed with exit code {res.returncode}")
        sys.exit(res.returncode)
    print(f"[SUCCESS] Step {step_num} completed in {time.time()-t0:.2f}s")

if __name__ == '__main__':
    t_start = time.time()
    print("******************************************************************")
    print("  FLOWPULSE: Unified End-to-End Pipeline Runner")
    print("  Delhi Transit Stack - Production Pipeline")
    print("******************************************************************")

    # Step 1: Grounded Running On-Board Crowding Pipeline
    run_step(1, "Continuous Running On-Board Crowding Accumulation", "compute_grounded_crowding.py")

    # Step 2: Chronological ML Training & Benchmarks
    run_step(2, "Chronological ML Training & Prior Benchmarks", "train_model.py")

    # Step 3: Week-to-Week Temporal Stability Benchmark (Section 3.3)
    run_step(3, "Week-to-Week Temporal Stability Evaluation", "audit_week_stability.py")

    # Step 4: Database Verification and Seeding
    run_step(4, "Database Persistence & Schema Seeding", "seed_database.py")

    # Step 5: Automated Verification Test Suite
    run_step(5, "Full-Stack Verification & Benchmark Test Suite", "test_backend.py")

    print("\n******************************************************************")
    print(f"  FULL PIPELINE RE-RUN COMPLETED SUCCESSFULLY IN {time.time()-t_start:.2f}s!")
    print("  All deliverables are grounded, verified, and production-ready.")
    print("******************************************************************\n")
