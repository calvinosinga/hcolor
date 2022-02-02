from hc_lib.plots.fig_lib import FigureLibrary

def redshiftR_fieldnameC_2D(rlib, iprops, rmprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Visualize redshift space distortions
    """
    row_prop = 'redshift'
    column_prop = 'fieldname'
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, '2D'))
    figArr, rowlabels, collabels = rlib.organizeCrossFigure(iprops, row_prop, column_prop, '2Dpk', 0, rmprops)
    rlib.tohdf5(figArr, savePath + 'redshiftR_fieldnameC_2D.hdf5', ['redshift','fieldname', 'snapshot'])
    # flib = FigureLibrary(figArr)
    
    # flib.createFig(panel_length, panel_bt, border, border, True)
    # flib.assign2DNorms()
    # flib.assignColormaps()
    # flib.addContours()
    # flib.plot2D()

    # flib.changeTickDirection()
    # flib.addColLabels(collabels)
    # flib.addRowLabels(rowlabels, pos = [0.05, 0.90], color='white')
    
    # flib.removeDefaultTickLabels()
    # flib.defaultAxesLabels(2)
    return
    # if not savePath == '':
    #     flib.saveFig(savePath, row_prop, column_prop, '2D')
         
    #     return None
    # else:
    #     return flib

def redshiftR_spaceC_fieldname(rlib, iprops, rmprops, savePath = '', panel_length = 3, panel_bt = 0.25, border = 1):
    row_prop = 'redshift'
    column_prop = 'space'
    panel_prop = 'fieldname'
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeCrossFigure(iprops, row_prop, column_prop, 'pk', 0, rmprops)
    rlib.tohdf5(figArr, savePath + 'redshiftR_spaceC_fieldname.hdf5', ['redshift','space','fieldname', 'snapshot', 'model'])
    return
