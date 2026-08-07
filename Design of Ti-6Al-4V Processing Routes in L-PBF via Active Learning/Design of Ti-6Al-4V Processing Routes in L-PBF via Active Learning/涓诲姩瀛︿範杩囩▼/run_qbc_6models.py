#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This is a test of query-by-commitee method in Bayesian optimization within
# an active learning loop. The code is written by Shu-Kai Li and Kang Wang
# Please address any questions or comments to kangwang@sjtu.edu.cn

"""QBC All-in-One: 合并去重 -> QBC算法"""

import numpy as np
import pandas as pd
import torch
from botorch.models import SingleTaskGP
from botorch.fit import fit_gpytorch_mll
from gpytorch.mlls import ExactMarginalLogLikelihood
from botorch.acquisition import ExpectedImprovement, ProbabilityOfImprovement, UpperConfidenceBound
from gpytorch.kernels import MaternKernel, ScaleKernel, RBFKernel
import os

# ============ 配置 ============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_CONFIG = [
    {"name": "Matern2.5_EI", "kernel": "Matern2.5", "acq": "EI"},
    {"name": "Matern2.5_PI", "kernel": "Matern2.5", "acq": "PI"},
    {"name": "Matern2.5_UCB", "kernel": "Matern2.5", "acq": "UCB", "beta": 1.5},
    {"name": "RBF_EI", "kernel": "RBF", "acq": "EI"},
    {"name": "RBF_PI", "kernel": "RBF", "acq": "PI"},
    {"name": "RBF_UCB", "kernel": "RBF", "acq": "UCB", "beta": 1.5},
]

# ============ Step 1: 合并去重 ============
def merge_and_deduplicate():
    print("\n[Step 1] Merging and deduplicating...")
    all_data = []
    for i in range(1, 7):
        file_path = os.path.join(BASE_DIR, f'./recommended_{i}.csv')
        if os.path.exists(file_path):
            all_data.append(pd.read_csv(file_path))

    merged = pd.concat(all_data, ignore_index=True)
    print(f"  Total before dedup: {len(merged)}")

    feat_cols = ['x', 'y']
    dedup = merged.drop_duplicates(subset=feat_cols, keep='first')

    output = os.path.join(BASE_DIR, 'curr_unlabeled.csv')
    dedup[feat_cols].to_csv(output, index=False)
    print(f"  After dedup: {len(dedup)} (removed {len(merged) - len(dedup)})")
    return output

# ============ Step 2: QBC算法 ============
def normalize_joint(X_train, X_unlabeled):
    """联合归一化：使用训练集和未标注集的共同范围"""
    X_all = np.vstack([X_train, X_unlabeled])
    x_min = X_all.min(axis=0)
    x_max = X_all.max(axis=0)
    X_train_norm = (X_train - x_min) / (x_max - x_min + 1e-8)
    X_unlabeled_norm = (X_unlabeled - x_min) / (x_max - x_min + 1e-8)
    return X_train_norm, X_unlabeled_norm

def standardize(y):
    return (y - y.mean()) / (y.std() + 1e-8)

def train_model(X_train, y_train, X_pool, cfg):
    try:
        if cfg['kernel'] == 'Matern2.5':
            cov = ScaleKernel(MaternKernel(nu=2.5, ard_num_dims=X_train.shape[-1]))
        else:
            cov = ScaleKernel(RBFKernel(ard_num_dims=X_train.shape[-1]))

        model = SingleTaskGP(X_train, y_train, covar_module=cov)
        fit_gpytorch_mll(ExactMarginalLogLikelihood(model.likelihood, model))

        best = y_train.max().item()
        if cfg['acq'] == 'EI':
            acq = ExpectedImprovement(model, best_f=best, maximize=True)
        elif cfg['acq'] == 'PI':
            acq = ProbabilityOfImprovement(model, best_f=best, maximize=True)
        else:
            acq = UpperConfidenceBound(model, beta=cfg['beta'], maximize=True)

        with torch.no_grad():
            return acq(X_pool.unsqueeze(1)).numpy()
    except Exception as e:
        print(f"    Warning: {cfg['name']} failed - {e}")
        return None

def run_qbc(labeled_file, unlabeled_file):
    print("\n[Step 2] Running QBC...")
    df_lab = pd.read_csv(labeled_file)
    df_unlab = pd.read_csv(unlabeled_file)

    X_lab = df_lab[['x', 'y']].values
    y_lab = df_lab['z'].values
    X_unlab = df_unlab[['x', 'y']].values

    print(f"  Labeled: {len(X_lab)}, Unlabeled: {len(X_unlab)}")

    X_lab_norm, X_unlab_norm = normalize_joint(X_lab, X_unlab)

    X_tr = torch.tensor(X_lab_norm, dtype=torch.float64)
    y_tr = torch.tensor(standardize(y_lab), dtype=torch.float64).unsqueeze(-1)
    X_pool = torch.tensor(X_unlab_norm, dtype=torch.float64)

    print(f"  Training {len(MODELS_CONFIG)} models...")
    acq_list = []
    for cfg in MODELS_CONFIG:
        print(f"    {cfg['name']}...", end=' ')
        vals = train_model(X_tr, y_tr, X_pool, cfg)
        if vals is not None:
            acq_list.append(vals)
            print("OK")
        else:
            print("FAILED")

    print(f"  Successfully trained: {len(acq_list)} models")

    acq_mat = np.array(acq_list).T
    variance = acq_mat.var(axis=1)

    top10_idx = np.argsort(variance)[-10:][::-1]
    recommended = df_unlab.iloc[top10_idx].copy()
    recommended['qbc_variance'] = variance[top10_idx]
    
    output = os.path.join(BASE_DIR, 'qbc_recommended.csv')
    recommended.to_csv(output, index=False)
    print(f"\n[Step 3] QBC推荐10个样本，保存到: qbc_recommended.csv")

def main():
    print("="*70 + "\nQBC贝叶斯优化\n" + "="*70)
    unlabeled_file = merge_and_deduplicate()
    labeled_file = os.path.join(BASE_DIR, 'labeled.csv')
    run_qbc(labeled_file, unlabeled_file)

if __name__ == "__main__":
    main()
