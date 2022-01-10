#! /Users/tsuno/.pyenv/shims/python3
# -*- coding: utf-8 -*-
#
# generated by wxGlade 0.9.6 on Thu Oct 29 22:41:10 2020
#

import numpy, matplotlib
if matplotlib.__version__ < '2.2':
    raise ValueError("Minimum Matplotlib version required: 2.2")
#
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

import wx
import os
from shutil import make_archive

# read from glade
import gui
# read from main solver
import fiber
import prop
import pandas as pd

import store
import sqlite3
import numpy as np

import report
import shutil

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade

class MyFrame(gui.MyFrame):


    # Make report
    def OnReport(self,event):

        with wx.FileDialog(self, "Save Pdf File", wildcard="Input File (*.pdf)|*.pdf",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind
            # save the current contents in the file
            pathname = fileDialog.GetPath() # pdf file

            try:
                """
                conn = sqlite3.connect(self.dbname)
                table = 'CNTL'
                df = pd.read_sql_query('SELECT * FROM %s' % table, conn)
                """
                #cntl = os.path.dirname(self.text_ctrl_2.GetValue())
                cntl = self.text_ctrl_2.GetValue()
                df = pd.read_csv(cntl)
                num = len(df)
                print("report No.=",num)
                title = "sample"

                self.list_ctrl_input.SetItemState(0,0,wx.LIST_STATE_SELECTED)
                self.list_ctrl_input.Select(0)
                for i in range(0,len(df)):
                    self.SaveFig2(i)
                    if i == len(df)-1:break;
                    self.list_ctrl_input.SetItemState(i,0,wx.LIST_STATE_SELECTED)
                    self.list_ctrl_input.Select(i+1)

                obj = report.Report(cntl)
                obj.create_pdf(num,pathname,title)
                del obj
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)

    # Export sqlite data
    ########################################################################
    def OnExport(self,event):
        with wx.FileDialog(self, "Save Sqlite File", wildcard="Output File (*.db)|*.db",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind
            # save the current contents in the file
            pathname = fileDialog.GetPath()
            try:
                input_path = './db/test.db'
                shutil.copyfile(input_path,pathname)
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)

    ########################################################################
    # No use
    def OnChooseTargetFile(self, event):  # wxGlade: MyFrame.<event_handler>
        pathname = self.showFileDialog()
        self.text_ctrl_1.SetValue(pathname)

    ########################################################################
    # Control file
    def OnChooseOutputFile(self, event):  # wxGlade: MyFrame.<event_handler>
        if os.path.exists('./db/test.db'):
            os.remove('./db/test.db')
            print('remove ./db/test.db ^v^!')
        else:
            print('none .db')

        pathname = self.showFileDialog()
        self.text_ctrl_2.SetValue(pathname)

        # test
        readFile = pathname
        self.read_cntl(readFile)
        self.list_ctrl_input.Select(0)
        #

    def showFileDialog(self):
        with wx.FileDialog(self, 'Pls, select File',
                          style=wx.DD_DEFAULT_STYLE
                                | wx.DD_DIR_MUST_EXIST
                                | wx.DD_CHANGE_DIR
                          ) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return
            return dialog.GetPath()

    def OnCancel(self, event):  # wxGlade: MyFrame.<event_handler>
        self.Destroy()

    ########################################################################
    # Cal, Run
    ########################################################################
    def OnExec(self, event):  # wxGlade: MyFrame.<event_handler>

        self.OnCap(event)
        #target_file = self.text_ctrl_1.GetValue()
        output_file = self.text_ctrl_2.GetValue()
        #
        #filepath = os.path.join(output_file, os.path.basename(target_file))
        #print(target_file)

        # Main Program
        # 入出力ファイルを初期設定以外にする場合は引数 inp_path out_path を指定
        id_cal,csvfile,\
            theta,ecumax,ndiv,nn,ecu,esu,\
            mate1,mate2,\
            xx1,yy1,xx2,yy2,ndimx,ndimy,fc,\
            ids,nx,ny,dtx,dty,dia,fy,\
            ibc,fbc,ibt,fbt,outfile\
            =\
            self.read_data()

        print("------------------------------")

        obj = fiber.Fiber(xx1,xx2,yy1,yy2,mate1,mate2)
        if obj.getModel(xx1,xx2,yy1,yy2,ndimx,ndimy,fc,\
                        ids,nx,ny,dtx,dty,dia,fy):
            obj.getG(xx1,xx2,yy1,yy2)
            #obj.viewModel(0.5)
            print("Complete Model Making")
        else:
            del obj
            obj = Fiber()
            dlg = wx.MessageDialog(self, 'Erro input',
                                   'Error input',
                                   wx.OK | wx.ICON_ERROR
                                   )
            dlg.ShowModal()
            dlg.Destroy()
            print("Fail Model Making")

        ax = []
        screen = []
        ax.append( self.matplotlib_axes2 )
        ax.append( self.matplotlib_axes3 )
        ax.append( self.matplotlib_axes4 )
        screen.append( self.matplotlib_canvas2 )

        for i in range(0,len(ax)):
            ax[i].clear()
        for i in range(0,len(screen)):
            screen[i].draw()

        #
        # making M-p relationship
        #
        obj.solve(nn,theta,ecumax,ndiv,ecu,esu,ax,screen,id_cal,self.dbname,outfile)
        self.list_ctrl_input.SetItem(id_cal, 0, "Y")

        #table = str(id_cal)+"mp"
        #fiber.AftFib(self.dbname).plotGui(id_cal,ax,screen)
        fiber.AftFib(output_file).plotGui(id_cal,ax,screen)
        #obj.solveBySt(nn,theta,0, ecu,"# Ultimate by concrete") # Conの圧縮歪み
        #obj.solveBySt(nn,theta,3,-esu,"# Ultimate by Steel Bar") # 鉄筋の引張歪み

        print("------------------------------")
        print("Complete")

    ########################################################################
    # test save fig
    def SaveFig(self,id_cal):
        self.matplotlib_figure2.savefig('./db/'+str(id_cal)+'mp.png')
        self.matplotlib_figure.savefig('./db/'+str(id_cal)+'model.png')

    ########################################################################
    # test save fig
    def SaveFig2(self,id_cal):
        cntl = self.text_ctrl_2.GetValue()
        pathname = os.path.dirname(cntl)
        df =  pd.read_csv(cntl)
        imagefile=pathname + "/" + df.iloc[id_cal,13].replace(' ','')
        print(imagefile)
        self.matplotlib_figure2.savefig(imagefile+'mp.png')
        self.matplotlib_figure.savefig(imagefile+'model.png')

    ########################################################################
    # calculate capacity
    def OnCap(self,event):

        #target_file = self.text_ctrl_1.GetValue()

        id_cal,csvfile,\
            theta,ecumax,ndiv,nn,ecu,esu,\
            mate1,mate2,\
            xx1,yy1,xx2,yy2,ndimx,ndimy,fc,\
            ids,nx,ny,dtx,dty,dia,fy,\
            ibc,fbc,ibt,fbt,outfile\
            =\
            self.read_data()

        obj = fiber.Fiber(xx1,xx2,yy1,yy2,mate1,mate2)
        if obj.getModel(xx1,xx2,yy1,yy2,ndimx,ndimy,fc,\
                        ids,nx,ny,dtx,dty,dia,fy):
            obj.getG(xx1,xx2,yy1,yy2)
            #obj.viewModel(0.5)
            print("Complete Model Making")
        else:
            del obj
            obj = Fiber()
            dlg = wx.MessageDialog(self, 'Erro input',
                                   'Error input',
                                   wx.OK | wx.ICON_ERROR
                                   )
            dlg.ShowModal()
            dlg.Destroy()
            print("Fail Model Making")


        # set of the allowable strength
        # concrete
        for i in range(0,len(mate1)):
            if mate1[i] == ibc:
                eca = prop.Conc(mate2[i]).ecs(fbc)
                ect = prop.Conc(mate2[i]).ect()
                print(mate2[i],fbc)
            if mate1[i] == ibt:
                esa = prop.St(-99,mate2[i]).st_s(fbt)
        #print(eca,esa,ect)

        # allowable moment
        ####################
        # Conの圧縮歪み
        comment, pa , ma_x, ma_y, eemax_a, eemin_a, eesmax_a, eesmin_a, ecmin_a =\
            obj.solveBySt(nn,theta,0, eca,"# Allowable by Concrete")
        # 鉄筋の引張歪み
        if abs(eesmin_a) > esa:
            comment, pa , ma_x, ma_y, eemax_a, eemin_a, eesmax_a, eesmin_a, ecmin_a =\
                obj.solveBySt(nn,theta,3, -esa,"# Allowable by Steel Bar")

        # Ultimate moment
        ####################
        # Conの圧縮歪み
        #comment, ec, es, pu, mux, muy, ecmin =\
            #obj.solveBySt(nn,theta,0, ecu,"# Ultimate by Concrete")
        comment, pu , mux, muy, eemax_u, eemin_u, eesmax_u, eesmin_u, ecmin_u =\
            obj.solveBySt(nn,theta,0, ecu,"# Ultimate by Concrete")
        # 鉄筋の引張歪み
        if abs(eesmin_u) > esu:
            #comment, ec, es, pu, mux, muy, ecmin =\
            #    obj.solveBySt(nn,theta,3,-esu,"# Ultimate by Steel Bar")
            comment, pu , mux, muy, eemax_u, eemin_u, eesmax_u, eesmin_u, ecmin_u =\
                obj.solveBySt(nn,theta,3,-esu,"# Ultimate by Steel Bar")

        # set of the crack strength
        # crack moment
        ####################
        mc_x = 0.0
        mc_y = 0.0
        #print(ecmin,ect)
        if ecmin_u < ect:
            print("ecmin_u",ecmin_u,"ect",ect)
            comment, pc , mc_x, mc_y, eemax_c, eemin_c, eesmax_c, eesmin_c, ecmin_c =\
                obj.solveBySt(nn,theta,1, ect,"# Concrete Crack")

        df = pd.DataFrame(np.arange(27).reshape(3,9),
                          columns=['p','mx','my','emax','emin','esmax','esmin','ec','xn'])
        df.loc[:,'p']     = [ pc,pa,pu]
        df.loc[:,'mx']    = [ mc_x,ma_x,mux]
        df.loc[:,'my']    = [ mc_y,ma_y,muy]
        df.loc[:,'emax']  = [ eemax_c,eemax_a,eemax_u]
        df.loc[:,'emin']  = [ eemin_c,eemin_a,eemin_u]
        df.loc[:,'esmax'] = [ eesmax_c,eesmax_a,eesmax_u]
        df.loc[:,'esmin'] = [ eesmin_c,eesmin_a,eesmin_u]
        df.loc[:,'ec']    = [ ecmin_c,ecmin_a,ecmin_u]
        df.loc[:,'xn']    = [ '#',ecmin_a/pa,ecmin_u/pu]

        # to csv
        df.to_csv(outfile+"cap",header=True,index=None)
        store.Store(self.dbname).conv_pd_data(df,str(id_cal)+"cap")

        #print(df)
        #print(pc,mc_x,mc_y,eemax_c,eemin_c,eesmax_c,eesmin_c,ecmin_c,ecmin_c/pc)
        #print(pc,mc_x,mc_y,eemax_c,eemin_c,eesmax_c,eesmin_c,ecmin_c)

        # Output to Gui
        ####################
        #self.text_ctrl_result.SetValue(comment)
        self.text_ctrl_nn.SetValue("{:.0f}".format(nn))
        self.text_ctrl_mcx.SetValue("{:.0f}".format(mc_x))
        self.text_ctrl_mcy.SetValue("{:.0f}".format(mc_y))
        self.text_ctrl_max.SetValue("{:.0f}".format(ma_x))
        self.text_ctrl_may.SetValue("{:.0f}".format(ma_y))
        self.text_ctrl_mux.SetValue("{:.0f}".format(mux))
        self.text_ctrl_muy.SetValue("{:.0f}".format(muy))


    ########################################################################
    # Mx-My Relationship
    def OnMxMy(self,event):

        #target_file = self.text_ctrl_1.GetValue()

        id_cal,csvfile,\
            theta,ecumax,ndiv,nn,ecu,esu,\
            mate1,mate2,\
            xx1,yy1,xx2,yy2,ndimx,ndimy,fc,\
            ids,nx,ny,dtx,dty,dia,fy,\
            ibc,fbc,ibt,fbt,outfile\
            =\
            self.read_data()

        obj = fiber.Fiber(xx1,xx2,yy1,yy2,mate1,mate2)
        if obj.getModel(xx1,xx2,yy1,yy2,ndimx,ndimy,fc,\
                        ids,nx,ny,dtx,dty,dia,fy):
            obj.getG(xx1,xx2,yy1,yy2)
            #obj.viewModel(0.5)
            print("Complete Model Making")
        else:
            del obj
            obj = Fiber()
            dlg = wx.MessageDialog(self, 'Erro input',
                                   'Error input',
                                   wx.OK | wx.ICON_ERROR
                                   )
            dlg.ShowModal()
            dlg.Destroy()
            print("Fail Model Making")

        # Spec
        ax     = self.matplotlib_axes
        screen = self.matplotlib_canvas
        self.matplotlib_axes.clear()
        self.matplotlib_canvas.draw()

        div = 32
        obj.mxmy(nn,0,ecu,div,ax,screen)
        #obj.mxmy(nn,3,-esu,16)

    ########################################################################
    # View Conter
    def OnConter(self, event):  # wxGlade: MyFrame.<event_handler>

        # Spec
        ax     = self.matplotlib_axes
        screen = self.matplotlib_canvas
        self.matplotlib_axes.clear()
        self.matplotlib_canvas.draw()

        # Make Model
        #target_file = self.text_ctrl_1.GetValue()
        id_cal,csvfile,\
            theta,ecumax,ndiv,nn,ecu,esu,\
            mate1,mate2,\
            xx1,yy1,xx2,yy2,ndimx,ndimy,fc,\
            ids,nx,ny,dtx,dty,dia,fy,\
            ibc,fbc,ibt,fbt,outfile\
            =\
            self.read_data()

        #plt.tight_layout()
        print("------------------------------")

        obj = fiber.Fiber(xx1,xx2,yy1,yy2,mate1,mate2)
        if obj.getModel(xx1,xx2,yy1,yy2,ndimx,ndimy,fc,\
                        ids,nx,ny,dtx,dty,dia,fy):
            obj.getG(xx1,xx2,yy1,yy2)
            obj.make_cont(nn,theta,ecu,ax,screen)
            print("Complete Model Making")
        else:
            del obj
            obj = Fiber()
            dlg = wx.MessageDialog(self, 'Erro input',
                                   'Error input',
                                   wx.OK | wx.ICON_ERROR
                                   )
            dlg.ShowModal()
            dlg.Destroy()
            print("Fail Model Making")

        #self.matplotlib_canvas.draw()
        del obj
        event.Skip()

    ########################################################################
    # View Model
    def OnPlot(self, event):  # wxGlade: MyFrame.<event_handler>

        # Spec
        ax     = self.matplotlib_axes
        screen = self.matplotlib_canvas
        self.matplotlib_axes.clear()
        self.matplotlib_canvas.draw()

        # Make Model
        #target_file = self.text_ctrl_1.GetValue()
        id_cal,csvfile,\
            theta,ecumax,ndiv,nn,ecu,esu,\
            mate1,mate2,\
            xx1,yy1,xx2,yy2,ndimx,ndimy,fc,\
            ids,nx,ny,dtx,dty,dia,fy,\
            ibc,fbc,ibt,fbt,outfile\
            =\
            self.read_data()

        #plt.tight_layout()
        print("------------------------------")

        obj = fiber.Fiber(xx1,xx2,yy1,yy2,mate1,mate2)
        if obj.getModel(xx1,xx2,yy1,yy2,ndimx,ndimy,fc,\
                        ids,nx,ny,dtx,dty,dia,fy):
            obj.getG(xx1,xx2,yy1,yy2)
            obj.viewModel(0.5,ax,screen)
            print("Complete Model Making")
        else:
            del obj
            obj = Fiber()
            dlg = wx.MessageDialog(self, 'Erro input',
                                   'Error input',
                                   wx.OK | wx.ICON_ERROR
                                   )
            dlg.ShowModal()
            dlg.Destroy()
            print("Fail Model Making")

        #self.matplotlib_canvas.draw()
        del obj
        event.Skip()

    ########################################################################
    # read control data
    def read_cntl(self,readFile):

        df = pd.read_csv(readFile)
        #print(df,len(df))

        self.dbname = './db/test.db'
        table = 'CNTL'
        obj = store.Store(self.dbname)
        obj.make_table(readFile,table)

        print(df)
        self.list_ctrl_input.DeleteAllItems()
        for i in range(0,len(df)):
            self.list_ctrl_input.InsertItem(i,i)
            #self.list_ctrl_input.SetItem(i, 0, "N")
            self.list_ctrl_input.SetItem(i, 0, df.iloc[i,14].replace(' ',''))
            self.list_ctrl_input.SetItem(i, 1, str(i+1))
            self.list_ctrl_input.SetItem(i, 2, df.iloc[i,0].replace(' ',''))
            self.list_ctrl_input.SetItem(i, 3, df.iloc[i,1].replace(' ',''))
            self.list_ctrl_input.SetItem(i, 4, str(df.iloc[i,3]))
            self.list_ctrl_input.SetItem(i, 5, str(df.iloc[i,2]))

    ########################################################################
    # all continuous calculation
    def On_all_cal(self,event):

        # read CNTL file
        conn = sqlite3.connect(self.dbname)
        table = 'CNTL'
        df = pd.read_sql_query('SELECT * FROM %s' % table, conn)
        #print(df)

        self.list_ctrl_input.SetItemState(0,0,wx.LIST_STATE_SELECTED)
        self.list_ctrl_input.Select(0)
        for i in range(0,len(df)):
            #self.list_ctrl_input.Select(-1)
            #self.list_ctrl_input.Select(i)
            #self.OnShow(event)
            self.OnExec(event)
            self.SaveFig(i)
            if i == len(df)-1:break;
            self.list_ctrl_input.SetItemState(i,0,wx.LIST_STATE_SELECTED)
            self.list_ctrl_input.Select(i+1)

    ########################################################################
    # Show
    def OnShow(self,event):

        # get index number
        id_cal = self.list_ctrl_input.GetFirstSelected()
        #print(id_cal)

        # read CNTL file
        """
        conn = sqlite3.connect(self.dbname)
        table = 'CNTL'
        df = pd.read_sql_query('SELECT * FROM %s' % table, conn)
        """

        # get dir. pathname
        cntl = self.text_ctrl_2.GetValue()
        pathname = os.path.dirname(self.text_ctrl_2.GetValue())
        df = pd.read_csv(cntl)
        # get data


        title   = df.iloc[id_cal,0]
        #csvfile = df.iloc[id_cal,1].replace(' ','')
        csvfile = pathname + "/" + df.iloc[id_cal,1].replace(' ','')
        theta   = df.iloc[id_cal,2]
        nn      = df.iloc[id_cal,3]
        ecumax  = df.iloc[id_cal,4]
        ndiv    = df.iloc[id_cal,5]
        ecu     = df.iloc[id_cal,6]
        esu     = df.iloc[id_cal,7]
        come       = df.iloc[id_cal,8].replace(' ','')
        cuvmax     = df.iloc[id_cal,9]
        mumax      = df.iloc[id_cal,10]
        stressmax  = df.iloc[id_cal,11]
        strainmax  = df.iloc[id_cal,12]

        #print(come,cuvmax)
        #print(nn)
        self.text_ctrl_nn.SetValue("{:.0f}".format(nn))
        self.text_ctrl_mcx.SetValue('')
        self.text_ctrl_mcy.SetValue('')
        self.text_ctrl_max.SetValue('')
        self.text_ctrl_may.SetValue('')
        self.text_ctrl_mux.SetValue('')
        self.text_ctrl_muy.SetValue('')

        #
        #print(pathname+"/"+csvfile)
        #target_file = pathname+"/"+csvfile.replace(' ','')

        #target_file = csvfile
        #self.text_ctrl_1.SetValue(target_file)
        self.OnPlot(event)

        ax = []
        screen = []
        ax.append( self.matplotlib_axes2 )
        ax.append( self.matplotlib_axes3 )
        ax.append( self.matplotlib_axes4 )
        screen.append( self.matplotlib_canvas2 )
        for i in range(0,len(ax)):
            ax[i].clear()
        for i in range(0,len(screen)):
            screen[i].draw()


        output_file = self.text_ctrl_2.GetValue()
        pathname = os.path.dirname(self.text_ctrl_2.GetValue())
        df1 = pd.read_csv(output_file)

        if self.list_ctrl_input.GetItemText(id_cal, 0 ) == "Y":
            # m-p
            #table = str(id_cal)+"mp"
            #fiber.AftFib(self.dbname).plotGui(id_cal,ax,screen)
            fiber.AftFib(output_file).plotGui(id_cal,ax,screen)
            # cap
            #conn = sqlite3.connect(self.dbname)
            #table = str(id_cal)+'cap'
            #df = pd.read_sql_query('SELECT * FROM "%s"' % table, conn)
            #conn.close()
            outfile = pathname + "/" + df1.iloc[id_cal,13].replace(' ','')
            df = pd.read_csv(outfile+"cap")

            self.text_ctrl_mcx.SetValue("{:.0f}".format(df.iloc[0,1]) )
            self.text_ctrl_mcy.SetValue("{:.0f}".format(df.iloc[0,2]) )
            self.text_ctrl_max.SetValue("{:.0f}".format(df.iloc[1,1]) )
            self.text_ctrl_may.SetValue("{:.0f}".format(df.iloc[1,2]) )
            self.text_ctrl_mux.SetValue("{:.0f}".format(df.iloc[2,1]) )
            self.text_ctrl_muy.SetValue("{:.0f}".format(df.iloc[2,2]) )


    ########################################################################
    # read data
    def read_data(self):

        ####################
        # ctln data from control file
        # get index number
        id_cal = self.list_ctrl_input.GetFirstSelected()
        #print(id_cal)

        # read CNTL file
        conn = sqlite3.connect(self.dbname)
        table = 'CNTL'
        df = pd.read_sql_query('SELECT * FROM %s' % table, conn)
        #print(df)

        # get dir. pathname
        pathname = os.path.dirname(self.text_ctrl_2.GetValue())

        # get data
        title   = df.iloc[id_cal,0]
        csvfile = pathname + "/" + df.iloc[id_cal,1].replace(' ','')
        #csvfile = df.iloc[id_cal,1]
        theta   = df.iloc[id_cal,2]
        nn      = df.iloc[id_cal,3]
        ecumax  = df.iloc[id_cal,4]
        ndiv    = df.iloc[id_cal,5]
        ecu     = df.iloc[id_cal,6]
        esu     = df.iloc[id_cal,7]

        outfile = pathname + "/" + df.iloc[id_cal,13].replace(' ','')
        #print(outfile)

        # Read Input File From local file
        ####################
        mate1 = []
        mate2 = []
        xx1 = []
        yy1 = []
        xx2 = []
        yy2 = []
        dtx = []
        dty = []
        ndimx = []
        ndimy = []
        fc = []
        ids = []
        nx = []
        ny = []
        dtx = []
        dty = []
        dia = []
        fy = []

        # capacity data
        fbc = 0.0
        fbt = 0.0

        readFile = csvfile

        # read data
        for line in open(readFile, "r"):
            # if first low = "#",  skip the line
            if line[0] == "#":
                continue
            data = line.split(",") # split line and put data into

            # read parameter
            """
            if(data[0] == "CTLN"):
                theta   = float(data[1])
                ecumax  = float(data[2])
                ndiv    = int(data[3])
                nn      = float(data[4])
                ecu     = float(data[5])
                esu     = float(data[6])
            """
            if(data[0] == "MATE"):
                mate1.append( int(data[1]) )
                mate2.append( float(data[2]) )
            if(data[0] == "CAPA"):
                ibc = int(data[1])
                fbc = float(data[2])
                ibt = int(data[3])
                fbt = float(data[4])
            if(data[0] == "FIBE"):
                #print(data)
                xx1.append( float(data[1]) )
                yy1.append( float(data[2]) )
                xx2.append( float(data[3]) )
                yy2.append( float(data[4]) )
                ndimx.append( int(data[5]) )
                ndimy.append( int(data[6]) )
                fc.append( int(data[7]) )
            if(data[0] == "REBA"):
                ids.append( int(data[1]) )
                nx.append( int(data[2]) )
                ny.append( int(data[3]) )
                dtx.append( float(data[4]) )
                dty.append( float(data[5]) )
                dia.append( str(data[6]).replace(' ','') )
                fy.append( int(data[7]) )
        print("Finish to read!")
        return id_cal,csvfile,\
            theta,ecumax,ndiv,nn,ecu,esu,\
            mate1,mate2,\
            xx1,yy1,xx2,yy2,ndimx,ndimy,fc,\
            ids,nx,ny,dtx,dty,dia,fy,\
            ibc,fbc,ibt,fbt,outfile

    ########################################################################
    # Store data
    def OnStore(self,event):
                #
        idView  = self.text_ctrl_idView.GetValue()
        idTotal = self.text_ctrl_idTotal.GetValue()
        #
        ####################
        data = []
        data = self.input_parameter(0)
        #
        ####################
        outFile = './db/rcslab.txt'
        if idTotal == '0':
            fout = open(outFile, "w", encoding='utf-8')
        else:
            fout = open(outFile, "a", encoding='utf-8')

        for i in range(len(data)):
            fout.writelines(str(data[i]))
            fout.writelines(', ')
        fout.writelines('\n')
        fout.close()

        #idView_next = int(idView) + 1
        idView_next = int(idTotal) + 2
        idTotal_next = int(idTotal) + 1
        self.text_ctrl_idView.SetValue(str(idView_next))
        self.text_ctrl_idTotal.SetValue(str(idTotal_next))
        #
        self.text_ctrl_title.SetValue('No.'+str(idView_next))
        #

        self.ListShow()
        self.Clear_R()

        # Pandas Check
        #df = pd.read_csv("./db/rcslab.txt")
        #print(df)


# end of class MyFrame

class MyApp(wx.App):
    def OnInit(self):
        if os.path.exists('./db/test.db'):
            #os.remove('./db/test.db')
            shutil.rmtree('./db')
            os.mkdir('./db')
            print('remove ./db/test.db ^v^!')
        else:
            print('none *db')

        """
        if os.path.exists('./db/*.png'):
            os.remove('./db/*.png')
            print('remove ./db/*.png ^v^!')
        else:
            print('none *png')
        """

        ########################################################################
        self.frame = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()

        return True

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
