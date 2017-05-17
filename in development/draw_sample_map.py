import matplotlib.pyplot as plt
import pandas as pd

#load test dataset
df = pd.read_csv('modules.csv', encoding='latin10')
df.sort_values('Date',inplace=True)
df['Module Type'] = df['Pmax[W]'].apply(lambda x:'2m' if x>90 else '1.5m')
df['Stress Type'] = df['Condition']
df['Module#']=df['Module#'].apply(lambda x:str(x)[-3:])
df['Stress Type']=df['Module#'].apply(lambda x:df[df['Module#']==x].Condition.iloc[-1])


#define the unique identifier for the nodes
node_uid = 'Module#'

#how many repeated measurements for each node?
n_stages = df[node_uid].value_counts().max()

#how many unique nodes?
n_nodes = len(df[node_uid].unique())


vert_step = 1
horz_step = 1

index_on = ['Stress Type','Module Type',node_uid]

map_height = (len(index_on)+n_stages+1)*vert_step
map_width = n_nodes*horz_step

f=plt.figure()
ax=f.add_subplot(111)

cmap = ['']

#draw a textbox on axis ax with top left corner at point x[0],x[1] of height h and width w
#with text label_text, color c and linewidth lw
def draw_textbox(ax,x,h,w,label_text,c,lw):
    x_ar = [x[0],x[0]+w,x[0]+w,x[0]]
    y_ar = [x[1],x[1],x[1]-h,x[1]-h]
    ax.fill(x_ar,y_ar,color=c,linewidth=lw)
    ax.plot(x_ar,y_ar,linewidth=lw,color='black')
    ax.text(x[0]+w/2,x[1]-h/2,label_text,verticalalignment='center',horizontalalignment='center')
    return

def draw_sample_map(ax, experiment_title, d, categories):
    #draw the top level label, which should be the PTR number or whatever
    draw_textbox(ax,[0,map_height],vert_step,map_width,experiment_title,'grey',1)
    #go through the list of categories and plot label text boxes for them
    for i, label in enumerate(categories):

        # define position vector val_r for the group label textbox
        val_ar = [0,map_height-(i+1)*vert_step+.01]

        for j,val in enumerate(d[label].unique()):

            uids_in_val = len(d[d[label]==val][node_uid].unique())
            cat_width = map_width*uids_in_val / n_nodes
            draw_textbox(ax,val_ar,vert_step,cat_width,val,'grey',1)

            if i==(len(categories)-1):
                uids_in_group = len(d[d[label]==val][node_uid].unique())
                for u,uid in enumerate(d[d[label]==val][node_uid].unique()):
                    d_uid = d[ (d[label]==val) & (d[node_uid]==uid)]
                    time_series_x = [val_ar[0]+(u+1/2)*(cat_width/uids_in_group) for z in range(len(d_uid))]
                    time_series_y = [val_ar[1]-vert_step*(z+1) for z in range(len(d_uid))]
                    ax.plot(time_series_x,time_series_y,'ko-')

            val_ar[0]=val_ar[0]+cat_width


def recurmap(ax,x,experiment_title, d, categories):
    if


draw_sample_map(ax,'Sample PT Data',df,index_on)

plt.xlim([0,map_width])
plt.ylim([0,map_height])
plt.show()
