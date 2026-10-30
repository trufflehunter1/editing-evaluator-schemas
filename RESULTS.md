# Results

Every reported number, with the script that produced it and its output file. Files are in `results/capcom/` or `results/validation/`. Values are rounded; the files hold full precision. Unless a table says otherwise, ratings use the neutral condition, and a penalty is extreme minus moderate within a pair, as mean (SD) across the 20 pairs.

## Baseline ratings

### Ratings by level

Script: `scripts/baseline_ratings.py`. Output: `results/capcom/baseline_ratings.csv`.

| question | moderate, mean (SD) | extreme, mean (SD) |
|---|---|---|
| capabilities | 6.026 (0.046) | 6.096 (0.108) |
| commitment_org | 5.235 (0.152) | 5.373 (0.159) |
| competence | 6.081 (0.081) | 6.185 (0.140) |
| goals_aligned | 6.078 (0.076) | 6.145 (0.106) |
| offer | 6.116 (0.089) | 6.197 (0.124) |
| stay_if_offer | 3.096 (0.074) | 3.052 (0.080) |

### Share of expected ratings above 6.5

Script: `scripts/baseline_ratings.py`. Output: `results/capcom/baseline_ratings.csv`.

| condition | prompts | share |
|---|---|---|
| all conditions | 2400 | 0.130 |
| commitment_info | 400 | 0.000 |
| mission | 400 | 0.120 |
| neutral | 400 | 0.007 |
| open_options | 400 | 0.000 |
| pay | 400 | 0.000 |
| rejected_options | 400 | 0.652 |

### Digit mass by question

Script: `scripts/baseline_ratings.py`. Output: `results/capcom/baseline_mass.csv`.

| question | mean | min |
|---|---|---|
| offer | 0.994 | 0.989 |
| capabilities | 0.991 | 0.980 |
| competence | 0.986 | 0.974 |
| commitment_org | 0.986 | 0.979 |
| commitment_industry | 0.991 | 0.984 |
| stay | 0.982 | 0.971 |
| extra_hours | 0.985 | 0.979 |
| goals_aligned | 0.992 | 0.983 |
| stay_if_offer | 0.981 | 0.969 |
| turn_down_concern | 0.997 | 0.993 |

### Unedited penalty by condition, mean

Script: `scripts/baseline_ratings.py`. Output: `results/capcom/baseline_penalty.csv`.

| question | commitment_info | mission | neutral | open_options | pay | rejected_options |
|---|---|---|---|---|---|---|
| capabilities | 0.046 | 0.053 | 0.071 | 0.049 | 0.028 | 0.150 |
| commitment_industry | 0.089 | 0.099 | 0.107 | 0.095 | 0.149 | 0.002 |
| commitment_org | 0.073 | 0.018 | 0.138 | 0.162 | 0.101 | 0.029 |
| competence | 0.126 | 0.069 | 0.104 | 0.057 | 0.040 | 0.132 |
| extra_hours | 0.288 | 0.198 | 0.210 | 0.161 | 0.186 | 0.070 |
| goals_aligned | 0.036 | 0.054 | 0.067 | 0.077 | 0.046 | 0.021 |
| offer | 0.043 | 0.088 | 0.081 | 0.013 | 0.055 | 0.005 |
| stay | 0.081 | 0.010 | 0.017 | 0.038 | 0.033 | 0.007 |
| stay_if_offer | 0.038 | 0.000 | -0.045 | -0.019 | 0.001 | 0.040 |
| turn_down_concern | -0.064 | -0.045 | -0.153 | -0.019 | -0.045 | 0.035 |

## Directions

### Cosines between directions (each against neutral sentences)

Script: `scripts/profile_directions.py`. Output: `results/capcom/cosines.csv`.

| pair | est_half_a L8 | est_half_a L13 | est_half_b L8 | est_half_b L13 | estimation L8 | estimation L13 | heldout L8 | heldout L13 |
|---|---|---|---|---|---|---|---|---|
| capability~commitment | 0.070 | 0.076 | 0.084 | 0.088 | 0.081 | 0.084 | 0.069 | 0.063 |
| capability~leaving | 0.027 | 0.030 | 0.048 | 0.035 | 0.039 | 0.033 | 0.022 | 0.024 |
| capability~mission | 0.087 | 0.052 | 0.086 | 0.028 | 0.090 | 0.041 | 0.082 | 0.045 |
| commitment~leaving | 0.761 | 0.744 | 0.760 | 0.743 | 0.761 | 0.743 | 0.761 | 0.744 |
| commitment~mission | 0.731 | 0.656 | 0.730 | 0.659 | 0.730 | 0.657 | 0.730 | 0.656 |
| mission~leaving | 0.709 | 0.691 | 0.708 | 0.692 | 0.709 | 0.691 | 0.709 | 0.691 |

### Stability

Script: `scripts/profile_directions.py`. Output: `results/capcom/stability.csv`.

| layer | direction | cos_estimation_vs_heldout | cos_half_a_vs_half_b |
|---|---|---|---|
| 8 | capability | 0.954 | 0.846 |
| 8 | commitment | 1.000 | 1.000 |
| 8 | mission | 1.000 | 1.000 |
| 8 | leaving | 1.000 | 1.000 |
| 13 | capability | 0.970 | 0.905 |
| 13 | commitment | 1.000 | 1.000 |
| 13 | mission | 1.000 | 1.000 |
| 13 | leaving | 1.000 | 1.000 |

### Word projections

Script: `scripts/profile_directions.py`. Output: `results/capcom/word_projections.csv`.

| layer | direction | list | mean_proj | sd_proj | mean_minus_neutral |
|---|---|---|---|---|---|
| 8 | capability | capability | -21.962 | 0.449 | 0.370 |
| 8 | capability | commitment | -22.296 | 0.501 | 0.036 |
| 8 | capability | neutral | -22.332 | 0.369 | 0.000 |
| 8 | commitment | capability | -14.814 | 0.375 | -0.156 |
| 8 | commitment | commitment | -13.574 | 0.502 | 1.084 |
| 8 | commitment | neutral | -14.657 | 0.600 | 0.000 |
| 8 | mission | capability | 2.003 | 0.496 | -0.643 |
| 8 | mission | commitment | 2.834 | 0.447 | 0.188 |
| 8 | mission | neutral | 2.646 | 0.613 | 0.000 |
| 8 | leaving | capability | -5.423 | 0.297 | -0.526 |
| 8 | leaving | commitment | -5.152 | 0.314 | -0.255 |
| 8 | leaving | neutral | -4.897 | 0.511 | 0.000 |
| 13 | capability | capability | -25.204 | 0.342 | 0.355 |
| 13 | capability | commitment | -25.383 | 0.387 | 0.177 |
| 13 | capability | neutral | -25.559 | 0.523 | 0.000 |
| 13 | commitment | capability | 0.934 | 0.596 | -0.573 |
| 13 | commitment | commitment | 2.614 | 0.882 | 1.107 |
| 13 | commitment | neutral | 1.507 | 0.870 | 0.000 |
| 13 | mission | capability | 31.153 | 0.967 | -1.360 |
| 13 | mission | commitment | 32.387 | 0.884 | -0.125 |
| 13 | mission | neutral | 32.512 | 1.049 | 0.000 |
| 13 | leaving | capability | 6.414 | 0.585 | -0.992 |
| 13 | leaving | commitment | 7.082 | 0.552 | -0.324 |
| 13 | leaving | neutral | 7.406 | 0.743 | 0.000 |

