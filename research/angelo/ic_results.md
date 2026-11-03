# IC study (pre-registered, item a)

Panel: data/train_1h.parquet, 14871 hours x 20 symbols.
Primary cell: S_res, skip1. Holm over the 6 S_res horizons; S_raw is comparison only.

```
signal horizon mean_ic       t        p  n_hours t_method incr_coef  incr_t   incr_p nonoverlap_ic nonoverlap_t nonoverlap_n   p_holm  primary
 S_res       1  0.0141  6.2060 5.44e-10    14869    plain    0.0143  6.1847 6.22e-10                                         3.26e-09    False
 S_res       2  0.0131  5.8494 4.93e-09    14868    NW(1)    0.0131  5.7809 7.43e-09        0.0105       3.2887    7434.0000 2.47e-08    False
 S_res       4  0.0072  3.2242   0.0013    14866    NW(3)    0.0068  3.0507   0.0023        0.0099       2.1723    3716.0000   0.0051    False
 S_res       8  0.0028  1.2339   0.2172    14862    NW(7)    0.0027  1.1780   0.2388        0.0097       1.5251    1857.0000   0.2769    False
 S_res      24 -0.0032 -1.4816   0.1385    14846   NW(23)   -0.0038 -1.7067   0.0879        0.0021       0.1838     618.0000   0.2769    False
 S_res   skip1  0.0038  1.6942   0.0902    14868    plain    0.0034  1.5082   0.1315                                           0.2707     True
 S_raw       1  0.0310 12.6954 6.27e-37    14870    plain                                                                                False
 S_raw       2  0.0275 11.5749 5.52e-31    14869    NW(1)                                   0.0211       6.1568    7435.0000             False
 S_raw       4  0.0228  9.6236 6.35e-22    14867    NW(3)                                   0.0261       5.2941    3717.0000             False
 S_raw       8  0.0129  5.4640 4.66e-08    14863    NW(7)                                   0.0249       3.6197    1858.0000             False
 S_raw      24  0.0056  2.3956   0.0166    14847   NW(23)                                   0.0202       1.6128     619.0000             False
 S_raw   skip1  0.0117  4.8721 1.10e-06    14869    plain                                                                                False
```
