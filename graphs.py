#matplotlib style
# def make(activity_count,data,type):
#     import matplotlib.pyplot as plt
#     graph=data.plot(kind='bar',figsize=(7, 7),edgecolor='black', rot=3,zorder=3 ) #plot bar graph
#     graph.grid(zorder=3)  #for grid lines
#     plt.xlabel("Activity type",labelpad=14)
#     plt.ylabel("Count")
#     plt.title("Activity Summary")
#     for p in graph.patches: #adding value count on each bar
#         graph.annotate('{:.1f}'.format(p.get_height()), (p.get_x()+0.25, p.get_height()+0.01))
    
#     #save graph in png , should be called before show()
#     plt.savefig('{}.png'.format(type)) 

#Seaborn style
def make(activity_count,data,type):
    import seaborn as sns
    graph=sns.barplot(x=activity_count["activity"].value_counts().index, y=activity_count["activity"].value_counts())
    graph.bar_label(graph.containers[0])
    
    #save graph in png , should be called before show()
    fig = graph.get_figure()
    fig.savefig('{}.png'.format(type)) 