### Correlation of word projections with valence

Script: `scripts/profile_directions.py`. Output: `results/capcom/valence_correlation.csv`.

| layer | direction | n_words | r_proj_valence | p |
|---|---|---|---|---|
| 8 | capability | 52 | 0.028 | 0.845 |
| 8 | commitment | 52 | 0.250 | 0.074 |
| 8 | mission | 52 | 0.302 | 0.030 |
| 8 | leaving | 52 | 0.241 | 0.086 |
| 13 | capability | 52 | -0.146 | 0.302 |
| 13 | commitment | 52 | 0.169 | 0.230 |
| 13 | mission | 52 | 0.411 | 0.002 |
| 13 | leaving | 52 | 0.146 | 0.303 |

### Sentence spread

Script: `scripts/profile_directions.py`. Output: `results/capcom/sentence_spread.csv`.

| layer | reference | set | n | mean_cos_to_set_direction | sd_cos |
|---|---|---|---|---|---|
| 8 | vs_neutral_mean | mission | 40 | 0.836 | 0.032 |
| 8 | vs_neutral_mean | leaving | 40 | 0.757 | 0.057 |
| 8 | vs_neutral_mean | commitment | 40 | 0.769 | 0.042 |
| 8 | vs_grand_mean | mission | 40 | 0.607 | 0.083 |
| 8 | vs_grand_mean | leaving | 40 | 0.477 | 0.120 |
| 8 | vs_grand_mean | commitment | 40 | 0.486 | 0.072 |
| 8 | vs_grand_mean | neutral | 40 | 0.691 | 0.075 |
| 13 | vs_neutral_mean | mission | 40 | 0.873 | 0.039 |
| 13 | vs_neutral_mean | leaving | 40 | 0.789 | 0.055 |
| 13 | vs_neutral_mean | commitment | 40 | 0.808 | 0.040 |
| 13 | vs_grand_mean | mission | 40 | 0.689 | 0.095 |
| 13 | vs_grand_mean | leaving | 40 | 0.517 | 0.131 |
| 13 | vs_grand_mean | commitment | 40 | 0.562 | 0.077 |
| 13 | vs_grand_mean | neutral | 40 | 0.707 | 0.112 |

### Sentence overlap

Script: `scripts/profile_directions.py`. Output: `results/capcom/sentence_overlap.csv`.

| layer | reference | set_a | set_b | mean_cos | sd_cos |
|---|---|---|---|---|---|
| 8 | vs_neutral_mean | mission | mission | 0.690 | 0.065 |
| 8 | vs_neutral_mean | mission | leaving | 0.449 | 0.083 |
| 8 | vs_neutral_mean | mission | commitment | 0.470 | 0.066 |
| 8 | vs_neutral_mean | leaving | leaving | 0.562 | 0.107 |
| 8 | vs_neutral_mean | leaving | commitment | 0.443 | 0.067 |
| 8 | vs_neutral_mean | commitment | commitment | 0.580 | 0.081 |
| 8 | vs_grand_mean | mission | mission | 0.353 | 0.130 |
| 8 | vs_grand_mean | mission | leaving | -0.068 | 0.115 |
| 8 | vs_grand_mean | mission | commitment | -0.045 | 0.093 |
| 8 | vs_grand_mean | mission | neutral | -0.225 | 0.065 |
| 8 | vs_grand_mean | leaving | leaving | 0.208 | 0.181 |
| 8 | vs_grand_mean | leaving | commitment | -0.025 | 0.101 |
| 8 | vs_grand_mean | leaving | neutral | -0.129 | 0.083 |
| 8 | vs_grand_mean | commitment | commitment | 0.217 | 0.134 |
| 8 | vs_grand_mean | commitment | neutral | -0.161 | 0.074 |
| 8 | vs_grand_mean | neutral | neutral | 0.464 | 0.111 |
| 13 | vs_neutral_mean | mission | mission | 0.756 | 0.069 |
| 13 | vs_neutral_mean | mission | leaving | 0.478 | 0.082 |
| 13 | vs_neutral_mean | mission | commitment | 0.465 | 0.074 |
| 13 | vs_neutral_mean | leaving | leaving | 0.612 | 0.101 |
| 13 | vs_neutral_mean | leaving | commitment | 0.474 | 0.067 |
| 13 | vs_neutral_mean | commitment | commitment | 0.643 | 0.077 |
| 13 | vs_grand_mean | mission | mission | 0.461 | 0.141 |
| 13 | vs_grand_mean | mission | leaving | -0.076 | 0.119 |
| 13 | vs_grand_mean | mission | commitment | -0.113 | 0.107 |
| 13 | vs_grand_mean | mission | neutral | -0.249 | 0.091 |
| 13 | vs_grand_mean | leaving | leaving | 0.249 | 0.184 |
| 13 | vs_grand_mean | leaving | commitment | -0.030 | 0.116 |
| 13 | vs_grand_mean | leaving | neutral | -0.150 | 0.090 |
| 13 | vs_grand_mean | commitment | commitment | 0.299 | 0.137 |
| 13 | vs_grand_mean | commitment | neutral | -0.157 | 0.102 |
| 13 | vs_grand_mean | neutral | neutral | 0.487 | 0.150 |

### Pair splits

Script: `scripts/profile_directions.py`. Output: `results/capcom/splits.csv`.

| split | pairs |
|---|---|
| estimation | 1,2,4,5,6,9,12,14,16,20 |
| heldout | 3,7,8,10,11,13,15,17,18,19 |
| est_half_a | 1,2,4,9,14 |
| est_half_b | 5,6,12,16,20 |

### Path-specific cosines (each set against the other two)

Script: `scripts/path_directions.py`. Output: `results/capcom/path_cosines.csv`.

| pair | L8 | L13 |
|---|---|---|
| capability~commitment | 0.021 | 0.065 |
| capability~leaving | -0.082 | -0.050 |
| capability~mission | 0.055 | -0.016 |
| commitment~leaving | -0.352 | -0.294 |
| commitment~mission | -0.550 | -0.633 |
| mission~leaving | -0.588 | -0.554 |

### Path-specific stability

Script: `scripts/path_directions.py`. Output: `results/capcom/path_stability.csv`.

