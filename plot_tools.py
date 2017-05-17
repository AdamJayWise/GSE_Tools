from bokeh import palettes

# return a label->color dictionary given a column label and palette
def dict_from_label(d='df',label_name = 'Comment',palette_name = ''):
    tag_list = []
    for unique_label in d[label_name].unique():
        tag_list.append(unique_label)


    if len(tag_list) > max(palette_name.keys()):
        return 'Error: more unique values than values in palette'

    while len(tag_list) not in palette_name.keys():
        tag_list.append('');

    if (len(tag_list)) in palette_name.keys():
        line_spec = palette_name[(len(tag_list))]
        return {k: v for k, v in zip(tag_list, line_spec)}
    else:
        print('Bad Match Between # of Values and Palette')
        return