Benchmark Report: Clean & Keywords Features
Model: inception
Iterations per config: 3
Summary by ID
| ID | Baseline | Clean | Keywords | Both |
|---|---|---|---|---|
| Q29tbWVudE5vZGU6Mjk1Mjc4NDIz | 2.00 | 5.00 | 2.67 | 4.00 |
| 1194921 | 10.00 | 9.67 | 8.00 | 10.00 |
| 6282093803 | 2.00 | 2.00 | 0.50 | 2.00 |
Overall Averages
| Configuration | Average Score |
|---|---|
| Clean | 5.56 |
| Both | 5.33 |
| Baseline | 4.67 |
| Keywords | 3.72 |
Observations:
- Clean (-clean) provided the best overall performance improvement (+0.89 over baseline).
- Keywords (-experimental) actually degraded performance significantly (-0.95 vs baseline), particularly for sample 6282093803 where the score dropped to 0.50.
- Both features combined performed better than baseline but slightly worse than Clean alone.
The Clean feature appears to be a solid improvement, while the Keywords feature may need refinement as it seems to be removing necessary context in some cases.