| layer | direction | cos_half_a_vs_half_b | norm |
|---|---|---|---|
| 8 | commitment | 0.871 | 21.592 |
| 8 | mission | 0.927 | 24.982 |
| 8 | leaving | 0.860 | 22.284 |
| 13 | commitment | 0.916 | 43.377 |
| 13 | mission | 0.951 | 49.790 |
| 13 | leaving | 0.903 | 40.321 |

### Path-specific word projections

Script: `scripts/path_directions.py`. Output: `results/capcom/path_word_projections.csv`.

| layer | direction | list | mean_proj | sd_proj | mean_minus_neutral |
|---|---|---|---|---|---|
| 8 | commitment | capability | -21.782 | 0.404 | 0.735 |
| 8 | commitment | commitment | -20.709 | 0.533 | 1.807 |
| 8 | commitment | neutral | -22.517 | 0.640 | 0.000 |
| 8 | mission | capability | 17.283 | 0.559 | -0.526 |
| 8 | mission | commitment | 17.507 | 0.455 | -0.302 |
| 8 | mission | neutral | 17.809 | 0.762 | 0.000 |
| 8 | leaving | capability | 1.730 | 0.484 | -0.122 |
| 8 | leaving | commitment | 0.439 | 0.450 | -1.412 |
| 8 | leaving | neutral | 1.852 | 0.529 | 0.000 |
| 13 | commitment | capability | -28.811 | 0.754 | 0.990 |
| 13 | commitment | commitment | -27.852 | 0.591 | 1.949 |
| 13 | commitment | neutral | -29.801 | 0.890 | 0.000 |
| 13 | mission | capability | 39.992 | 0.938 | -0.964 |
| 13 | mission | commitment | 40.275 | 0.608 | -0.681 |
| 13 | mission | neutral | 40.956 | 1.091 | 0.000 |
| 13 | leaving | capability | -18.390 | 0.772 | 0.125 |
| 13 | leaving | commitment | -19.771 | 0.822 | -1.256 |
| 13 | leaving | neutral | -18.515 | 0.836 | 0.000 |

### Path-specific correlation with valence

Script: `scripts/path_directions.py`. Output: `results/capcom/path_valence_correlation.csv`.

| layer | direction | n_words | r_proj_valence | p |
|---|---|---|---|---|
| 8 | commitment | 52 | 0.033 | 0.817 |
| 8 | mission | 52 | 0.110 | 0.439 |
| 8 | leaving | 52 | -0.161 | 0.255 |
| 13 | commitment | 52 | -0.178 | 0.206 |
| 13 | mission | 52 | 0.445 | 0.001 |
| 13 | leaving | 52 | -0.358 | 0.009 |

## Editing pilot (layer 8)

### Directions

Script: `scripts/edit_pilot.py tests`. Output: `directions/path_gs_L8.npz`.

| measure | value |
|---|---|
| cos(c, L) | -0.0347 |
| cos(c, M) | 0.0878 |
| cos(L, M) | -0.7087 |

### Unit tests on held-out profiles

Script: `scripts/edit_pilot.py tests`. Output: `results/capcom/edit_unit_tests.csv`.

| edit | cos_a | cos_c | proj_c | proj_L | proj_M | proj_l_hat | proj_m_hat | proj_sham | c_mod | c_ext | c_pairs_ext_gt_mod |
|---|---|---|---|---|---|---|---|---|---|---|---|
| unedited | – | 0.954 | 1.037 | -0.056 | 0.103 | 0.024 | 0.090 | -0.009 | -0.628 | 0.409 | 1.000 |
| LEAVE_0.2 | 0.173 | 0.931 | 1.008 | 0.187 | -0.071 | 0.195 | 0.088 | -0.009 | -0.611 | 0.398 | 1.000 |
| LEAVE_0.4 | 0.366 | 0.867 | 0.936 | 0.395 | -0.222 | 0.337 | 0.082 | -0.009 | -0.566 | 0.369 | 1.000 |
| LEAVE_0.6 | 0.560 | 0.751 | 0.808 | 0.602 | -0.376 | 0.475 | 0.071 | -0.009 | -0.489 | 0.319 | 1.000 |
| MISSION_0.2 | 0.180 | 0.917 | 0.994 | 0.155 | -0.195 | 0.024 | -0.121 | -0.009 | -0.602 | 0.392 | 1.000 |
| MISSION_0.4 | 0.372 | 0.842 | 0.910 | 0.300 | -0.402 | 0.021 | -0.269 | -0.009 | -0.551 | 0.359 | 1.000 |
| MISSION_0.6 | 0.565 | 0.715 | 0.772 | 0.444 | -0.610 | 0.016 | -0.418 | -0.009 | -0.467 | 0.305 | 1.000 |
| SHAM_0.2 | 0.183 | 0.936 | 1.016 | -0.055 | 0.101 | 0.024 | 0.088 | 0.198 | -0.615 | 0.401 | 1.000 |
| SHAM_0.4 | 0.374 | 0.877 | 0.950 | -0.053 | 0.095 | 0.021 | 0.082 | 0.406 | -0.576 | 0.375 | 1.000 |
| SHAM_0.6 | 0.567 | 0.767 | 0.830 | -0.049 | 0.085 | 0.016 | 0.071 | 0.613 | -0.502 | 0.327 | 1.000 |

### Decoding probe

Script: `scripts/edit_pilot.py tests`. Output: `results/capcom/edit_probe.csv`.

| edit | n | accuracy | auc |
|---|---|---|---|
| unedited | 20 | 1.000 | 1.000 |
| LEAVE_0.2 | 20 | 1.000 | 1.000 |
| LEAVE_0.4 | 20 | 1.000 | 1.000 |
| LEAVE_0.6 | 20 | 1.000 | 1.000 |
| MISSION_0.2 | 20 | 1.000 | 1.000 |
| MISSION_0.4 | 20 | 1.000 | 1.000 |
| MISSION_0.6 | 20 | 1.000 | 1.000 |
| SHAM_0.2 | 20 | 1.000 | 1.000 |
| SHAM_0.4 | 20 | 1.000 | 1.000 |
| SHAM_0.6 | 20 | 1.000 | 1.000 |

### Hook check

Script: `scripts/edit_pilot.py tests`. Output: `results/capcom/edit_hook_check.csv`.

| edit | max_abs_error | rel_error |
|---|---|---|
| unedited_vs_cache | 0.0464 | 0.0010 |
| LEAVE_0.2 | 0.0134 | 0.1033 |
| LEAVE_0.4 | 0.0115 | 0.0507 |
| LEAVE_0.6 | 0.0054 | 0.0255 |
| MISSION_0.2 | 0.0192 | 0.1121 |
| MISSION_0.4 | 0.0178 | 0.0584 |
| MISSION_0.6 | 0.0044 | 0.0224 |
| SHAM_0.2 | 0.0054 | 0.0787 |
| SHAM_0.4 | 0.0287 | 0.1059 |
| SHAM_0.6 | 0.0165 | 0.0414 |

