# Import libraries
import pandas as pd
import numpy as np
import pyodbc

# Define function to poll the GSPS database tables relevant to production on the Mondragon automated lines
# use the pyodbc library to run a query against submodule serial number
# returns a dataframe with results for this submodules
# I'm not sure if it would be better to run a query for a range of sumbodules IDs?

def poll_gsps_mondragon(serial):
    # open ODBC connection
    cnxn = pyodbc.connect("DSN=GSPS")
    # cursor = cnxn.cursor()
    
    if type(serial) == str:
        serial = [serial]
        
    # SQL query string w/ formatting to insert serial #
    sql = """
    SELECT
          [Sub Timestamp] = sub.[Timestamp],
          sub.[SubId],
          sub.[RecipeName],
          sub.[LaneNo],
          sub.[FsLot],
          cell.[Reel],
          cell.[ReelPosition_m],sub.[Pmax_W],
          sub.[Isc_A],
          sub.[Voc_V],
          sub.[Imax_A],
          sub.[Vmax_V],
          sub.[Eff_%],
          sub.[FillF_%],
          sub.[TestTemp_C],
          cell.[CellID],
          cell.[RecipeName],
          cell.[CellWidth_mm],
          cell.[CellLength_mm],
          [Cell Voc Calc_mV] = cell.[VocCalc_mV],
          [Cell Voc Min_mV] = cell.[VocMin_mV],
          [Cell Voc Max_mV] = cell.[VocMax_mV]

    FROM [10.10.138.6\MONDRAGONLINE01].[MondragonLine01].[dbo].[CellSub] cellsub
    JOIN [10.10.138.6\MONDRAGONLINE01].[MondragonLine01].[dbo].[cell] cell ON cell.CellID = cellsub.CellID AND LEN(cell.CellID) > 1
    JOIN [10.10.138.6\MONDRAGONLINE01].[MondragonLine01].[dbo].[Sub] sub ON sub.SubID = cellsub.SubID

    WHERE sub.[SubId] in {}

    """
    # serial = '1A21702060366'
    return pd.read_sql_query(sql.format(','.join(["'"+s+"'" for s in serial])), cnxn)


# Define function to poll the GSPS database tables relevant pilot line production
# use the pyodbc library to run a query against submodule serial number
# returns a dataframe with results for this submodules
# I'm not sure if it would be better to run a query for a range of sumbodules IDs?

def poll_gsps(serial):
    cnxn = pyodbc.connect("DSN=GSPS")
    cursor = cnxn.cursor()
    
    if type(serial) == str:
        serial = [serial]

    sql = """
    SELECT
     ist.ICI_Submodule_Test_ID,
     [ID] = ist.ICI_Submodule_Test_ID,
     [Serial #] = isub.Submodule_Serial_Number,
     [Status] = do.DB_Object_Name,
     [Product Recipe] = prr.Product_Recipe_Code + N' - ' + prr.Product_Recipe_Name,
     [Part Number] =  pn.Part_Number,
     [SOP] = s.SOP_Number,
     [Comment] = ist.Comment,
     [Equipment] = res.Resource_Code,
     [Position Y] = isc.Position_X,
     [Position X] = isc.Position_Y,
     [IPP Date & Time] = isc.Date_Time,
     [Bin] = isc.Bin_Serial_Number,
     [Plate] = isc.Plate_Serial_Number,
     [Replace Count] = isc.Replaced_Count,
     [Reel] = lbr.LBR_Code,
     [Web Position, m] = ic.Web_Position_m,
     [Singulation Date & Time] = ic.Date_Time,
     [Singulation Bin] = ic.Bin_Serial_Number,
     [Cell Length, mm] = ic.Cell_Length_mm,
     [Cell OK] = ic.Cell_OK,
     [Frontsheet Lot] = fsr.Resource_Name,  --ifc.frontsheet_lot,
     [ICI PTR] = ptr.PTR_Number,
     [Project Code] = proj.Short_Name,
     [Project Description] = proj.Description

    FROM
     gse.ICI_Submodule_Tests ist
    JOIN
     gse.ICI_Submodules isub ON isub.ICI_Submodule_ID=ist.ICI_Submodule_ID
    JOIN
     SOPs s ON s.SOP_ID=ist.SOP_ID
    LEFT JOIN
     DB_Objects do ON do.DB_Object_ID=isub.ICI_Submodule_Status_DB_Object_ID
    LEFT JOIN
     gse.ICI_Frontsheet_Cuts ifc on ifc.ICI_Frontsheet_Cut_ID = isub.ICI_Frontsheet_Cut_ID
    LEFT JOIN
     gse.Product_Recipes prr ON prr.Product_Recipe_ID=ifc.Product_Recipe_ID
    LEFT JOIN
     gse.Part_Numbers pn ON pn.Part_Number_ID=isub.Part_Number_ID
    LEFT JOIN
     gse.ICI_Submodule_Cells isc ON isc.ICI_Submodule_ID=isub.ICI_Submodule_ID
    LEFT JOIN
     Resources res ON res.Resource_ID=isc.Equipment_Resource_ID
    LEFT JOIN
     Resources fsr ON fsr.Resource_ID=ifc.Frontsheet_Resource_ID
    LEFT JOIN
     gse.ICI_Cells ic ON ic.ICI_Cell_ID=isc.ICI_Cell_ID
    LEFT JOIN
     gse.vw_LBRs lbr ON lbr.LBR_ID=ic.Reel_LBR_ID

    LEFT JOIN
     ifs.project_activities proj ON isub.Project_Activity_ID = proj.Project_Activity_ID
    LEFT JOIN
     dbo.PTRs ptr on isub.PTR_ID = ptr.PTR_ID

    WHERE isub.Submodule_Serial_Number in ({})

    """
    #serial = '052913-2'
    return pd.read_sql_query(sql.format(','.join(["'"+s+"'" for s in serial])), cnxn)


