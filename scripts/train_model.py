#!/usr/bin/env python3
"""训练世界杯专属预测模型。"""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import MODEL_DIR, WC_MODEL_FILENAME
from src.data.wc_training_data import build_wc_training_csv
from src.model.train import train_model


def main():
    parser = argparse.ArgumentParser(description="训练世界杯专属模型")
    parser.add_argument(
        "--output",
        default=str(MODEL_DIR / WC_MODEL_FILENAME),
        help="模型保存路径",
    )
    args = parser.parse_args()

    df = build_wc_training_csv()
    print(f"世界杯训练集: {len(df)} 场 (2018+2022+2026)")

    metrics = train_model(df, model_path=Path(args.output))

    print("\n=== 世界杯模型训练完成 ===")
    print(f"模型: {args.output}")
    print(f"训练样本: {metrics['train_samples']}")
    print(f"测试样本: {metrics['test_samples']}")
    print(f"准确率:   {metrics['accuracy']:.2%}")
    print(f"特征数量: {metrics.get('feature_count', 'N/A')}")
    print("\n分类报告:")
    print(metrics["report"])


if __name__ == "__main__":
    main()
