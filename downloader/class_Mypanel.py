'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
This is the Mypanel class for GUI module.
It creates the widgets like buttons and textAreas; packs them into container.
It also implements the binding of buttons to various events using functions to
filter, browse location, and download content.

It imports:
    -wx
    -re
    -get_urls
    -downloader_script
It defines:
    -__init__
    -EvtCheckBox
    -select_all
    -select_default
    -enter
    -download
    -browse
    -reset
    -filter
    -EvtCheckListBox
    -close
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
"""Required modules"""
import re,os
import wx
from wx.lib.agw import aquabutton as AB
from wx.lib.agw import pygauge as PG

import get_urls,downloader_script
from class_Menu import Menu
from join_path import opj
from class_preferences import open_pref

#Global constants
#-----------------------------------------------------------------
#reading default value of location from config file
dir_file = open(opj('config.txt'),'r')
default_dir = dir_file.readlines()[0][7:-1]
dir_file.close() 

class Mypanel(object):
    def __init__(self,panel,win):
        self.win = win                                                      #The window object
        self.panel = panel                                                  #The panel object
        
        #window icon
        self.win.SetIcon(wx.Icon(opj('../Icons/Logo.png'),
                       wx.BITMAP_TYPE_PNG))
                       
        #upper container for logo, description, url and dir
        box = wx.StaticBox(self.panel, -1,size=(500,50))
        self.introsizer = wx.StaticBoxSizer(box)

        #---------------------------------------------------------------
        #Images                
        #LOGO
        png = wx.Image(opj('../Icons/Logo.png'),
                       wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        logo = wx.StaticBitmap(panel, -1, png)
        
        #folder
        png = wx.Image(opj('../Icons/folder.png'),
                       wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        folder_icon = wx.StaticBitmap(panel, -1, png,size=(25,30))
        
        loading_icon = wx.Image(opj('../Icons/lightbox-ico-loading2.gif'),
                                wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        #container for loading_icon
        self.loading_icon = wx.StaticBitmap(panel,-1,loading_icon,size=(40,40))
        
        #---------------------------------------------------------------        
        #Description
        sub_container = wx.BoxSizer(wx.VERTICAL)
        description = wx.TextCtrl(self.panel, -1,"\t\t\t\tSJdownloader",size=(460,70),
                                  style=wx.TE_MULTILINE|wx.TE_RICH2|wx.TE_NO_VSCROLL|
                                  wx.TE_READONLY)
        font = wx.Font(20, wx.SWISS,wx.NORMAL, wx.BOLD, False, "Courier New")
        description.SetStyle(1,16,wx.TextAttr("WHITE",(0,162,232,255),font))
        description.AppendText("\nA free internet downloader, Now download It all,\
just enter the url and click start!For more click Show Links!")
        font = wx.Font(10, wx.SWISS,wx.NORMAL, wx.BOLD, False, "Courier New")
        description.SetStyle(17,126,wx.TextAttr("BLACK",(0,162,232,255),font))
        description.SetBackgroundColour((0,162,232,255))
        sub_container.Add(description,0)
        
        self.introsizer.Add(logo,proportion=0)
        self.introsizer.Add(sub_container,proportion=0,flag=wx.EXPAND)
        #--------------------------------------------------------------------------
        #creating buttons, and binding events with them, that occurs on click.

        #calls (enter) method
        show_btn = AB.AquaButton(panel, -1, None, "Links",size=(70,25))
        show_btn.SetBackgroundColour((98,208,255,255))
        show_btn.SetForegroundColour("Black")
        show_btn.SetToolTipString("Click to show found links")
        show_btn.Bind(wx.EVT_BUTTON,self.enter)

        #calls browse method;
        browse_btn = AB.AquaButton(panel, -1, None, "Browse",size=(70,25))
        browse_btn.SetBackgroundColour((98,208,255,255))
        browse_btn.SetForegroundColour("Black")
        browse_btn.SetToolTipString("Select location")
        browse_btn.Bind(wx.EVT_BUTTON,self.browse)
        
        #calls reset method
        reset_btn = AB.AquaButton(panel, -1, None, "Reset",size=(70,25))
        reset_btn.SetBackgroundColour((98,208,255,255))
        reset_btn.SetForegroundColour("Black")
        reset_btn.SetToolTipString("Reset downloader")
        reset_btn.Bind(wx.EVT_BUTTON,self.reset)

        #calls download metod
        self.download_btn = AB.AquaButton(panel, -1, None, "Start",size=(70,25))
        self.download_btn.SetBackgroundColour((98,208,255,255))
        self.download_btn.SetForegroundColour("Black")
        self.download_btn.SetToolTipString("Start download")
        self.download_btn.Bind(wx.EVT_BUTTON,self.download)
        
        close_btn = AB.AquaButton(panel, -1, None, "Close",size=(70,25))
        close_btn.SetBackgroundColour((98,208,255,255))
        close_btn.SetForegroundColour("Black")
        close_btn.SetToolTipString("Close")
        close_btn.Bind(wx.EVT_BUTTON,self.close)
        
        cancel_btn = AB.AquaButton(panel, -1, None, "Cancel",size=(70,25))
        cancel_btn.SetBackgroundColour((98,208,255,255))
        cancel_btn.SetForegroundColour("Black")
        cancel_btn.SetToolTipString("Cancel download")
        cancel_btn.Bind(wx.EVT_BUTTON,self.cancel)

        #calls filter method
        self.filter_btn = AB.AquaButton(panel, -1, None, "Filter",size=(70,25))
        self.filter_btn.SetBackgroundColour((98,208,255,255))
        self.filter_btn.SetForegroundColour("Black")
        self.filter_btn.SetToolTipString("Filter links")
        self.filter_btn.Bind(wx.EVT_BUTTON,self.filter)
        self.filter_btn.Disable()
        
        #--------------------------------------------------------------------------
        #defining text areas; to input text
        '''
        >>>"http://www.google.com/" -> keyed in url_field
        calls (enter)
        >>>C:\Python27 -> keyed in dir
        >>>.*.jpg -> keyed in regex
        '''

        #Static text area:

        #Label, before text box for url
        url = wx.StaticText(panel, -1, "URL:",size=(70,15))
     
        #Label, before text box for dir location
        location = wx.StaticText(panel, -1, "Save file in:",size=(70,15))
        #Count of links
        self.count = wx.StaticText(self.panel,-1,"No. of links found:",
                                       size=(255,15),pos=(420,295))
        #Label, before regex text box
        regex = wx.StaticText(panel, -1, "Enter regex:",pos=(400,310))
        #progress label
        progress = wx.StaticText(panel, -1, "Progress")

        #--------------------------------------------------------------------------
 
        #text box for url, calls (enter) method on text event
        self.url_field = wx.TextCtrl(panel,
                                     size=(0,15),pos=(5,5),                                     
                                     style=wx.TE_PROCESS_ENTER,
                                     )
        self.url_field.SetToolTipString("Enter url here");
        #self.url_field.Bind(wx.EVT_TEXT, self.enter)                                                                   
        
        #text box for showing dir location
        self.dir = wx.TextCtrl(panel,size=(0,15),pos=(5,30))
        #set directory value
        self.dir.SetValue(default_dir)

        self.dir.SetToolTipString("Selected location to save file");

        #Static box For showing links
        self.box = wx.StaticBox(self.panel, -1, "The links will be shown here")
        self.bsizer = wx.StaticBoxSizer(self.box, wx.VERTICAL)
        #adding loading_icon
        self.bsizer.Add(self.loading_icon)
        
        #text box for entering regex pattern
        self.regex = wx.TextCtrl(panel,size=(190,25))
        self.regex.SetToolTipString("Enter type string to filter content");
        self.regex.SetEditable(False)
        #Progress bar
        self.progress = PG.PyGauge(panel,-1,size=(255,20),style=wx.GA_HORIZONTAL)

        #--------------------------------------------------------------------------
        #Defining CheckBoxes

        self.cb1 = wx.CheckBox(panel, -1, "jpeg",
                          (5, 295), (75, 20))
        self.cb2 = wx.CheckBox(panel, -1, "png",
                          (5, 310), (75, 20))
        self.cb3 = wx.CheckBox(panel, -1, "gif",
                          (5, 335), (75, 20))
        self.cb4 = wx.CheckBox(panel, -1, "mp4",
                          (35, 295), (75, 20))
        self.cb5 = wx.CheckBox(panel, -1, "3gp",
                          (35,310), (75, 20))
        self.cb6 = wx.CheckBox(panel, -1, "avi",
                          (35, 335), (75, 20))
        self.cb7 = wx.CheckBox(panel, -1, "flv",
                          (70, 295), (55, 20))
        self.cb8 = wx.CheckBox(panel, -1, "mp3",
                          (70, 310), (55, 20))
        self.cb9 = wx.CheckBox(panel, -1, "jpg",
                          (70, 310), (55, 20))
        self.selectAll = wx.CheckBox(self.panel, -1, "select all",
                              (70, 310), (85, 15))
        self.selectDefault = wx.CheckBox(self.panel, -1, "Apply default filter",
                              (70, 310), (400, 20))
        self.selectDefault.Enable(False)
        
        #Binding events with checkboxes
        
        self.cb1.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox)
        self.cb1.Enable(False)
        self.cb2.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox)
        self.cb2.Enable(False)
        self.cb3.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox)
        self.cb3.Enable(False)
        self.cb4.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox)
        self.cb4.Enable(False)
        self.cb5.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox)
        self.cb5.Enable(False)
        self.cb6.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox)
        self.cb6.Enable(False)
        self.cb7.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox)
        self.cb7.Enable(False)
        self.cb8.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox)
        self.cb8.Enable(False)
        self.cb9.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox)
        self.cb9.Enable(False)
        self.selectAll.Bind(wx.EVT_CHECKBOX, self.select_all)
        self.selectDefault.Bind(wx.EVT_CHECKBOX, self.select_default)
        
        #--------------------------------------------------------------------------

        #WRAPPING UP THE BOXES
        #----------------------
        #The text controls
        #-----------------

        #The url, url label containers                           Container#1
        
        url_box = wx.BoxSizer()                                  
        url_box.Add(url,proportion=0,flag=wx.TOP|wx.RIGHT,border=7)
        url_box.Add(self.url_field,proportion=1,flag=wx.EXPAND|
                    wx.ALL,border=2)
        url_box.Add(show_btn,proportion=0,border=5,flag=wx.LEFT|wx.TOP)

        #The dir location, location label container              Container#2 
        dir_box = wx.BoxSizer()
        dir_box.Add(location,proportion=0,flag=wx.TOP|wx.RIGHT,border=5)
        dir_box.Add(self.dir,proportion=1,flag=wx.ALL|wx.EXPAND,border=2)
        dir_box.Add(folder_icon,proportion=0,border=5,flag=wx.TOP)#|wx.RIGHT)
        dir_box.Add(browse_btn,proportion=0,border=5,flag=wx.LEFT|wx.TOP)
        #--------------------------------------------------------------------------
        #For select all and count box
        self.hbox = wx.FlexGridSizer(cols=2, vgap=10, hgap=250)
        self.hbox.Add(self.selectAll,proportion=0,flag=wx.TOP|wx.LEFT|
                      wx.RIGHT,border=3)
        self.hbox.Add(self.count,proportion=1,flag=wx.TOP|wx.LEFT|
                      wx.RIGHT,border=3)
        
        #container for main output box                           Container#3
        Static_box = wx.BoxSizer()
        Static_box.Add(self.bsizer,proportion=1,flag=wx.EXPAND
                  |wx.ALL,border=3
                  )
        Static_box.Add(reset_btn,proportion=0,border=10,flag=wx.LEFT|wx.TOP)
        #--------------------------------------------------------------------------

        #--------------
        #The checkBoxes
        #--------------
        #First set of boxes vertically
        feature_box1 = wx.BoxSizer(wx.VERTICAL)
        
        feature_box1.Add(self.cb1, proportion=0,flag=wx.EXPAND     #jpeg
                      |wx.LEFT|wx.BOTTOM,border=5)
        feature_box1.Add(self.cb2, proportion=0,flag=wx.EXPAND     #png
                      |wx.LEFT|wx.BOTTOM,border=5)
        feature_box1.Add(self.cb3, proportion=0,flag=wx.EXPAND     #gif
                      |wx.LEFT|wx.BOTTOM,border=5)

        #Second set of boxes vertically
        feature_box2 = wx.BoxSizer(wx.VERTICAL)
        feature_box2.Add(self.cb4, proportion=0,flag=wx.EXPAND     #mp4
                      |wx.ALL,border=2)
        feature_box2.Add(self.cb5, proportion=0,flag=wx.EXPAND     #3gp
                      |wx.ALL,border=2)
        feature_box2.Add(self.cb6, proportion=0,flag=wx.EXPAND     #avi
                      |wx.ALL,border=2)

        #Third set of boxes vertically
        feature_box3 = wx.BoxSizer(wx.VERTICAL)
        feature_box3.Add(self.cb7, proportion=0,flag=wx.EXPAND     #flv
                      |wx.ALL,border=2)
        feature_box3.Add(self.cb8, proportion=0,flag=wx.EXPAND     #mp3
                      |wx.ALL,border=2)
        feature_box3.Add(self.cb9, proportion=0,flag=wx.EXPAND     #jpg
                      |wx.ALL,border=2)
        #--------------------------------------------------------------------------
        
        #-------------------
        #Extra feature boxes
        #-------------------
        #container for regex text box and filter button
        regex_box = wx.FlexGridSizer(cols=3, vgap=10, hgap=3)
        regex_box.Add(regex,proportion=0,flag=wx.TOP,border=7)
        regex_box.Add(self.regex,proportion=1,flag=wx.BOTTOM|wx.LEFT
                      |wx.EXPAND|wx.RIGHT,border=5)
        regex_box.Add(self.filter_btn,proportion=0,
                      flag=wx.TOP|wx.RIGHT|wx.BOTTOM,border=3)

        #container for (regex,filter) container and count text box
        feature_box4 = wx.BoxSizer(wx.VERTICAL)
        feature_box4.Add(regex_box,proportion=0,flag=wx.ALL)
        feature_box4.Add(self.selectDefault,proportion=1,flag=wx.TOP,border=2)
        
        #--------------------------------------------------------------------------
        #container for (checkbox, extra feature) containers     Container#4
        feature_box = wx.BoxSizer()
        feature_box.Add(feature_box1,proportion=0)
        feature_box.Add(feature_box2,proportion=0)
        feature_box.Add(feature_box3,proportion=0)
        feature_box.Add(feature_box4,proportion=0,flag=wx.EXPAND)

        #--------------------------------------------------------------------------

        #container for progres bar                              Container#5
        prog_box = wx.BoxSizer()
        prog_box.Add(progress, proportion=0, flag=wx.ALL,border=5)
        prog_box.Add(self.progress,proportion=1,
                     flag=wx.ALL,border=5)
        prog_box.Add(self.download_btn,proportion=0,border=5,
                     flag=wx.ALL)
        prog_box.Add(cancel_btn, proportion=0, border=5,
                      flag=wx.ALL)
        prog_box.Add(close_btn, proportion=0,border=5,
                     flag=wx.LEFT|wx.TOP)

        #--------------------------------------------------------------------------      
        #container for introsizer and Containers #1,#2,#3,#4,#5
        #-------------------------------------------
        self.main_container = wx.BoxSizer(wx.VERTICAL)
        sub_container.Add(url_box,proportion=0,flag=wx.EXPAND)
        sub_container.Add(dir_box,proportion=0,flag=wx.EXPAND)
        self.main_container.Add(self.introsizer,proportion = 0,flag=wx.EXPAND)
        self.main_container.Add(self.hbox,proportion=0,flag=wx.EXPAND)
        self.main_container.Hide(self.hbox)
        self.panel.Layout()
        self.main_container.Add(Static_box,proportion=1,
                           flag=wx.EXPAND)
        self.main_container.Add(feature_box,proportion=0)
        self.main_container.Add(prog_box,proportion=0)
      
        panel.SetSizer(self.main_container)
        self.win.CenterOnScreen()
        #--------------------------------------------------------------------------
        
        #an empty list for showing filtered links.
        self.filtered = []
        #for keeping track of old regex filtered list; used in (filter)
        self.old_filtered = []
        #to take note of checkboxes checked or unchecked
        self.checked_boxes = []
        #for select_all method, to keep track of checked items
        self.checked_items = []
        #to keep urls that were filtered manually, if default was unchecked
        self.preserve_filter = []
        #List for checked links to download;
         #used in (enter),(filter),(EvtCheckBox)
        self.countLink = 0
        menu = Menu(self.win)
        
    #--------------------------------------------------------------------------
    def EvtCheckBox(self, event):
        check_box = event.GetEventObject()
        regex = '.*\.'+check_box.GetLabelText()                       #creating a regex pattern based on
                                                                                                     #the label str of selected checkbox.
        try:            
            filtered = re.findall(regex, '\n'.join(self.urls),re.I|re.M)

            if event.IsChecked():
                self.checked_boxes.append(check_box.GetLabelText())

                if filtered:
                    self.filtered.extend(filtered)
                    self.box.SetLabel("")
                    self.count.SetLabel("No. of links found: "+str(len(self.filtered)))
                    self.main_container.Show(self.hbox)
                    self.panel.Layout()
                else:
                    self.box.SetLabel("No links matched, try another filter; or to show all links, click 'show links' button")
                    if not self.filtered:
                        self.main_container.Hide(self.hbox)
                        self.panel.Layout()
                    
                self.check_list.SetItems(self.filtered)
                if self.selectAll.IsChecked():
                    self.select_all()
                    
            else:
                self.checked_boxes.remove(check_box.GetLabelText())
                self.box.SetLabel("")
                for item in filtered:
                    self.filtered.remove(item)

                self.check_list.SetItems(self.filtered)
                self.count.SetLabel("No. of links found: "+str(len(self.filtered)))

                if not self.checked_boxes:
                    self.main_container.Show(self.hbox)
                    self.panel.Layout()
                    self.check_list.SetItems(self.urls)
                    self.count.SetLabel("No. of links found: "+str(self.countLink))
                        
                elif not self.filtered:
                    self.box.SetLabel("No links matched, try another filter; or to show all links, click 'show links' button")           
                    self.main_container.Hide(self.hbox)
                    self.panel.Layout()

                if self.selectAll.IsChecked():
                    self.select_all()
                                    
            self.check_list.Bind(wx.EVT_CHECKLISTBOX, self.EvtCheckListBox) 
            #self.check_list.SetSelection(0)
        except Exception as e:
            print e
            
    #--------------------------------------------------------------------------
    def select_all(self, *event):
        if self.selectAll.IsChecked():
            if self.filtered:
                 try:
                    self.checked_items = self.filtered
                    indices = range(len(self.filtered))
                    self.check_list.SetChecked(indices)
                 except Exception as e:
                     print e
            else:
                try:
                    self.checked_items = self.urls
                    indices = range(len(self.urls))
                    self.check_list.SetChecked(indices)
                except Exception as e:
                    print e
        else:
            try:
                for index in xrange(len(self.checked_items)):
                    self.check_list.Check(index,False)
            except:
                pass
            
    #--------------------------------------------------------------------------
    def select_default(self, event):
        if event.IsChecked():
            print 'disable all other filters'
            self.filter_btn.Disable()
            self.cb1.Enable(False)
            self.cb2.Enable(False)
            self.cb3.Enable(False)
            self.cb4.Enable(False)
            self.cb5.Enable(False)
            self.cb6.Enable(False)
            self.cb7.Enable(False)
            self.cb8.Enable(False)
            self.cb9.Enable(False)
            self.regex.SetEditable(False)

            self.filter()

            self.panel.Layout()
        else:
            #enable all other filters
            self.filter_btn.Enable()
            self.cb1.Enable(True)
            self.cb2.Enable(True)
            self.cb3.Enable(True)
            self.cb4.Enable(True)
            self.cb5.Enable(True)
            self.cb6.Enable(True)
            self.cb7.Enable(True)
            self.cb8.Enable(True)
            self.cb9.Enable(True)
            self.regex.SetEditable(True)

            self.panel.Layout()
            
            self.box.SetLabel("")
            if self.preserve_filter:
                self.filtered = self.preserve_filter
                self.check_list.SetItems(self.filtered)
                self.count.SetLabel("No. of links found: "+str(len(self.filtered)))
            else:
                self.check_list.SetItems(self.urls)
                self.count.SetLabel("No. of links found: "+str(self.countLink))
            self.panel.Layout()                    
            
                       
    #--------------------------------------------------------------------------
    def enter(self, event):
        '''
        The function to prepare a list of all urls found on home page,
        It works on text_enter_event of textctrl box called 'url'.
        '''
        global default_dir
        
        #Fetching urls
        home_url = self.url_field.GetValue().strip()
        if home_url == "":
            self.url_field.SetValue("Please enter url")
            return
        self.box.SetLabel("Fetching...")
        self.loading_icon.Show()
        error, self.urls = get_urls.main(home_url)

        #if urls fetched
        if self.urls:
            self.countLink = len(self.urls)
            
            self.main_container.Show(self.hbox)
            #Enabling the checkboxes, and buttons
            self.cb1.Enable(True)
            self.cb2.Enable(True)
            self.cb3.Enable(True)
            self.cb4.Enable(True)
            self.cb5.Enable(True)
            self.cb6.Enable(True)
            self.cb7.Enable(True)
            self.cb8.Enable(True)
            self.cb9.Enable(True)
            self.selectDefault.Enable(True)

            self.filter_btn.Enable()
            self.regex.SetEditable(True)

            #--------------------------------------------------------------
            #Creating check list box
            try:
                self.check_list.Destroy()
                self.filtered = []
            except:
                pass

            self.check_list = wx.CheckListBox(self.panel, -1, (5,150),
                                              (490,120),self.urls,
                                              style = wx.HSCROLL)
            self.count.SetLabel("No. of links found: "+str(self.countLink))
            self.box.SetLabel("")
            
            self.bsizer.Add(self.check_list,proportion=1,flag=wx.EXPAND
                      |wx.ALL,border=2
                      )
                      
            self.panel.Layout()
            self.check_list.Bind(wx.EVT_CHECKLISTBOX, self.EvtCheckListBox)
        else:
            print error
            
    #--------------------------------------------------------------------------
    def filter(self,*event):
        '''
        The function filters links found on the page.
        It uses regex to filter and display a list of urls matching the pattern.
        The pattern is specified in the box called regex.
        '''
        #if default filter applied
        if self.selectDefault.IsChecked():
            self.preserve_filter = self.filtered
            self.filtered = []
            patternFile = open(opj('config.txt'),'r')
            pattern = patternFile.readlines()[1][9:-1]
        else:
            pattern = self.regex.GetValue()
            
        try:
             if self.urls:
                 filtered = None
                 if pattern:
                     filtered = re.findall(pattern,'\n'.join(self.urls),re.I|re.M)
                     self.filtered.extend(filtered)
                     if not self.selectDefault.IsChecked():
                         self.old_filtered = filtered

                 elif self.old_filtered:
                     for item in self.old_filtered:
                         self.filtered.remove(item)
                     self.old_filtered = []
                         
                 if pattern and not filtered:
                     self.box.SetLabel("No links matched, try another filter; or to show all links, click 'show links' button")

                 if self.filtered:
                     self.check_list.SetItems(self.filtered)
                     self.count.SetLabel("No. of links found: "+str(len(self.filtered)))
                 else:
                     self.check_list.SetItems(self.urls)
                     self.count.SetLabel("No. of links found: "+str(self.countLink))
               
                 self.check_list.Bind(wx.EVT_CHECKLISTBOX, self.EvtCheckListBox) 
                 self.check_list.SetSelection(0)
        except Exception as e:
            print e
        
    def EvtCheckListBox(self, event):
        '''
        Function to implement checking and unchecking of list items.
        Also, according to checking and unchecking, adds and removes
        items to/from download list.
        '''
        index = event.GetSelection()
        label = self.check_list.GetString(index)
        status = 'un'
        string_at_index = self.check_list.GetString(index)
        
        if self.check_list.IsChecked(index):
            status = ''
            self.check_list.SetSelection(index)                             #so that (un)checking also selects (moves the highl

    #--------------------------------------------------------------------------
    def download(self,event):
        '''
        The function is bind with download button and download the content.
        It fetches urls from the 'contents' textctrl and sends urls to
        downloader_script.
        Uses 'browse' filedialogs current path to save files.
        '''
        global default_dir

        if not(self.url_field.GetValue() == ""):                           #If url field is not empty
            if self.dir.GetValue() == "":                                  #if dir field is empty       

                self.dir.SetValue(default_dir)
                self.path = default_dir.replace("\n","")
            self.path = default_dir.replace("\n","")
            self.box.SetLabel("Fetching.....")
                
            try:
                urls_to_download = self.check_list.GetCheckedStrings()              
                error = downloader_script.main(urls_to_download,self.path,
                                               self.progress)
                self.progress.SetValue(100)
    
            except AttributeError:
                error = downloader_script.main([self.url_field.GetValue().strip()],self.path,
                                               self.progress)
                self.progress.SetValue(100)
            if error:
                print error
                dlg = wx.MessageDialog(self.panel,str(error),
                                       'Oops!', wx.OK|wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
            
        else:
            self.url_field.SetValue("Please Enter url")

    #--------------------------------------------------------------------------
    def browse(self,event):
        '''
        The function is bind with the browse button.
        It opens a directory location.
        Treats the dir input in dir_ box as the default.
        '''
        
        dir_= self.dir.GetValue()
        dlg = wx.DirDialog(self.win, "Choose a directory:",
                          style=wx.DD_DEFAULT_STYLE
                           | wx.DD_DIR_MUST_EXIST
                           | wx.DD_CHANGE_DIR
                           )

        dlg.SetPath(dir_)
        if dlg.ShowModal() == wx.ID_OK:
            self.path = dlg.GetPath()
            self.dir.SetValue(self.path)

        dlg.Destroy()
        
    #--------------------------------------------------------------------------
    def reset(self,event):
        '''
        This is bound to reset button, when pressed, it clears all text areas.
        '''
        self.url_field.SetValue(" ")
        try:
            self.check_list.Destroy()
        except Exception:
            pass
        self.regex.SetValue(" ")
        self.path = " "
        self.box.SetLabel("The links will be shown here")
        self.main_container.Hide(self.hbox)
        
        #Disabling all checkboxes
        self.cb1.Enable(False)
        self.cb2.Enable(False)
        self.cb3.Enable(False)
        self.cb4.Enable(False)
        self.cb5.Enable(False)
        self.cb6.Enable(False)
        self.cb7.Enable(False)
        self.cb8.Enable(False)
        self.cb8.Enable(False)
        self.cb1.SetValue(False)
        self.cb2.SetValue(False)
        self.cb3.SetValue(False)
        self.cb4.SetValue(False)
        self.cb5.SetValue(False)
        self.cb6.SetValue(False)
        self.cb7.SetValue(False)
        self.cb8.SetValue(False)
        self.cb9.SetValue(False)
        self.selectAll.SetValue(False)
        self.selectDefault.Enable(False)
        
        self.filter_btn.Disable()        
        self.regex.SetEditable(False)
        
        self.panel.Layout()

    #--------------------------------------------------------------------------
    def cancel(self, event):
        downloader_script.stop = True
        self.win.Destroy()
    
    def close(self, event):
        self.win.Destroy()
