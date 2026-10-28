#!/usr/bin/env python3
import json,os
import matplotlib.pyplot as plt
import numpy as np
HERE=os.path.dirname(os.path.abspath(__file__));OUT=os.path.join(HERE,'out4');r=json.load(open(os.path.join(OUT,'results.json')))
def forest(keys,d,title,name):
 m=np.array([d[k]['mean']*100 for k in keys]);lo=np.array([d[k]['lo']*100 for k in keys]);hi=np.array([d[k]['hi']*100 for k in keys]);y=np.arange(len(keys))
 fig,ax=plt.subplots(figsize=(7,3.8));ax.errorbar(m,y,xerr=[m-lo,hi-m],fmt='o',capsize=4,color='#315b7d');ax.axvline(0,color='black',lw=.8);ax.set_yticks(y,keys);ax.set_xlabel('Mean abnormal return (%)');ax.set_title(title);ax.grid(axis='x',alpha=.2);fig.tight_layout();fig.savefig(os.path.join(OUT,name),dpi=160);plt.close(fig)
forest(['R_5','R_20','R_60'],r['rights_horizons'],'Rights after ex-date','fig1_rights_horizons.png')
forest(['A_5','A_20','A_60'],r['ais_horizons'],'ESOP/private placement around AIS','fig2_ais_horizons.png')
forest(['IS','OOS','ESOP','PRIVATE_PLACEMENT'],{**r['rights_splits'],**r['ais_splits']},'Primary stability and subtypes','fig3_stability.png')
