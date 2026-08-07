#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This is a test of query-by-commitee method in Bayesian optimization within
# an active learning loop. The code is written by Shu-Kai Li and Kang Wang
# Please address any questions or comments to kangwang@sjtu.edu.cn


"""对QBC推荐样本进行采样并更新labeled数据"""

import pandas as pd
import os
from datetime import datetime
from test_function import test_function

def main():
    # 读取当前数据
    df_labeled = pd.read_csv('labeled.csv')
    df_qbc = pd.read_csv('qbc_recommended.csv')
    
    print(f"当前labeled: {len(df_labeled)} 个样本")
    print(f"QBC推荐: {len(df_qbc)} 个样本")
    
    # 对推荐样本计算z值
    df_qbc['z'] = test_function(df_qbc['x'].values, df_qbc['y'].values)
    
    # 合并到labeled
    df_new = pd.concat([df_labeled, df_qbc[['x', 'y', 'z']]], ignore_index=True)
    
    # 创建输出文件夹
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"iteration_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存新的labeled数据
    output_file = os.path.join(output_dir, 'labeled.csv')
    output_file = os.path.join('labeled.csv')
    df_new.to_csv(output_file, index=False)
    
    # 保存采样的样本
    sampled_file = os.path.join(output_dir, 'sampled.csv')
    df_qbc[['x', 'y', 'z']].to_csv(sampled_file, index=False)
    
    print(f"\n采样完成:")
    print(f"  新增样本: {len(df_qbc)} 个")
    print(f"  更新后labeled: {len(df_new)} 个样本")
    print(f"  最佳z: {df_new['z'].max():.4f}")
    print(f"  输出目录: {output_dir}")

if __name__ == "__main__":
    main()

