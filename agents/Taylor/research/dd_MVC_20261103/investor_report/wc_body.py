import sys,re
L=open('MVC_DD_investor_report_20261103.md').read().split('\n')
def cnt(skip_head_block):
    n=0
    for i,l in enumerate(L):
        if l.startswith(('|','![')) or not l.strip(): continue
        n+=len(l.split())
    return n
print('nontable all',cnt(0))
n=0
for l in L:
    if l.startswith(('|','![','#')) or not l.strip(): continue
    n+=len(l.split())
print('no headings',n)
