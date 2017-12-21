import matplotlib.pyplot as plt
from matplotlib import cm

def show_time_series_by_group(data = df_iv, group_ind = 'Condition', uid_col = 'ID', cmap_name = 'jet', x = 'Datetime', y = 'Pmax', ax = plt.gca()):
    cmap = cm.get_cmap(cmap_name)
    unique_groups = data[group_ind].unique()
    num_groups = len(unique_groups)
    cdict = {k:v for (k,v) in zip(unique_groups,np.linspace(0,1,num_groups))}
    
    labels = []
    for lbl, grp in data.groupby([group_ind,uid_col]):
        
        if lbl[0] not in labels:
            l = lbl[0]
            labels.append(lbl[0])
        elif lbl[0] in labels:
            l = '_'
            
        x_data = (grp[x]-min(grp[x])).apply(lambda x: x.total_seconds()/3600)
        ax.plot( x_data, grp[y], color = cmap(cdict[grp[group_ind].iloc[0]]), label = l )
    
    ax.set_xlabel('Hours')
    ax.set_ylabel(y)