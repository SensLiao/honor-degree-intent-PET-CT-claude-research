# -*- coding: utf-8 -*-
import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
orig = len(s.encode('utf-8'))


def rep(a, b):
    global s
    n = s.count(a)
    if n != 1:
        raise SystemExit('count=%d for: %s' % (n, a[:60]))
    s = s.replace(a, b)


rep('z390 上的作业照旧追加到服务器 tmux 里的主线队列，失败即停；新作业类型（候选重算、回归器拟合、给 2S-ICR 让卡的暂停）要在队列里加支持，算在组 A 判定程序的工作量里。每出一个 VAL，当天按 `collect_baseline_fold_val.py` 的做法收回本机核 sha256，网页 VAL 视图随到随上线（D-2026-10-03-01）。',
    'z390 的作业照旧追加到服务器 tmux 主线队列，失败即停；候选重算、回归器拟合和让卡暂停这几类新作业要在队列里加支持。每出一个 VAL，当天收回本机核 sha256，网页 VAL 视图随到随上线（D-2026-10-03-01）。')
rep('40k 训练中途要让路，就从最近 checkpoint 续训（每个样本的随机数按序号定，停了再接，喂进去的数据不变）。它只留 final.pt、latest.pt 和 30k、35k 两个，约 0.3 GB。',
    '40k 训练要让路时从最近 checkpoint 续训（样本随机数按序号定，数据不变）；只留 final.pt、latest.pt 和 30k、35k 两个，约 0.3 GB。')
rep('| 先用范围阶梯拟合第一版；续修、撤回阶梯在 10-06 的联合回放里补上，整体约晚半天，不动 10-18 |',
    '| 先用范围阶梯拟合第一版，另两族在 10-06 的联合回放里补上，约晚半天，不动 10-18 |')

open(p, 'w', encoding='utf-8', newline='\n').write(s)
print(orig, len(s.encode('utf-8')))
