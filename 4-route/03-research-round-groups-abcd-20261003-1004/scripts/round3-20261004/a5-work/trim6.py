# -*- coding: utf-8 -*-
import sys
p=sys.argv[1]; s=open(p,encoding='utf-8').read(); o=len(s.encode('utf-8'))
pairs=[('自动阶段约 9.2 小时（fold2 实测 00:21 到 09:34）','自动阶段约 9.2 小时（fold2 实测）'),
       ('第一阶段按同样倍数估 555 到 695 秒/轮，VAL 估 8 小时','第一阶段按同倍数估，VAL 估 8 小时')]
for a,b in pairs:
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
open(p,'w',encoding='utf-8',newline='\n').write(s); print(o,len(s.encode('utf-8')))
