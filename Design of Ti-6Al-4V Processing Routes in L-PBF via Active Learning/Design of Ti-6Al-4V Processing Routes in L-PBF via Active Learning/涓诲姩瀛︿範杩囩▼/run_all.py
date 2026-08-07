# This is a test of query-by-commitee method in Bayesian optimization within
# an active learning loop. The code is written by Shu-Kai Li and Kang Wang
# Please address any questions or comments to kangwang@sjtu.edu.cn

import BayesianOpt_01_Matern_EHVI
import BayesianOpt_02_Matern_PI
import BayesianOpt_03_Matern_UCB
import BayesianOpt_04_RBF_EHVI
import BayesianOpt_05_RBF_PI
import BayesianOpt_06_RBF_PI
import generate_initial_data
import run_qbc_6models
import run_sample_and_update

# generate initial unlabeld data (sampling grid) and labeled data (random sampling)
generate_initial_data.main()

# -----------------------------------------------------------------------------

total_iter = 10

for I in range(total_iter):

    # run 6 models of Bayesian optimization with different kernel functions for 
    # Gaussian process regression (GPR) and aquisition functions
    BayesianOpt_01_Matern_EHVI.main()
    BayesianOpt_02_Matern_PI.main()
    BayesianOpt_03_Matern_UCB.main()
    BayesianOpt_04_RBF_EHVI.main()
    BayesianOpt_05_RBF_PI.main()
    BayesianOpt_06_RBF_PI.main()
    
    # gather the recommended unlabeled data from 6 models and recommend top 10
    # most recommended data by QBC
    run_qbc_6models.main()
    
    # sample the space (data acquisition) using recommened data and update the 
    # labeled data
    run_sample_and_update.main()