### Digit mass

Script: `scripts/edit_pilot.py rate`. Output: `results/capcom/edit_mass.csv`.

| edit | mean | min |
|---|---|---|
| LEAVE_0.2 | 0.9886 | 0.9784 |
| LEAVE_0.4 | 0.9884 | 0.9782 |
| LEAVE_0.6 | 0.9883 | 0.9790 |
| MISSION_0.2 | 0.9886 | 0.9788 |
| MISSION_0.4 | 0.9886 | 0.9786 |
| MISSION_0.6 | 0.9886 | 0.9784 |
| SHAM_0.2 | 0.9886 | 0.9779 |
| SHAM_0.4 | 0.9886 | 0.9786 |
| SHAM_0.6 | 0.9886 | 0.9788 |
| unedited | 0.9887 | 0.9792 |

### Penalty

Script: `scripts/edit_pilot.py rate`. Output: `results/capcom/edit_penalty.csv`.

| edit | offer | capabilities | commitment_org | goals_aligned | stay_if_offer |
|---|---|---|---|---|---|
| unedited | +0.07 (0.05) | +0.06 (0.05) | +0.13 (0.10) | +0.07 (0.04) | -0.05 (0.06) |
| LEAVE_0.2 | +0.09 (0.05) | +0.06 (0.06) | +0.14 (0.09) | +0.07 (0.03) | -0.05 (0.05) |
| LEAVE_0.4 | +0.08 (0.04) | +0.06 (0.06) | +0.14 (0.08) | +0.07 (0.03) | -0.04 (0.04) |
| LEAVE_0.6 | +0.08 (0.05) | +0.07 (0.06) | +0.12 (0.10) | +0.07 (0.03) | -0.04 (0.04) |
| MISSION_0.2 | +0.07 (0.05) | +0.06 (0.06) | +0.15 (0.09) | +0.07 (0.04) | -0.04 (0.04) |
| MISSION_0.4 | +0.07 (0.05) | +0.06 (0.06) | +0.14 (0.10) | +0.07 (0.04) | -0.04 (0.04) |
| MISSION_0.6 | +0.07 (0.05) | +0.06 (0.05) | +0.15 (0.07) | +0.07 (0.03) | -0.03 (0.03) |
| SHAM_0.2 | +0.06 (0.04) | +0.06 (0.05) | +0.12 (0.08) | +0.07 (0.03) | -0.03 (0.04) |
| SHAM_0.4 | +0.07 (0.04) | +0.06 (0.06) | +0.13 (0.09) | +0.06 (0.03) | -0.04 (0.04) |
| SHAM_0.6 | +0.07 (0.05) | +0.06 (0.06) | +0.12 (0.07) | +0.06 (0.03) | -0.03 (0.05) |

### Offer penalty minus matching SHAM

Script: `scripts/edit_pilot.py rate`. Output: `results/capcom/edit_penalty.csv`.

| edit | minus SHAM |
|---|---|
| LEAVE_0.2 | 0.022 |
| LEAVE_0.4 | 0.009 |
| LEAVE_0.6 | 0.016 |
| MISSION_0.2 | 0.004 |
| MISSION_0.4 | 0.003 |
| MISSION_0.6 | 0.002 |

### Edited minus unedited, same prompts

Script: `scripts/edit_pilot.py rate`. Output: `results/capcom/edit_ratings.csv`.

| edit | mean | mean abs | max abs |
|---|---|---|---|
| LEAVE_0.2 | 0.0140 | 0.0197 | 0.0981 |
| LEAVE_0.4 | 0.0275 | 0.0333 | 0.1523 |
| LEAVE_0.6 | 0.0396 | 0.0438 | 0.1933 |
| MISSION_0.2 | 0.0042 | 0.0152 | 0.1001 |
| MISSION_0.4 | 0.0060 | 0.0177 | 0.1001 |
| MISSION_0.6 | 0.0094 | 0.0192 | 0.1116 |
| SHAM_0.2 | -0.0042 | 0.0162 | 0.1113 |
| SHAM_0.4 | -0.0061 | 0.0160 | 0.1173 |
| SHAM_0.6 | -0.0069 | 0.0180 | 0.1115 |

### Two unedited runs in different batches, same 200 prompts

Script: `scripts/edit_pilot.py rate, scripts/baseline_ratings.py`. Output: `results/capcom/edit_ratings.csv`, `results/capcom/baseline_ratings.csv`.

| measure | value |
|---|---|
| mean abs | 0.0187 |
| SD | 0.0294 |
| max abs | 0.1403 |
| share above 0.05 | 0.0900 |

## Natural effects

### Projections of each natural difference

Script: `scripts/steering_diagnostics.py effects`. Output: `results/capcom/natural_effects.csv`.

| layer | split | effect | axis | projection | magnitude | full_vector_norm | mean_profile_norm |
|---|---|---|---|---|---|---|---|
| 8 | estimation | capability | c | 1.120 | 1.120 | 1.120 | 75.808 |
| 8 | estimation | leaving | L | 24.023 | 24.023 | 34.050 | 75.808 |
| 8 | estimation | mission | -M | -27.294 | 27.294 | 38.686 | 75.808 |
| 8 | heldout | capability | c | 1.037 | 1.037 | 1.087 | 75.808 |
| 8 | heldout | leaving | L | 24.023 | 24.023 | 34.051 | 75.808 |
| 8 | heldout | mission | -M | -27.264 | 27.264 | 38.645 | 75.808 |
| 8 | all | capability | c | 1.079 | 1.079 | 1.091 | 75.808 |
| 8 | all | leaving | L | 24.023 | 24.023 | 34.050 | 75.808 |
| 8 | all | mission | -M | -27.279 | 27.279 | 38.665 | 75.808 |
| 13 | estimation | capability | c | 2.218 | 2.218 | 2.218 | 147.181 |
| 13 | estimation | leaving | L | 44.815 | 44.815 | 62.037 | 147.181 |
| 13 | estimation | mission | -M | -51.473 | 51.473 | 71.253 | 147.181 |
| 13 | heldout | capability | c | 2.083 | 2.083 | 2.146 | 147.181 |
| 13 | heldout | leaving | L | 44.890 | 44.890 | 62.057 | 147.181 |
| 13 | heldout | mission | -M | -51.380 | 51.380 | 71.195 | 147.181 |
| 13 | all | capability | c | 2.151 | 2.151 | 2.166 | 147.181 |
| 13 | all | leaving | L | 44.853 | 44.853 | 62.044 | 147.181 |
| 13 | all | mission | -M | -51.427 | 51.427 | 71.222 | 147.181 |

## Direct steering

### Mean change from unedited, 40 profiles

Script: `scripts/steering_diagnostics.py steer-rate, steer-summary`. Output: `results/capcom/steering_change.csv`, `results/capcom/steering_ratings.csv`.