def poll_gsps_batch(serials):
    df_list = []
    for s in serials:
        df_list.append(poll_gsps(s))
    return pd.DataFrame(df_list)
    
def get_lbiv_by_lot(lot):
    sql = """
    SELECT 
    LotBatchReel,
    Web_Position,
    Time_Date,
    [Light_Voltage_01] = Voltage_Channel01_Light,
    [Light_Voltage_02] = Voltage_Channel19_Light,
    [Light_Voltage_03] = Voltage_Channel02_Light,
    [Light_Voltage_04] = Voltage_Channel20_Light,
    [Light_Voltage_05] = Voltage_Channel03_Light,
    [Light_Voltage_06] = Voltage_Channel21_Light,
    [Light_Voltage_07] = Voltage_Channel04_Light,
    [Light_Voltage_08] = Voltage_Channel22_Light,
    [Light_Voltage_09] = Voltage_Channel05_Light,
    [Light_Voltage_10] = Voltage_Channel23_Light,
    [Light_Voltage_11] = Voltage_Channel06_Light,
    [Light_Voltage_12] = Voltage_Channel24_Light,
    [Light_Voltage_13] = Voltage_Channel07_Light,
    [Light_Voltage_14] = Voltage_Channel25_Light,
    [Light_Voltage_15] = Voltage_Channel08_Light,
    [Light_Voltage_16] = Voltage_Channel26_Light,
    [Light_Voltage_17] = Voltage_Channel09_Light,
    [Light_Voltage_18] = Voltage_Channel27_Light,
    [Dark_Voltage_01] = Voltage_Channel10_Dark,
    [Dark_Voltage_02] = Voltage_Channel28_Dark,
    [Dark_Voltage_03] = Voltage_Channel11_Dark,
    [Dark_Voltage_04] = Voltage_Channel29_Dark,
    [Dark_Voltage_05] = Voltage_Channel12_Dark,
    [Dark_Voltage_06] = Voltage_Channel30_Dark,
    [Dark_Voltage_07] = Voltage_Channel13_Dark,
    [Dark_Voltage_08] = Voltage_Channel31_Dark,
    [Dark_Voltage_09] = Voltage_Channel14_Dark,
    [Dark_Voltage_10] = Voltage_Channel32_Dark,
    [Dark_Voltage_11] = Voltage_Channel15_Dark,
    [Dark_Voltage_12] = Voltage_Channel33_Dark,
    [Dark_Voltage_13] = Voltage_Channel16_Dark,
    [Dark_Voltage_14] = Voltage_Channel34_Dark,
    [Dark_Voltage_15] = Voltage_Channel17_Dark,
    [Dark_Voltage_16] = Voltage_Channel35_Dark,
    [Dark_Voltage_17] = Voltage_Channel18_Dark,
    [Dark_Voltage_18] = Voltage_Channel36_Dark
    FROM 
        [GlobalSolar_Flare_Production].[dbo].[FileDataLBIVRun]
    WHERE
        FileLot='{}'
    ORDER BY 1,2
    """
    cnxn = pyodbc.connect("DSN=GSPS")
    df = pd.read_sql_query(sql.format(lot), cnxn)
    df_light = pd.melt(df,id_vars = ['LotBatchReel','Web_Position','Time_Date'], value_vars = [c for c in df.columns if 'Light' in c], var_name = 'Crossweb Channel', value_name = 'Light Voltage')
    df_dark = pd.melt(df,id_vars = ['LotBatchReel','Web_Position','Time_Date'], value_vars = [c for c in df.columns if 'Dark' in c], var_name = 'Crossweb Channel', value_name = 'Dark Voltage')
    df_light['Crossweb Channel'] = df_light['Crossweb Channel'].apply(lambda x:x[-2:]).astype(float)
    df_dark['Crossweb Channel'] = df_dark['Crossweb Channel'].apply(lambda x:x[-2:]).astype(float)
    #df['Crossweb Channel'] = df['Crossweb Channel'].apply(lambda x:x[-2:]).astype(float)
    
    return pd.merge(df_light,df_dark[[c for c in df_dark.columns if 'Time' not in c]],on = ['LotBatchReel','Web_Position','Crossweb Channel'])