#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This is a test of query-by-commitee method in Bayesian optimization within
# an active learning loop. The code is written by Shu-Kai Li and Kang Wang
# Please address any questions or comments to kangwang@sjtu.edu.cn


"""对 QBC 推荐样本进行采样并写入新的迭代目录。

默认不会覆盖输入目录中的 ``labeled.csv``。这对真实实验尤其重要：
推荐值是待验证的合成目标或模型输出，不能静默改写已有观测记录。
"""

import argparse
import pandas as pd
from pathlib import Path
from datetime import datetime
from test_function import test_function

def run(input_dir: Path, output_dir: Path, qbc_file: Path | None = None) -> Path:
    # 读取当前数据
    labeled_path = input_dir / 'labeled.csv'
    qbc_path = qbc_file or input_dir / 'qbc_recommended.csv'
    df_labeled = pd.read_csv(labeled_path)
    df_qbc = pd.read_csv(qbc_path)
    for column in ('x', 'y', 'z'):
        if column not in df_labeled.columns:
            raise ValueError(f'{labeled_path} 缺少列: {column}')
    for column in ('x', 'y'):
        if column not in df_qbc.columns:
            raise ValueError(f'{qbc_path} 缺少列: {column}')
    
    print(f"当前labeled: {len(df_labeled)} 个样本")
    print(f"QBC推荐: {len(df_qbc)} 个样本")
    
    # 对推荐样本计算z值
    df_qbc['z'] = test_function(df_qbc['x'].values, df_qbc['y'].values)
    
    # 合并到labeled
    df_new = pd.concat([df_labeled, df_qbc[['x', 'y', 'z']]], ignore_index=True)
    
    # 创建输出文件夹；输入目录保持只读语义。
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存新的labeled数据
    output_file = output_dir / 'labeled.csv'
    df_new.to_csv(output_file, index=False)
    
    # 保存采样的样本
    sampled_file = output_dir / 'sampled.csv'
    df_qbc[['x', 'y', 'z']].to_csv(sampled_file, index=False)
    
    print(f"\n采样完成:")
    print(f"  新增样本: {len(df_qbc)} 个")
    print(f"  更新后labeled: {len(df_new)} 个样本")
    print(f"  最佳z: {df_new['z'].max():.4f}")
    print(f"  输出目录: {output_dir}")
    return output_file


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, default=Path(__file__).resolve().parent,
                        help='包含 labeled.csv 和 qbc_recommended.csv 的目录')
    parser.add_argument('--qbc-file', type=Path,
                        help='QBC 推荐文件；不提供时从 --input-dir/qbc_recommended.csv 读取')
    parser.add_argument('--output-dir', type=Path,
                        help='输出目录；默认在输入目录下创建带时间戳的 iterations 子目录')
    args = parser.parse_args()
    output_dir = args.output_dir
    if output_dir is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = args.input_dir / 'iterations' / f'iteration_{timestamp}'
    run(args.input_dir, output_dir, args.qbc_file)

if __name__ == "__main__":
    main()