| edit | alpha | offer | stay_if_offer | goals_aligned | commitment_org |
|---|---|---|---|---|---|
| steer_L8_LEAVE_k0.5 | 12.012 | -0.171 | -0.061 | -0.161 | -0.536 |
| steer_L8_LEAVE_k1 | 24.023 | -0.353 | -0.182 | -0.465 | -0.986 |
| steer_L8_LEAVE_k2 | 48.046 | -2.282 | -0.677 | -2.621 | -1.677 |
| steer_L8_MISSION_k0.5 | 13.632 | -0.070 | -0.056 | -0.063 | -0.232 |
| steer_L8_MISSION_k1 | 27.264 | -0.182 | -0.159 | -0.153 | -0.483 |
| steer_L8_MISSION_k2 | 54.528 | -1.397 | -0.469 | -1.185 | -1.237 |
| steer_L13_LEAVE_k0.5 | 22.445 | -0.069 | -0.037 | -0.042 | -0.093 |
| steer_L13_LEAVE_k1 | 44.890 | -0.131 | -0.098 | -0.098 | -0.281 |
| steer_L13_LEAVE_k2 | 89.779 | -0.214 | -0.267 | -0.230 | -0.772 |
| steer_L13_MISSION_k0.5 | 25.690 | -0.071 | -0.041 | -0.077 | -0.191 |
| steer_L13_MISSION_k1 | 51.380 | -0.138 | -0.098 | -0.143 | -0.438 |
| steer_L13_MISSION_k2 | 102.759 | -0.242 | -0.183 | -0.250 | -0.916 |

### Noise floor for the mean change

Script: `scripts/steering_diagnostics.py steer-summary`. Output: `results/capcom/steering_noise.csv`.

| edit | question | mean_change | sd | mean_abs | max_abs |
|---|---|---|---|---|---|
| repeat | commitment_org | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| repeat | goals_aligned | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| repeat | offer | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| repeat | stay_if_offer | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| shuffle_0 | commitment_org | -0.0223 | 0.0453 | 0.0368 | 0.1059 |
| shuffle_0 | goals_aligned | 0.0016 | 0.0132 | 0.0076 | 0.0373 |
| shuffle_0 | offer | -0.0006 | 0.0205 | 0.0145 | 0.0525 |
| shuffle_0 | stay_if_offer | -0.0020 | 0.0357 | 0.0252 | 0.0812 |
| shuffle_1 | commitment_org | -0.0213 | 0.0437 | 0.0337 | 0.1055 |
| shuffle_1 | goals_aligned | 0.0054 | 0.0166 | 0.0086 | 0.0808 |
| shuffle_1 | offer | -0.0022 | 0.0209 | 0.0159 | 0.0576 |
| shuffle_1 | stay_if_offer | 0.0062 | 0.0320 | 0.0205 | 0.1029 |
| shuffle_2 | commitment_org | -0.0107 | 0.0426 | 0.0301 | 0.1171 |
| shuffle_2 | goals_aligned | 0.0013 | 0.0141 | 0.0091 | 0.0347 |
| shuffle_2 | offer | -0.0011 | 0.0237 | 0.0182 | 0.0525 |
| shuffle_2 | stay_if_offer | 0.0120 | 0.0340 | 0.0233 | 0.1055 |

### Steering hook check

Script: `scripts/steering_diagnostics.py steer-check`. Output: `results/capcom/steering_check.csv`.

| edit | alpha | moved_along_axis | ratio | off_axis_rel |
|---|---|---|---|---|
| steer_L8_LEAVE_k0.5 | 12.0116 | 12.0022 | 0.9992 | 0.0080 |
| steer_L8_LEAVE_k1 | 24.0231 | 24.0189 | 0.9998 | 0.0024 |
| steer_L8_LEAVE_k2 | 48.0463 | 48.0494 | 1.0001 | 0.0015 |
| steer_L8_MISSION_k0.5 | 13.6319 | 13.6241 | 0.9994 | 0.0095 |
| steer_L8_MISSION_k1 | 27.2639 | 27.2631 | 1.0000 | 0.0036 |
| steer_L8_MISSION_k2 | 54.5278 | 54.5320 | 1.0001 | 0.0011 |
| steer_L13_LEAVE_k0.5 | 22.4448 | 22.4321 | 0.9994 | 0.0102 |
| steer_L13_LEAVE_k1 | 44.8896 | 44.8864 | 0.9999 | 0.0030 |
| steer_L13_LEAVE_k2 | 89.7791 | 89.7894 | 1.0001 | 0.0019 |
| steer_L13_MISSION_k0.5 | 25.6898 | 25.6882 | 0.9999 | 0.0051 |
| steer_L13_MISSION_k1 | 51.3796 | 51.3876 | 1.0002 | 0.0023 |
| steer_L13_MISSION_k2 | 102.7593 | 102.7772 | 1.0002 | 0.0010 |

### Digit mass

Script: `scripts/steering_diagnostics.py steer-summary`. Output: `results/capcom/steering_mass.csv`.

| edit | mean | min |
|---|---|---|
| repeat | 0.9882 | 0.9792 |
| shuffle_0 | 0.9882 | 0.9788 |
| shuffle_1 | 0.9881 | 0.9788 |
| shuffle_2 | 0.9881 | 0.9790 |
| steer_L13_LEAVE_k0.5 | 0.9885 | 0.9787 |
| steer_L13_LEAVE_k1 | 0.9890 | 0.9787 |
| steer_L13_LEAVE_k2 | 0.9908 | 0.9827 |
| steer_L13_MISSION_k0.5 | 0.9885 | 0.9791 |
| steer_L13_MISSION_k1 | 0.9892 | 0.9808 |
| steer_L13_MISSION_k2 | 0.9909 | 0.9825 |
| steer_L8_LEAVE_k0.5 | 0.9893 | 0.9804 |
| steer_L8_LEAVE_k1 | 0.9899 | 0.9800 |
| steer_L8_LEAVE_k2 | 0.9936 | 0.9822 |
| steer_L8_MISSION_k0.5 | 0.9888 | 0.9788 |
| steer_L8_MISSION_k1 | 0.9895 | 0.9792 |
| steer_L8_MISSION_k2 | 0.9905 | 0.9834 |
| unedited | 0.9882 | 0.9792 |

## Matched-magnitude edit (layer 8)

### Unit test through the hook

Script: `scripts/steering_diagnostics.py matched-test`. Output: `results/capcom/matched_unit_test.csv`.

