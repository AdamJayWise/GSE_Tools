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

    WHERE sub.[SubId] LIKE {}

    """
    # serial = '1A21702060366'
    return pd.read_sql_query(sql.format("'" + serial + "'"), cnxn)


# Define function to poll the GSPS database tables relevant pilot line production
# use the pyodbc library to run a query against submodule serial number
# returns a dataframe with results for this submodules
# I'm not sure if it would be better to run a query for a range of sumbodules IDs?

def poll_gsps(serial):
    cnxn = pyodbc.connect("DSN=GSPS")
    cursor = cnxn.cursor()

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
     [Equipment] = isc.Cell_Position,
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

    WHERE isub.Submodule_Serial_Number like {}

    """
    #serial = '052913-2'
    return pd.read_sql_query(sql.format("'" + serial + "'"), cnxn)


def poll_gsps_batch(serials):
    df_list = []
    for s in serials:
        df_list.append(poll_gsps(s))
    return pd.DataFrame(df_list)