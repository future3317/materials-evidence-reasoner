#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This is a test of query-by-commitee method in Bayesian optimization within
# an active learning loop. The code is written by Shu-Kai Li and Kang Wang
# Please address any questions or comments to kangwang@sjtu.edu.cn


"""生成初始数据（所有方法共享）"""

# generate_initial_data.py

import numpy as np
import pandas as pd
import os
from scipy.stats import qmc

from test_function import test_function

def main():
    x_range, y_range = [-1.5, 1.5], [-0.2, 2.0]
    np.random.seed(0)
    
    # 2个初始点
    x_lab = np.random.uniform(x_range[0], x_range[1], 10)
    y_lab = np.random.uniform(y_range[0], y_range[1], 10)
    z_lab = test_function(x_lab, y_lab)
    
    df_labeled = pd.DataFrame({'x': x_lab, 'y': y_lab, 'z': z_lab})
    
    if not os.path.exists('labeled.csv'):
        df_labeled.to_csv('labeled.csv', index=False)
    
    # 4000个候选点
    sampler = qmc.LatinHypercube(d=2, seed=42)
    samples = sampler.random(n=10000)
    x_unl = samples[:, 0] * (x_range[1] - x_range[0]) + x_range[0]
    y_unl = samples[:, 1] * (y_range[1] - y_range[0]) + y_range[0]
    
    df_pool = pd.DataFrame({'x': x_unl, 'y': y_unl})
    df_pool.to_csv('init_unlabeled.csv', index=False)
    
    print(f"初始数据: {len(df_labeled)} 个样本")
    print(f"候选池: {len(df_pool)} 个样本")
    print(f"初始最佳z: {z_lab.max():.4f}")

if __name__ == "__main__":
    main()