| edit | beta | a_dot_c | all_proj_L | heldout_proj_L | all_proj_minus_M | heldout_proj_minus_M | all_proj_sham | heldout_proj_sham |
|---|---|---|---|---|---|---|---|---|
| unedited | – | – | -0.048 | -0.055 | -0.102 | -0.103 | -0.005 | -0.008 |
| matched_LEAVE_k0.25 | 5.611 | -0.035 | 6.016 | 5.781 | 4.196 | 4.033 | -0.005 | -0.008 |
| matched_LEAVE_k0.5 | 11.178 | -0.035 | 12.033 | 11.571 | 8.460 | 8.136 | -0.005 | -0.008 |
| matched_LEAVE_k1 | 22.312 | -0.035 | 24.067 | 23.152 | 16.988 | 16.344 | -0.005 | -0.008 |
| matched_MISSION_k0.25 | 6.411 | -0.088 | 4.862 | 4.671 | 6.828 | 6.566 | -0.005 | -0.009 |
| matched_MISSION_k0.5 | 12.729 | -0.088 | 9.702 | 9.328 | 13.656 | 13.137 | -0.005 | -0.009 |
| matched_MISSION_k1 | 25.365 | -0.088 | 19.381 | 18.643 | 27.314 | 26.280 | -0.005 | -0.008 |
| matched_SHAM_k0.25 | 5.571 | 0.000 | -0.048 | -0.055 | -0.103 | -0.103 | 6.017 | 5.786 |
| matched_SHAM_k0.5 | 11.138 | 0.000 | -0.049 | -0.056 | -0.102 | -0.104 | 12.034 | 11.577 |
| matched_SHAM_k1 | 22.272 | 0.000 | -0.048 | -0.055 | -0.102 | -0.103 | 24.068 | 23.158 |

| edit | all_proj_l_hat | all_proj_minus_m_hat | all_proj_c | pairs_ext_gt_mod_on_c | token_push_mean | token_push_rms | token_push_max | token_norm_mean |
|---|---|---|---|---|---|---|---|---|
| unedited | 0.034 | -0.096 | 1.081 | 1.000 | – | – | – | 121.207 |
| matched_LEAVE_k0.25 | 4.312 | -0.096 | 0.870 | 1.000 | 32.074 | 41.126 | 152.770 | 128.038 |
| matched_LEAVE_k0.5 | 8.558 | -0.096 | 0.662 | 1.000 | 63.898 | 81.931 | 304.346 | 143.928 |
| matched_LEAVE_k1 | 17.048 | -0.096 | 0.245 | 1.000 | 127.545 | 163.541 | 607.500 | 188.796 |
| matched_MISSION_k0.25 | 0.034 | 4.793 | 0.472 | 1.000 | 36.650 | 46.993 | 174.564 | 129.343 |
| matched_MISSION_k0.5 | 0.034 | 9.610 | -0.128 | 0.000 | 72.766 | 93.302 | 346.586 | 148.590 |
| matched_MISSION_k1 | 0.034 | 19.246 | -1.327 | 0.000 | 144.999 | 185.920 | 690.631 | 201.811 |
| matched_SHAM_k0.25 | 0.034 | -0.097 | 1.081 | 1.000 | 31.847 | 40.835 | 151.690 | 127.452 |
| matched_SHAM_k0.5 | 0.034 | -0.096 | 1.080 | 1.000 | 63.671 | 81.640 | 303.266 | 142.980 |
| matched_SHAM_k1 | 0.034 | -0.096 | 1.082 | 1.000 | 127.319 | 163.250 | 606.419 | 187.484 |

### Penalty

Script: `scripts/steering_diagnostics.py matched-rate, matched-summary`. Output: `results/capcom/matched_penalty.csv`.

| edit | offer | stay_if_offer | goals_aligned | commitment_org |
|---|---|---|---|---|
| unedited | +0.076 (0.054) | -0.043 (0.059) | +0.067 (0.038) | +0.135 (0.092) |
| matched_LEAVE_k0.25 | +0.042 (0.051) | -0.180 (0.072) | +0.005 (0.042) | -0.117 (0.123) |
| matched_LEAVE_k0.5 | -0.966 (0.479) | -0.140 (0.070) | -0.783 (0.331) | -0.474 (0.190) |
| matched_LEAVE_k1 | -0.182 (0.149) | -0.463 (0.148) | -0.194 (0.111) | -0.246 (0.094) |
| matched_MISSION_k0.25 | -0.004 (0.059) | -0.086 (0.068) | +0.004 (0.047) | -0.050 (0.108) |
| matched_MISSION_k0.5 | +0.014 (0.076) | -0.011 (0.042) | -0.021 (0.097) | +0.248 (0.082) |
| matched_MISSION_k1 | +0.250 (0.096) | -0.139 (0.056) | +0.429 (0.185) | +0.263 (0.095) |
| matched_SHAM_k0.25 | +0.025 (0.051) | -0.042 (0.062) | +0.050 (0.030) | -0.037 (0.111) |
| matched_SHAM_k0.5 | -0.112 (0.083) | +0.019 (0.042) | -0.073 (0.054) | -0.238 (0.142) |
| matched_SHAM_k1 | -0.303 (0.114) | +0.108 (0.060) | -0.179 (0.080) | -0.315 (0.157) |

### Penalty minus matching SHAM

Script: `scripts/steering_diagnostics.py matched-summary`. Output: `results/capcom/matched_vs_sham.csv`.

| edit | offer | stay_if_offer | goals_aligned | commitment_org |
|---|---|---|---|---|
| matched_LEAVE_k0.25 | 0.017 | -0.138 | -0.045 | -0.080 |
| matched_LEAVE_k0.5 | -0.855 | -0.159 | -0.710 | -0.237 |
| matched_LEAVE_k1 | 0.120 | -0.571 | -0.015 | 0.069 |
| matched_MISSION_k0.25 | -0.029 | -0.044 | -0.046 | -0.013 |
| matched_MISSION_k0.5 | 0.126 | -0.029 | 0.052 | 0.485 |
| matched_MISSION_k1 | 0.553 | -0.247 | 0.608 | 0.578 |

### Noise floor for the penalty

Script: `scripts/steering_diagnostics.py matched-summary`. Output: `results/capcom/matched_noise.csv`.

| edit | offer | stay_if_offer | goals_aligned | commitment_org |
|---|---|---|---|---|
| repeat | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| shuffle_0 | -0.0101 | 0.0017 | -0.0005 | -0.0188 |
| shuffle_1 | -0.0008 | -0.0027 | 0.0074 | -0.0047 |
| shuffle_2 | -0.0036 | -0.0047 | -0.0036 | 0.0109 |

### Digit mass

Script: `scripts/steering_diagnostics.py matched-summary`. Output: `results/capcom/matched_mass.csv`.

| edit | mean | min |
|---|---|---|
| matched_LEAVE_k0.25 | 0.9880 | 0.9784 |
| matched_LEAVE_k0.5 | 0.9921 | 0.9828 |
| matched_LEAVE_k1 | 0.9973 | 0.9857 |
| matched_MISSION_k0.25 | 0.9884 | 0.9811 |
| matched_MISSION_k0.5 | 0.9829 | 0.9741 |
| matched_MISSION_k1 | 0.9549 | 0.9205 |
| matched_SHAM_k0.25 | 0.9873 | 0.9779 |
| matched_SHAM_k0.5 | 0.9847 | 0.9743 |
| matched_SHAM_k1 | 0.9847 | 0.9722 |

