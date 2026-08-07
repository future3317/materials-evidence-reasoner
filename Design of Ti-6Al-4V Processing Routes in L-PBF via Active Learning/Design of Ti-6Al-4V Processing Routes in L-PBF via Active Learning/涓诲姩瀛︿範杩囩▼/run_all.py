# This is a test of query-by-commitee method in Bayesian optimization within
# an active learning loop. The code is written by Shu-Kai Li and Kang Wang
# Please address any questions or comments to kangwang@sjtu.edu.cn

import argparse
import shutil
from datetime import datetime
from pathlib import Path
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Run the bundled active-learning example in an isolated workspace.")
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--output-dir", type=Path, help="Run directory; defaults to runs/run_<timestamp>")
    args = parser.parse_args()

    source_dir = Path(__file__).resolve().parent
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = args.output_dir or source_dir / "runs" / f"run_{timestamp}"
    run_dir = run_dir.resolve()
    if run_dir == source_dir:
        raise ValueError("--output-dir 不能等于输入代码目录")
    run_dir.mkdir(parents=True, exist_ok=False)

    # Copy only executable inputs and the starting records. All generated CSVs
    # then stay inside run_dir, leaving the checked-in example untouched.
    for path in source_dir.glob("*.py"):
        shutil.copy2(path, run_dir / path.name)
    for name in ("labeled.csv", "init_unlabeled.csv"):
        source = source_dir / name
        if source.is_file():
            shutil.copy2(source, run_dir / name)

    os.chdir(run_dir)
    sys.path.insert(0, str(run_dir))
    import BayesianOpt_01_Matern_EHVI
    import BayesianOpt_02_Matern_PI
    import BayesianOpt_03_Matern_UCB
    import BayesianOpt_04_RBF_EHVI
    import BayesianOpt_05_RBF_PI
    import BayesianOpt_06_RBF_PI
    import generate_initial_data
    import run_qbc_6models
    import run_sample_and_update

    # Generate initial unlabeled data and create labeled data only when the
    # isolated workspace did not receive a starting record.
    generate_initial_data.main()

# -----------------------------------------------------------------------------

    total_iter = args.iterations

    for I in range(total_iter):
        # run 6 models of Bayesian optimization with different kernel functions
        # for Gaussian process regression and acquisition functions
        BayesianOpt_01_Matern_EHVI.main()
        BayesianOpt_02_Matern_PI.main()
        BayesianOpt_03_Matern_UCB.main()
        BayesianOpt_04_RBF_EHVI.main()
        BayesianOpt_05_RBF_PI.main()
        BayesianOpt_06_RBF_PI.main()

        # Gather the recommendations and run the sampling step.
        run_qbc_6models.main()
        iteration_dir = run_dir / "iterations" / f"iteration_{I + 1:02d}"
        new_labeled = run_sample_and_update.run(run_dir, iteration_dir)
        # Promote only inside the isolated run workspace for the next cycle.
        shutil.copy2(new_labeled, run_dir / "labeled.csv")

    print(f"完成。输入目录未修改；运行产物保存在: {run_dir}")

