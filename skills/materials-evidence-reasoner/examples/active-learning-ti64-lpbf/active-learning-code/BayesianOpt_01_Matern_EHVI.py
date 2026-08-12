#!/usr/bin/env python3

# This is a test of query-by-commitee method in Bayesian optimization within
# an active learning loop. The code is written by Shu-Kai Li and Kang Wang
# Please address any questions or comments to kangwang@sjtu.edu.cn

import numpy as np
import pandas as pd
import torch
import warnings
import os
import matplotlib.pyplot as plt
from datetime import datetime
from botorch.models import SingleTaskGP
from botorch.fit import fit_gpytorch_mll
from gpytorch.mlls import ExactMarginalLogLikelihood
from botorch.acquisition import ExpectedImprovement
from gpytorch.kernels import MaternKernel, ScaleKernel

# 数据预处理函数
def normalize_inputs(X, bounds):
    """归一化输入到[0,1]"""
    return (X - bounds[:, 0]) / (bounds[:, 1] - bounds[:, 0])

def standardize_outputs(y):
    """标准化输出到均值0方差1"""
    mean, std = y.mean(), y.std()
    return (y - mean) / std, mean, std

INPUT_BOUNDS = np.array([[-1.5, 1.5], [-0.2, 2.0]])

warnings.filterwarnings('ignore')
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def plot_pareto_front(df_labeled, df_recommended, output_dir):

    # ==============================
    # Müller–Brown potential parameters
    # ==============================
    A = np.array([-200.0, -100.0, -170.0, 15.0])
    a = np.array([-1.0, -1.0, -6.5, 0.7])
    b = np.array([0.0, 0.0, 11.0, 0.6])
    c = np.array([-10.0, -10.0, -6.5, 0.7])
    x0 = np.array([1.0, 0.0, -0.5, -1.0])
    y0 = np.array([0.0, 0.5, 1.5, 1.0])
    
    # ==============================
    # Define Müller–Brown potential
    # ==============================
    def muller_brown_potential(x, y):
        """
        Calculate the Müller–Brown potential:
        V(x,y) = sum_i A_i * exp[a_i(x-x_i)^2 + b_i(x-x_i)(y-y_i) + c_i(y-y_i)^2]
        """
        V = np.zeros_like(x, dtype=float)
        for Ai, ai, bi, ci, x0i, y0i in zip(A, a, b, c, x0, y0):
            dx = x - x0i
            dy = y - y0i
            V += Ai * np.exp(ai * dx**2 + bi * dx * dy + ci * dy**2)
        return V

    x = np.linspace(-1.5, 1.5, 500)
    y = np.linspace(-0.2, 2.0, 500)
    X, Y = np.meshgrid(x, y)
    
    # Calculate potential surface
    Z = muller_brown_potential(X, Y)
    
    # 为了让图更清晰，可以把过高的势能值截断
    Z_plot = np.clip(Z, -200, 100)
    
    # ==============================
    # Plot contour figure
    # ==============================
    plt.figure(figsize=(10, 6))
    
    levels = np.linspace(-200, 100, 41)
    
    # Filled contours
    contour_filled = plt.contourf(X, Y, Z_plot, levels=levels, cmap='viridis')
    
    # Contour lines
    contour_lines = plt.contour(X, Y, Z_plot, levels=levels, colors='k', linewidths=0.5)
    
    # Label contour lines
    plt.clabel(contour_lines, inline=True, fontsize=8, fmt="%.0f")
    
    # Axis labels and title
    plt.xlabel("x", fontsize=12)
    plt.ylabel("y", fontsize=12)
    plt.title("Müller–Brown Potential Contour Plot", fontsize=14)
    
    # Colorbar
    cbar = plt.colorbar(contour_filled)
    cbar.set_label("V(x, y)", fontsize=12)
    
    plt.tight_layout()
    
    plt.scatter(df_labeled['x'], df_labeled['y'], c='lightgray', s=100, edgecolors='black', label='已标注样本')
    plt.scatter(df_recommended['x'], df_recommended['y'], c='red', s=200, marker='*', edgecolors='black', linewidths=2, label='本轮推荐', zorder=5)

    plt.xlim(-1.5, 1.5)
    plt.ylim(-0.2, 2.0)
    # plt.title(f'样本分布 (n={len(df_labeled)}, 最佳z={df_labeled["z"].max():.4f})')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(f'{output_dir}/sample_distribution_1.png', dpi=150, bbox_inches='tight')
    plt.close()

def main():
    print("="*70 + "\nMatern2.5 + EI 贝叶斯优化\n" + "="*70)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"ex_01_output_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    df_labeled = pd.read_csv('labeled.csv')
    df_unlabeled = pd.read_csv('init_unlabeled.csv')
    X_labeled = df_labeled[['x', 'y']].values
    y_labeled = df_labeled['z'].values
    X_unlabeled = df_unlabeled[['x', 'y']].values
    print(f"\n已标注: {len(X_labeled)}, 候选: {len(X_unlabeled)}, 最佳z: {y_labeled.max():.6f}")
    df_labeled.to_csv(f'{output_dir}/labeled_snapshot.csv', index=False)
    X_labeled_norm = normalize_inputs(X_labeled, INPUT_BOUNDS)
    X_unlabeled_norm = normalize_inputs(X_unlabeled, INPUT_BOUNDS)
    y_labeled_std, _, _ = standardize_outputs(y_labeled)
    X_train = torch.tensor(X_labeled_norm, dtype=torch.float64)
    y_train = torch.tensor(y_labeled_std, dtype=torch.float64).unsqueeze(-1)
    X_pool = torch.tensor(X_unlabeled_norm, dtype=torch.float64)
    print("训练GP模型...")
    covar_module = ScaleKernel(MaternKernel(nu=2.5, ard_num_dims=X_train.shape[-1]))
    model = SingleTaskGP(X_train, y_train, covar_module=covar_module)
    mll = ExactMarginalLogLikelihood(model.likelihood, model)
    fit_gpytorch_mll(mll)
    best_f = y_train.max().item()
    acq = ExpectedImprovement(model, best_f=best_f, maximize=True)
    with torch.no_grad():
        acq_values = acq(X_pool.unsqueeze(1)).numpy()
    top10_idx = np.argsort(acq_values)[-10:][::-1]
    recommended = df_unlabeled.iloc[top10_idx].copy()
    recommended['acquisition_value'] = acq_values[top10_idx]
    # recommended.to_csv('recommended.csv', index=False)
    recommended.to_csv(f'{output_dir}/recommended_1.csv', index=False)
    recommended.to_csv('./recommended_1.csv', index=False)

    plot_pareto_front(df_labeled, recommended, output_dir)
    print(f"\n推荐10个样本，输出文件夹: {output_dir}")

if __name__ == "__main__":
    main()