### Change from unedited by level

Script: `scripts/steering_diagnostics.py matched-rate`. Output: `results/capcom/matched_ratings.csv`, `results/capcom/steering_ratings.csv`.

| edit | offer moderate | offer extreme | stay_if_offer moderate | stay_if_offer extreme | goals_aligned moderate | goals_aligned extreme | commitment_org moderate | commitment_org extreme |
|---|---|---|---|---|---|---|---|---|
| matched_LEAVE_k0.25 | 0.347 | 0.313 | -0.290 | -0.427 | 0.059 | -0.003 | 0.219 | -0.033 |
| matched_LEAVE_k0.5 | -0.480 | -1.523 | -0.700 | -0.798 | -1.703 | -2.552 | -1.162 | -1.771 |
| matched_LEAVE_k1 | -3.265 | -3.524 | -1.545 | -1.965 | -3.503 | -3.763 | -2.784 | -3.165 |
| matched_MISSION_k0.25 | 0.033 | -0.047 | 0.057 | 0.015 | 0.081 | 0.018 | 0.284 | 0.099 |
| matched_MISSION_k0.5 | -0.444 | -0.506 | 0.027 | 0.059 | -0.391 | -0.479 | -0.439 | -0.326 |
| matched_MISSION_k1 | -1.308 | -1.134 | 0.085 | -0.012 | -0.939 | -0.577 | -0.941 | -0.813 |
| matched_SHAM_k0.25 | 0.031 | -0.021 | -0.011 | -0.010 | 0.056 | 0.039 | 0.131 | -0.041 |
| matched_SHAM_k0.5 | 0.046 | -0.142 | -0.200 | -0.139 | 0.139 | -0.001 | -0.032 | -0.404 |
| matched_SHAM_k1 | 0.026 | -0.353 | -0.162 | -0.011 | -0.135 | -0.380 | -0.535 | -0.985 |

## Information crossover: matched_LEAVE_k0.5

The offer penalty of this edit was at least 0.3 more negative than matching SHAM, the rule for running the crossover. No other edit met it, and these conditions have no SHAM. The `unedited_baseline` rows come from `baseline_ratings.csv`, which used different batches.

### Penalty by condition

Script: `scripts/steering_diagnostics.py crossover matched_LEAVE_k0.5`. Output: `results/capcom/matched_crossover_penalty_LEAVE_k0.5.csv`, `results/capcom/matched_crossover_ratings_LEAVE_k0.5.csv`.

| edit | condition | question | mean | std | moderate | extreme |
|---|---|---|---|---|---|---|
| matched_LEAVE_k0.5 | mission | commitment_org | -0.492 | 0.280 | 5.775 | 5.284 |
| matched_LEAVE_k0.5 | mission | goals_aligned | -0.265 | 0.107 | 6.564 | 6.299 |
| matched_LEAVE_k0.5 | mission | offer | -0.252 | 0.112 | 6.405 | 6.152 |
| matched_LEAVE_k0.5 | mission | stay_if_offer | -0.950 | 0.335 | 3.838 | 2.889 |
| matched_LEAVE_k0.5 | open_options | commitment_org | -0.206 | 0.073 | 3.955 | 3.750 |
| matched_LEAVE_k0.5 | open_options | goals_aligned | -0.498 | 0.207 | 3.899 | 3.402 |
| matched_LEAVE_k0.5 | open_options | offer | -0.694 | 0.257 | 5.095 | 4.400 |
| matched_LEAVE_k0.5 | open_options | stay_if_offer | -0.333 | 0.132 | 2.589 | 2.256 |
| matched_LEAVE_k0.5 | pay | commitment_org | -0.227 | 0.069 | 4.030 | 3.803 |
| matched_LEAVE_k0.5 | pay | goals_aligned | -0.534 | 0.187 | 3.867 | 3.334 |
| matched_LEAVE_k0.5 | pay | offer | -0.784 | 0.345 | 5.617 | 4.834 |
| matched_LEAVE_k0.5 | pay | stay_if_offer | -0.292 | 0.099 | 2.813 | 2.521 |
| matched_LEAVE_k0.5 | rejected_options | commitment_org | -0.598 | 0.322 | 6.403 | 5.805 |
| matched_LEAVE_k0.5 | rejected_options | goals_aligned | -0.564 | 0.375 | 6.564 | 6.000 |
| matched_LEAVE_k0.5 | rejected_options | offer | -0.127 | 0.092 | 6.945 | 6.818 |
| matched_LEAVE_k0.5 | rejected_options | stay_if_offer | -2.461 | 1.279 | 5.765 | 3.304 |
| unedited_baseline | mission | commitment_org | 0.018 | 0.011 | 5.964 | 5.982 |
| unedited_baseline | mission | goals_aligned | 0.054 | 0.050 | 6.614 | 6.667 |
| unedited_baseline | mission | offer | 0.088 | 0.039 | 6.294 | 6.382 |
| unedited_baseline | mission | stay_if_offer | 0.000 | 0.037 | 4.138 | 4.139 |
| unedited_baseline | open_options | commitment_org | 0.162 | 0.070 | 4.717 | 4.879 |
| unedited_baseline | open_options | goals_aligned | 0.077 | 0.036 | 6.047 | 6.124 |
| unedited_baseline | open_options | offer | 0.013 | 0.029 | 6.000 | 6.013 |
| unedited_baseline | open_options | stay_if_offer | -0.019 | 0.087 | 3.264 | 3.245 |
| unedited_baseline | pay | commitment_org | 0.101 | 0.077 | 5.318 | 5.419 |
| unedited_baseline | pay | goals_aligned | 0.046 | 0.037 | 5.867 | 5.913 |
| unedited_baseline | pay | offer | 0.055 | 0.029 | 6.063 | 6.118 |
| unedited_baseline | pay | stay_if_offer | 0.001 | 0.059 | 4.107 | 4.108 |
| unedited_baseline | rejected_options | commitment_org | 0.029 | 0.041 | 6.660 | 6.689 |
| unedited_baseline | rejected_options | goals_aligned | 0.021 | 0.017 | 6.883 | 6.905 |
| unedited_baseline | rejected_options | offer | 0.005 | 0.005 | 6.962 | 6.966 |
| unedited_baseline | rejected_options | stay_if_offer | 0.040 | 0.039 | 6.284 | 6.324 |

### Digit mass

Script: `scripts/steering_diagnostics.py crossover matched_LEAVE_k0.5`. Output: `results/capcom/matched_crossover_mass_LEAVE_k0.5.csv`.

| condition | mean | min |
|---|---|---|
| mission | 0.9887 | 0.9733 |
| open_options | 0.9921 | 0.9836 |
| pay | 0.9933 | 0.9849 |
| rejected_options | 0.9854 | 0.9447 |

## Validation

