import os
import sys

from tuning.sell_pattern.hyo_tuning_manager import SellPatternTuner

current_dir = os.path.dirname(os.path.abspath(__file__))
current_dir = current_dir.replace("/tuning/sell_pattern", "")
os.chdir(current_dir)
sys.path.insert(0, current_dir)

def main():
    tuner = SellPatternTuner()
    # patterns_to_tune = list(tuner.patterns.keys())
    patterns_to_tune = ['BearDvg2']
    results = tuner.tune_multiple_patterns(patterns_to_tune, max_evals=1000)
    # results = tuner.tune_multiple_patterns(['BearDvgVNI'], max_evals=1000)

    print(f"\nTuning patterns: {patterns_to_tune}")
    print("\nFinal results:", results)


if __name__ == "__main__":
    main()
