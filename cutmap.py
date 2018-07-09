# Cut Map Tools
# Started 6/22/18 - Adam Wise
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pyodbc


def plot_roll_image(data = None, title = 'Roll Map'):
    plt.figure( figsize = (16,1))
    im_vis = data.drop_duplicates('SubId').pivot(index = 'FsPosition_m', columns = 'LaneNo', values='Pmax_W')
    plt.imshow(im_vis.T, aspect = 'auto', vmin = 12.5, vmax = 15.5, cmap = 'viridis')
    cb = plt.colorbar(orientation='horizontal', pad = 0.4)
    cb.set_label('Submodule Pmax')
    plt.title(title)
    plt.yticks([0,1],['1','2'])
    plt.show()
    return None
    
def get_gpsp_defects(serial_list):
    """
    Arguments:
        pandas.Series serial_list: series of SubId strings
    returns:
        pandas.DataFrame defects: dataframe of defect info
    """
    
    # SQL query to get defect info

    sql = """

    SELECT
        isd.ICI_Submodule_Defect_ID,
        [Submodule Serial Number] = Submodule_Serial_Number,
        [Status] = stat.DB_Object_Name,
        [Defect Code] = dt.Defect_Type_Code,
        dt.Defect_Type_Code_Binary_Sort_Order, -- Sort field
        [Defect Name] = dt.Defect_Type_Name_En,
        Location = Defect_Location,
        Comments = Defect_Comments,
        [Product Recipe] = prr.Product_Recipe_Name
        ,[Frontsheet Roll] = fsr.Resource_Name
          ,[Inspector 1] = op1.Operator_Name_FL
          ,[Inspector 2] = op2.Operator_Name_FL
          ,[Inspection Date] = CONVERT(VARCHAR, Inspection_Date_Time, 101)
          ,[Part Number] =  pn.Part_Number
          ,[Tray] = tr.Tray_Serial_Number
          ,[Carton] = cr.Carton_Number
          ,[Customer Order] = co.Customer_Order_Number
          ,[Customer] = co.Customer_Name
          ,[PTR] = ptr.PTR_Number
    FROM
        [gse].[ICI_Submodules] isub
    JOIN
        gse.ICI_Submodule_Defects isd ON isd.ICI_Submodule_ID=isub.ICI_Submodule_ID
    JOIN
        Defect_Types dt ON dt.Defect_Type_ID = isd.Defect_Type_ID
    LEFT JOIN
        (SELECT ICI_Submodule_ID,Date_Time = MAX(Date_Time) FROM gse.ICI_Submodule_Cells GROUP BY ICI_Submodule_ID) ipp ON ipp.ICI_Submodule_ID=isub.ICI_Submodule_ID
    LEFT JOIN
        gse.ICI_Submodule_Tests ist ON ist.ICI_Submodule_ID=isub.ICI_Submodule_ID AND ist.SOP_ID=58
    LEFT JOIN
        dbo.Facilities f ON isub.Facility_ID = f.Facility_ID
    LEFT JOIN
        dbo.DB_Objects stat ON stat.DB_Object_ID = isub.ICI_Submodule_Status_DB_Object_ID
    LEFT JOIN
        dbo.Operators op1 ON op1.OperatorID = isub.Inspector_1_ID
    LEFT JOIN
        dbo.Operators op2 ON op2.OperatorID = isub.Inspector_2_ID
    LEFT JOIN
        gse.Part_Numbers pn ON pn.Part_Number_ID=isub.Part_Number_ID
    LEFT JOIN
        PTRs ptr ON ptr.PTR_ID=isub.PTR_ID
    LEFT JOIN
        gse.ICI_Submodule_Trays tr ON tr.ICI_Submodule_Tray_ID=isub.ICI_Submodule_Tray_ID
    LEFT JOIN
        gse.Cartons cr ON cr.Carton_ID=tr.Carton_ID
    LEFT JOIN
        ifs.Customer_Orders co ON co.Customer_Order_ID=cr.Customer_Order_ID
    LEFT JOIN
        gse.ICI_Frontsheet_Cuts ifc ON ifc.ICI_Frontsheet_Cut_ID = isub.ICI_Frontsheet_Cut_ID
    LEFT JOIN
        Resources fsr ON fsr.Resource_ID=ifc.Frontsheet_Resource_ID
    LEFT JOIN
        gse.Product_Recipes prr ON prr.Product_Recipe_ID=ifc.Product_Recipe_ID
    LEFT JOIN
        (SELECT Row = ROW_NUMBER() OVER (PARTITION BY ICI_Pan_ID ORDER BY Date_Time), ICI_Submodule_ID, ICI_Pan_ID, Date_Time FROM (SELECT ICI_Submodule_ID, ICI_Pan_ID, Date_Time = MAX(Date_Time) FROM gse.ICI_Submodule_Pans GROUP BY ICI_Submodule_ID,ICI_Pan_ID) a) isp ON isp.ICI_Submodule_ID=isub.ICI_Submodule_ID
    LEFT JOIN
        gse.ICI_Pans ip ON ip.ICI_Pan_ID=isp.ICI_Pan_ID
    LEFT JOIN
        Resources res ON res.Resource_ID=ip.Pan_Resource_ID
    WHERE
        Submodule_Serial_Number IN ({})

    ORDER BY
        isub.Submodule_Serial_Number DESC,
        dt.Defect_Type_Code_Binary_Sort_Order,
        isd.ICI_Submodule_Defect_ID DESC

    """

    cnxn = pyodbc.connect("DSN=GSPS")
    cursor = cnxn.cursor()
    serial_list = serial_list.apply(lambda x: "'{}'".format(x))
    defects = pd.read_sql_query(sql.format(','.join(serial_list)), cnxn)
    defects['SubId'] = defects['Submodule Serial Number']
    return defects[['SubId','Status','Defect Code']]
    
    
    
    
    