The gender direction is the mean of the top-100 masculine words minus the mean of the top-100 feminine words, mean-pooled. All 600 Glasgow gender items are used.

### Gender direction against Glasgow GEND

Script: `scripts/validate_gender.py`. Output: `results/validation/gender_direction_glasgow.csv`.

| model | layer | items | n | pearson_r | spearman_rho |
|---|---|---|---|---|---|
| base | 4 | all | 600 | 0.837 | 0.849 |
| base | 4 | not_in_direction | 400 | 0.740 | 0.744 |
| base | 8 | all | 600 | 0.829 | 0.835 |
| base | 8 | not_in_direction | 400 | 0.745 | 0.753 |
| base | 13 | all | 600 | 0.801 | 0.808 |
| base | 13 | not_in_direction | 400 | 0.697 | 0.706 |
| base | 18 | all | 600 | 0.823 | 0.830 |
| base | 18 | not_in_direction | 400 | 0.725 | 0.736 |
| it | 4 | all | 600 | 0.836 | 0.853 |
| it | 4 | not_in_direction | 400 | 0.757 | 0.767 |
| it | 8 | all | 600 | 0.792 | 0.798 |
| it | 8 | not_in_direction | 400 | 0.714 | 0.722 |
| it | 13 | all | 600 | 0.764 | 0.773 |
| it | 13 | not_in_direction | 400 | 0.703 | 0.713 |
| it | 18 | all | 600 | 0.837 | 0.846 |
| it | 18 | not_in_direction | 400 | 0.746 | 0.757 |

### The evaluator's ratings against Glasgow GEND

Script: `scripts/validate_gender.py, which runs scripts/behavioral_ratings.py`. Output: `results/validation/evaluator_glasgow.csv`, `results/validation/evaluator_ratings.csv`.

| adj | n | pearson_r | spearman_rho | mean_mass | min_mass |
|---|---|---|---|---|---|
| masculine | 600 | 0.590 | 0.654 | 0.999 | 0.987 |
| feminine | 600 | -0.640 | -0.686 | 0.998 | 0.956 |

### Gender direction, base model against instruction-tuned model

Script: `scripts/validate_gender.py, which runs scripts/compare_models.py`. Output: `results/validation/base_vs_it_cosines.csv`.

| layer | cos_base_it |
|---|---|
| 4 | 0.967 |
| 8 | 0.950 |
| 13 | 0.902 |
| 18 | 0.907 |

## Numbers that changed in the rerun

Only the validation numbers changed. The rerun used only the 600 gender items, so the batches, and therefore the padding, differ from the earlier run. Both runs use the same 200 words to build the direction. Every other number comes from a result file whose values did not change; steering and matched labels were renamed, and summaries rebuilt from the renamed files match the earlier values exactly.

| number | measure | old | new | difference |
|---|---|---|---|---|
| base, L4, all | pearson_r | 0.83678 | 0.83676 | -0.00002 |
| base, L4, all | spearman_rho | 0.84863 | 0.84861 | -0.00001 |
| base, L4, not_in_direction | pearson_r | 0.73977 | 0.73974 | -0.00003 |
| base, L4, not_in_direction | spearman_rho | 0.74394 | 0.74390 | -0.00004 |
| base, L8, all | pearson_r | 0.82854 | 0.82853 | -0.00001 |
| base, L8, all | spearman_rho | 0.83500 | 0.83496 | -0.00004 |
| base, L8, not_in_direction | pearson_r | 0.74456 | 0.74459 | 0.00003 |
| base, L8, not_in_direction | spearman_rho | 0.75299 | 0.75309 | 0.00010 |
| base, L13, all | pearson_r | 0.80143 | 0.80138 | -0.00005 |
| base, L13, all | spearman_rho | 0.80806 | 0.80802 | -0.00004 |
| base, L13, not_in_direction | pearson_r | 0.69723 | 0.69716 | -0.00008 |
| base, L13, not_in_direction | spearman_rho | 0.70664 | 0.70648 | -0.00016 |
| base, L18, all | pearson_r | 0.82282 | 0.82281 | -0.00001 |
| base, L18, all | spearman_rho | 0.82960 | 0.82953 | -0.00007 |
| base, L18, not_in_direction | pearson_r | 0.72517 | 0.72517 | -0.00000 |
| base, L18, not_in_direction | spearman_rho | 0.73665 | 0.73642 | -0.00023 |
| it, L4, all | pearson_r | 0.83605 | 0.83605 | 0.00000 |
| it, L4, all | spearman_rho | 0.85292 | 0.85292 | 0.00000 |
| it, L4, not_in_direction | pearson_r | 0.75712 | 0.75712 | 0.00000 |
| it, L4, not_in_direction | spearman_rho | 0.76711 | 0.76711 | 0.00000 |
| it, L8, all | pearson_r | 0.79177 | 0.79177 | -0.00000 |
| it, L8, all | spearman_rho | 0.79837 | 0.79836 | -0.00000 |
| it, L8, not_in_direction | pearson_r | 0.71374 | 0.71374 | -0.00001 |
| it, L8, not_in_direction | spearman_rho | 0.72204 | 0.72203 | -0.00001 |
| it, L13, all | pearson_r | 0.76431 | 0.76430 | -0.00000 |
| it, L13, all | spearman_rho | 0.77264 | 0.77264 | 0.00000 |
| it, L13, not_in_direction | pearson_r | 0.70346 | 0.70346 | -0.00000 |
| it, L13, not_in_direction | spearman_rho | 0.71311 | 0.71311 | 0.00000 |
| it, L18, all | pearson_r | 0.83685 | 0.83685 | -0.00000 |
| it, L18, all | spearman_rho | 0.84560 | 0.84560 | 0.00000 |
| it, L18, not_in_direction | pearson_r | 0.74554 | 0.74554 | 0.00000 |
| it, L18, not_in_direction | spearman_rho | 0.75684 | 0.75684 | 0.00000 |
| evaluator, masculine | pearson_r | 0.58953 | 0.59043 | 0.00089 |
| evaluator, masculine | spearman_rho | 0.65262 | 0.65366 | 0.00104 |
| evaluator, feminine | pearson_r | -0.63928 | -0.63976 | -0.00048 |
| evaluator, feminine | spearman_rho | -0.68526 | -0.68568 | -0.00042 |
| base vs instruction-tuned, L4 | cosine | 0.96724 | 0.96723 | -0.00002 |
| base vs instruction-tuned, L8 | cosine | 0.94960 | 0.94960 | -0.00001 |
| base vs instruction-tuned, L13 | cosine | 0.90194 | 0.90191 | -0.00003 |
| base vs instruction-tuned, L18 | cosine | 0.90675 | 0.90675 | -0.00000 |

Individual evaluator ratings (1200 word-adjective ratings) moved by 0.0069 on average, with a maximum of 0.2131; all are in `results/validation/evaluator_ratings.csv`.