def generate_cut_map(data_ref = None,
                     chunk_lengths = [4 for i in range(12)],
                     title = 'title',
                     min_power = 12.5,
                     sort_on = "FsLot",
                     leader_offset = 0):
    
    def getID(x, data = data_ref):
        if x > leader_offset:
            x = x - leader_offset
        return data[data['FsPosition_m']==x]['SubId'].values

    roll = data_ref[(data_ref.Status!='Fail')&(data_ref.LAM_OK==1)].copy()
    roll['Serial'] = roll['SubId'].apply(lambda x:x[3:])
    
    roll = roll.groupby('FsPosition_m').filter(lambda x:  (x['Pmax_W'].sum()>25) ) 
    
    roll = roll.sort_values('Serial').drop_duplicates('SubId').pivot(index='FsPosition_m',columns='LaneNo',values='Pmax_W')

    roll = roll.reset_index()

    roll.columns = ['Fs',1,2]
    roll['IDs'] = roll['Fs'].apply(getID)
    roll_ref = roll.copy()

    chunks = pd.DataFrame([])

    for chunk_length in chunk_lengths:
        roll = roll.reset_index(drop=True)
        #print(chunk_length)
        # search through and pull chunks from the roll
        result_list = []
        #chunk_length = 12

        for i in range(len(roll)):

            #terminate search if index goes beyond length of roll
            if i+chunk_length>len(roll):
                break

            snip = roll.iloc[i:i+chunk_length]


            if max(snip['Fs'].diff()>0.6).any():
                #print('Failed Chunk at {}'.format(i))
                continue

            Pmax_net = snip[[1,2]].sum().sum()    
            #print(i,np.round( Pmax_net ))
            try:
                result_list.append( (i,
                                 Pmax_net,
                                 np.std(snip[[1,2]].values),
                                 snip['Fs'].min(),
                                 snip.sort_values('Fs').IDs.apply(list).sum(),
                                min([float(i[5:]) for s in snip.IDs.values for i in s])  ))
            except:
                return snip
                

        try:
            results = pd.DataFrame(result_list)
        except:
            #print(results)
            continue
        try:
            results.columns = ['Index Start','Pmax','Pmax STD', 'Fs Start','Serials','Starting Serial']
        except:
            #print(results)
            continue
        results = results.sort_values('Pmax', ascending = False)

        best_chunk = results.iloc[0]
        best_chunk['Length'] = chunk_length


        chunks = chunks.append(best_chunk)
        roll = roll.drop([int(best_chunk['Index Start']+q) for q in range(chunk_length)])


    def round2half(x):
        #return np.round(x*2)/2
        return x
    
    n = 4
    vlist = [(0,-1*n),(0,n),(2,n),(2,-1*n)]
    plt.figure(figsize = (24,1))

    for c in chunks.sort_values('Fs Start').iterrows():
        r1 = round2half(c[1]['Fs Start'])
        r2 = r1+c[1]['Length']*0.5
        x1=0.5
        x2=2.5
        plt.fill([r1,r1,r2,r2,r1],[x1,x2,x2,x1,x1],'k-',alpha=0.2, lw=1)

    plt.scatter(data_ref['FsPosition_m'].apply(round2half),data_ref['LaneNo'],verts=vlist, s = 300, c = data_ref['Pmax_W'],edgecolor = 'none', linewidth = 0.2, vmin = 10, vmax = 15)
    plt.yticks([1,2],[1,2])
    plt.ylim(0.5,2.5)
    plt.xlim(data_ref['FsPosition_m'].min()-1,data_ref['FsPosition_m'].max()+1)
    plt.colorbar(orientation = 'vertical', pad = 0)

    for c in chunks.sort_values('Fs Start').iterrows():
        r1 = round2half(c[1]['Fs Start'])
        r2 = r1+c[1]['Length']*0.5
        x1=0.6
        x2=2.4
        plt.plot([r1,r1,r2,r2,r1],[x1,x2,x2,x1,x1],'k-', lw=1)

    fail_qc = (data_ref['Status']=='Fail')
    fail_lam = (data_ref['LAM_OK']==0)
    fail_power = (data_ref['Pmax_W'] < min_power)
    
    vlist_qc = [(0,-1*n),(0,0),(2,0),(2,-1*n)]
    vlist_power = [(0,0),(0,n),(2,n),(2,0)]
    
    for c in data_ref[(fail_qc)|(fail_lam)|(fail_power)].iterrows():
        plt.scatter(round2half(c[1]['FsPosition_m']),c[1]['LaneNo'],verts=vlist, s = 300, lw=0, color = 'white', alpha = 1)
    for c in data_ref[fail_qc].iterrows():  
        plt.scatter(round2half(c[1]['FsPosition_m']),c[1]['LaneNo'],verts=vlist_qc, s = 150, lw=0, color = 'red', alpha = 0.5)
    
    for c in data_ref[data_ref['Pmax_W']<min_power].iterrows():
        plt.scatter(round2half(c[1]['FsPosition_m']),c[1]['LaneNo'],verts=vlist_power, s = 150, lw=0, color = 'black', alpha = 0.5)
    
    for c in data_ref[data_ref['LAM_OK']==0].iterrows():
        plt.scatter(round2half(c[1]['FsPosition_m']),c[1]['LaneNo'],verts=vlist, s = 10, lw=0, color = 'white', alpha = 0)
        


    #plt.plot(120.4,2,'rs')

    plt.xlabel('Frontsheet Position, m')
    plt.ylabel('Lane')
    plt.title(title)
    plt.show()

    return chunks.reset_index(drop = True)

    