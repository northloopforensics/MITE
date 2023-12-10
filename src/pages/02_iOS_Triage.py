##  Triage

##       ToDo
#   Storage Space
#   Backup include full designation

import json
from pymobiledevice3.lockdown import create_using_usbmux 
from pymobiledevice3.services import installation_proxy, screenshot
from pymobiledevice3.services.afc import AfcService, AfcShell
from pymobiledevice3.services.screenshot import ScreenshotService
from pymobiledevice3.services.dvt.instruments.screenshot import Screenshot
from pymobiledevice3.services.dvt.dvt_secure_socket_proxy import DvtSecureSocketProxyService
from pymobiledevice3.cli.afc import afc_ls, afc_pull
import pandas as pd
import streamlit as st
import iDevice_Model
import os
from pymobiledevice3.services.mobilebackup2 import Mobilebackup2Service
from pymobiledevice3.utils import try_decode
# from pymobiledevice3.services.base_service import BaseService
from pymobiledevice3.services import syslog
from pymobiledevice3.services.os_trace import OsTraceService
from pymobiledevice3.services.syslog import SyslogService
from pymobiledevice3.usbmux import list_devices
import datetime
import time
from reportlab.lib import pagesizes
from reportlab.pdfbase.pdfdoc import PDFText
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Frame, Spacer
from reportlab.platypus import KeepInFrame, HRFlowable
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import LETTER, landscape, portrait
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas 
from reportlab.platypus.flowables import KeepTogether

##################      Streamlit HTML CSS Stuff    #######################
#Custom button color to bring prominence to executable actions
m = st.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: #ff0000;
            color:#ffffff;
        }
        div.stButton > button:hover {
            background-color: #8b0000;
            color:#ff0000;
            }
        </style>""", unsafe_allow_html=True)

shrink_sidebar_top = st.markdown("""
  <style>
    .css-1helkxk.e1fqkh3o9 {
      margin-top: -50px;
    }
  </style>
""", unsafe_allow_html=True)
#This removes Streamlit default settings icons
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

update_msg = st.empty()
 
def work_site():                #cause script to execute in directory containing script
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  #move to dir that holds this script and ADB (need to change for exe)
    global pwd
    pwd = os.path.dirname(os.path.abspath(__file__))
    
def get_report_settings():
    with open("../Support_Files/last.config", "r") as last_input:
        content = last_input.read()
        result_dict = json.loads(content)
        last_inv = result_dict["Examiner"]
        last_agency = result_dict["Organization"]
        last_ReportFolder = result_dict["Report Location"]
    return last_inv, last_agency, last_ReportFolder



def add_logo():     #Places MITE logo in upper left
    st.sidebar.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url("data:image/png;base64,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");
                background-repeat: no-repeat;
                padding-top: 85px;
                position: relative;
                background-position: 20px 20px;
            }
            [data-testid="stSidebarNav"]::before {
                content: "MITE";
                margin-left: 20px;
                margin-top: 20px;
                color: #797979;
                font-size: 75px;
                font-family: impact;
                position: relative;
                top: 50px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
add_logo()

if list_devices() == []:
    st.write("Attach an unlocked iOS device and 'Trust' this workstation. ")
    TESTCONNECTION = st.button("Test for Connection", key="TESTCONNECTION")
    st.write(" ")
    st.write(" ")
    st.caption("Tips: ")
    st.caption("- Change Display lock time to 'Never'")
    st.caption("- Disable wireless connectivity on device")
    st.caption("- Be prepared to monitor activity")
    st.caption("- Be prepared to enter passcode") 
    st.caption("""If subject device is attached but not recognized, or backups fail repeatedly, perform a power cycle on the device.
    """)
    if TESTCONNECTION == True:
        list_devices()
else:

    lock_Handshake = create_using_usbmux()
    now = datetime.datetime.now()
    stamp = now.strftime("%Y%m%d%H%M%S")
    bluetooth_Mac = ""
    device_Name = ""
    wifi_Mac = ""
    casenum = ""
    MEID = ""
    IMEI = []
    IMSI = ""
    ICCID = ""
    carrier_Bundle = ""
    phonenumber = ""
    app_Listing = []
    file_Listing = []
    itunes_installed_applications = []
    itunes_deleted_applications = []
    domain_list = []
    profile_list = ["None Selected"]
    comparison_filenames = []           #   filenames from profile
    comparison_hashes = []              #   hashes from profile
    comparison_keywords = []            #   keywords from profile
    profile = ""
    match_filenames =[]                 #   Match results between device and profile
    match_hashes = []
    match_keywords = []
 
    st.header("iOS Triage")

    # try:
    all_iOS_IDs = lock_Handshake.all_domains    # pulls info from function all_domains
        # print(all_iOS_IDs)
    # except Exception:
    #     st.error("Please check device connection and trust status.")
    def Lockdown_Identifiers():
        for i in all_iOS_IDs:
            # print(i)
            domain_list.append(i)
            if "com.apple.iTunes" in i:         #   This is a dictionary of lists showing installed and deleted apps
                # print(i)
                # print(all_iOS_IDs[i])
                try:
                    itunes_deleted_applications.extend(dict(all_iOS_IDs[i])['DeletedApplications'])
                    itunes_installed_applications.extend(dict(all_iOS_IDs[i])['LibraryApplications'])
                except KeyError:
                    print("** No iTunes app data to populate **")
                    pass
                
            if "BluetoothAddress" in i:         #   BT mac
                # print(i)
                # print(all_iOS_IDs[i])
                global bluetooth_Mac
                bluetooth_Mac = (all_iOS_IDs[i])

            if "ProductVersion" in i:
                global iOSversion
                iOSversion = all_iOS_IDs[i]
            if "DeviceName" in i:         #   device name
                # print(i)
                # print(all_iOS_IDs[i])
                global device_Name
                device_Name = (all_iOS_IDs[i])
            if "InternationalMobileEquipmentIdentity" in i:         #   device name
                # print(i)
                # print(all_iOS_IDs[i])
                global IMEI
                # print(all_iOS_IDs[i])
                IMEI = (all_iOS_IDs[i])     #   fix it so both imeis show up 
                # IMEI = (IMEI).split(',')
                # IMEI =(all_iOS_IDs[i])
            if "CarrierBundleInfoArray" in i:         #    Carrier data and IDs
                # print(i)
                try:
                    carrierentry = (all_iOS_IDs[i])[0]
                    # print(carrierentry)
                    global ICCID
                    ICCID = (carrierentry['IntegratedCircuitCardIdentity'])
                    global IMSI
                    IMSI = (carrierentry['InternationalMobileSubscriberIdentity'])
                    global carrier_Bundle
                    carrier_Bundle = (carrierentry['CFBundleIdentifier'])
                    global MEID
                    MEID = (carrierentry['MobileEquipmentIdentifier'])
                except IndexError:
                    print("No carrier info to report")
                    pass
                except KeyError:
                    print("No MEID found on phone")
                    pass
            if "ProductType" in i:         #   device name
                # print(i)
                # print(all_iOS_IDs[i])
                global device_Model
                device_Model = iDevice_Model.Get_iModel(all_iOS_IDs[i])     # Checks dictionary and returns friendly name


            if "SerialNumber" in i and not "Baseband" in i and not "Wireless" in i:         #   serial number - removes baseband serial num and wireless board serial num
                # print(i)
                # print(all_iOS_IDs[i])
                global serial_Number
                serial_Number = all_iOS_IDs[i]
            if "com.apple.disk_usage" in i and not "factory" in i:         #   device name
                # print(i)
                diskUse = (all_iOS_IDs[i])
                total_Disk_size = diskUse['TotalDiskCapacity']
                global total_size_in_GB
                total_size_in_GB = str(round(total_Disk_size / 1000 /1000 / 1000))
                global used_size_in_GB
                used_Disk_size = diskUse['TotalDataCapacity']
                used_size_in_GB = str(round(used_Disk_size / 1024 / 1024 / 1024))
                
                
            if "com.apple.disk_usage.factory" in i:         #   device name
                # print(i)
                app_storage = (all_iOS_IDs[i])
                global calendar_storage
                calendar_storage = app_storage["CalendarUsage"]
                global camera_storage
                camera_storage = app_storage['CameraUsage']
                global notes_storage
                notes_storage = app_storage['NotesUsage']
                global photo_storage
                photo_storage = app_storage['PhotoUsage']
            if "PhoneNumber" in i:
                global phonenumber
                phonenumber = all_iOS_IDs[i]
            if "WiFiAddress" in i:
                global wifi_Mac
                wifi_Mac = all_iOS_IDs[i]


    # print("total - " + total_size_in_GB + "GB     Used - " + used_size_in_GB + "GB")

    def identifiers_view():
        # try:
            devd =  {"Attached Device":[device_Model,device_Name,serial_Number, IMEI, MEID,
            phonenumber,IMSI,ICCID,carrier_Bundle, iOSversion, bluetooth_Mac, wifi_Mac]}
                    
            props = pd.DataFrame(devd, index=["Model","Device Name","Serial Number","IMEI","MEID", "Phone Number", "IMSI", "ICCID",
            "Carrier Bundle", "iOS Version", "Bluetooth MAC", "WiFi MAC"])
            st.table(props)

    def Get_Applications():
        app_Library = (installation_proxy.InstallationProxyService(lockdown=lock_Handshake).get_apps())     #   returns dictionary of app elements
        
        for i in app_Library:
            if 'apple' not in i:
                app_Name = app_Library[i]['CFBundleDisplayName']
                cleanApp = app_Name.strip("\u200e")     #   thank you Whatsapp
                app_Listing.append(cleanApp)
        app_Listing.sort()
        st.subheader("Installed 3rd Party Applications")
        for ap in app_Listing:
            st.write(ap)


    def make_report_folders():
        
        global Case_Folder
        Case_Folder = (report_root + '/MITE_Cases/' + str(casenum) + "_" + device_Model + "_" + device_Name + "_" + stamp) 
        os.makedirs(Case_Folder)
        os.makedirs(str(Case_Folder) + '/Backups & Exports')
        os.makedirs(str(Case_Folder) + '/Reports')
        global backuplocation
        backuplocation = Case_Folder + '/Backups & Exports/'
    
    def make_report(folder):
    #   Start with raw text reports for large output
        print("make report test - folder = " + folder)
        with open(folder + '/Reports/' + device_Model + '_' + now.strftime(" %Y%m%d%H%M%S") + '_Media_File_List.txt', 'w', encoding='utf-8') as file_report:
            file_report.write('Case Number: ' + casenum +'\n\n')
            file_report.write('Device Name: ' + device_Model +'\n\n')
           
            file_report.write('Serial No.:        ' + serial_Number +'\n\n')
           
            file_report.write('Files stored at var/mobile/Media:\n\n')
            for ele in file_Listing:
                file_report.write(ele + '\n')
        with open(folder +'/Reports/' + device_Model + '_' + now.strftime(" %Y%m%d%H%M%S") + '_Application_List.txt', 'w') as app_report:
            app_report.write('Case Number: ' + casenum +'\n\n' )
            app_report.write('Device Name: ' + device_Model +'\n\n')
            
            app_report.write('Serial No.:        ' + serial_Number +'\n\n')
            
            app_report.write('Installed 3rd Party Applications\n\n')
            for op in app_Listing:
                app_report.write(op + '\n') 
        # make lists of matches for filenames, hashes, and keywords 
        if len(comparison_filenames) > 0:
            for ele in file_Listing:
                for nam in comparison_filenames:
                    if nam in ele:
                        match_filenames.append(ele)
                        # print('match name' + ele)

                        
        if len(comparison_keywords) > 0:
            for ele in file_Listing:
                for wrd in comparison_keywords:
                    if wrd in ele:
                        match_keywords.append(ele)

        ##########      PDF REPORT STUFF    ####################    
        global pdfReportPages
        pdfReportPages = (Case_Folder + "/MITE_Triage_Report_" + now.strftime(" %Y%m%d%H%M%S") + ".pdf")
        global doc
        doc = SimpleDocTemplate(pdfReportPages, pagesize=LETTER)

        # container for the "Flowable" objects
        global elements
        elements = []
        styles=getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Table Normal', fontName ='Helvetica',fontSize=8, leading=10,backColor = colors.white, textColor=colors.black, alignment=TA_LEFT))
        styleA = styles["Table Normal"]
        styleN = styles["BodyText"]
        styleH = styles["Heading1"]
        w, t, c = '100%', 2, 'darkgrey'
        elements.append(Paragraph("<i><font color='Darkslategray'>MITE TRIAGE REPORT</font></i>", styleH))
        elements.append(HRFlowable(width=w, thickness=t, color=c, spaceBefore=2, vAlign='MIDDLE', lineCap='square'))    #   Border
        elements.append(Paragraph(" ", styleN))
        elements.append(Paragraph("<font color='Darkslategray'>Investigator: </font>" + inv, styleN))
        elements.append(Paragraph("<font color='Darkslategray'>Agency: </font>" + agency, styleN))
        
        
        elements.append(Paragraph(" ", styleN))
        elements.append(HRFlowable(width=w, thickness=t, color=c, spaceBefore=2, vAlign='MIDDLE', lineCap='square'))    #   Border
        elements.append(Paragraph(" ", styleN))
        
        elements.append(Paragraph("<i><font color='Darkslategray'>Date/Time: </font></i>" + now.strftime("%m/%d/%Y %H:%M:%S"), styleN))
        elements.append(Paragraph("<i><font color='Darkslategray'>Case Number: </font></i>" + casenum, styleN))
        # elements.append(Paragraph("<font color='Darkslategray'>Search Authority: </font>" + search_authority, styleN))

        elements.append(Paragraph(" ", styleN))
        elements.append(HRFlowable(width=w, thickness=t, color=c, spaceBefore=2, vAlign='MIDDLE', lineCap='square'))    #   Border
        elements.append(Paragraph(" ", styleN))
        
        elements.append(Paragraph("<i><font color='Darkslategray'>Device Manufacturer: </font></i>" + "Apple", styleN))
        elements.append(Paragraph("<i><font color='Darkslategray'>Device Model: </font></i>" + device_Model, styleN))
        elements.append(Paragraph("<i><font color='Darkslategray'>Device Name: </font></i>" + device_Name, styleN))
        elements.append(Paragraph("<i><font color='Darkslategray'>Device Serial: </font></i>" + serial_Number, styleN))
        try:
            elements.append(Paragraph("<i><font color='Darkslategray'>IMEI: </font></i>" + IMEI, styleN))
        except TypeError:
            pass
        elements.append(Paragraph("<i><font color='Darkslategray'>iOS Version: </font></i>" + iOSversion, styleN))

        elements.append(Paragraph(" ", styleN))
        elements.append(HRFlowable(width=w, thickness=t, color=c, spaceBefore=2, vAlign='MIDDLE', lineCap='square'))    #   Border
        elements.append(Paragraph(" ", styleN))

        elements.append(Paragraph("<i><font color='Darkslategray'>SIM Carrier: </font></i>" + carrier_Bundle, styleN))
        elements.append(Paragraph("<i><font color='Darkslategray'>Phone Number: </font></i>" + phonenumber, styleN))
        elements.append(Paragraph("<i><font color='Darkslategray'>ICCID: </font></i>" + ICCID, styleN))
        elements.append(Paragraph("<i><font color='Darkslategray'>Bluetooth MAC: </font></i>" + bluetooth_Mac, styleN))
        elements.append(Paragraph("<i><font color='Darkslategray'>WiFi MAC: </font></i>" + wifi_Mac, styleN))
        

        elements.append(Paragraph(" ", styleN))
        elements.append(HRFlowable(width=w, thickness=t, color=c, spaceBefore=2, vAlign='MIDDLE', lineCap='square'))    #   Border
        elements.append(Paragraph(" ", styleN))

        elements.append(Paragraph("<i><font color='Darkslategray'>Installed 3rd Party Applications on Device:</font></i>", styleN))
        for item in app_Listing:
            if len(item) > 3:
                elements.append(Paragraph("·&nbsp;&nbsp;" + item, styleA))

        elements.append(Paragraph(" ", styleN))
        elements.append(HRFlowable(width=w, thickness=t, color=c, spaceBefore=2, vAlign='MIDDLE', lineCap='square'))    #   Border
        elements.append(Paragraph(" ", styleN))

        if profile != "None Selected":

            elements.append(Paragraph("<i><font color='Darkslategray'>SEARCH RESULTS</font></i>", styleN))
            elements.append(Paragraph("  ", styleN))
            elements.append(Paragraph("<i><font color='Darkslategray'>File Name Hits: </font></i>", styleN))
            elements.append(Paragraph(" ", styleN))

            if len(comparison_filenames) > 0:
                if len(match_filenames) == 0:
                    elements.append(Paragraph("No matching filenames found.", styleA))
                if len(match_filenames) > 0:
                    for hit in match_filenames:
                        elements.append(Paragraph("·&nbsp;&nbsp;" + hit, styleA))
            
            elements.append(Paragraph(" ", styleN))
            elements.append(HRFlowable(width=w, thickness=t, color=c, spaceBefore=2, vAlign='MIDDLE', lineCap='square'))
            elements.append(Paragraph(" ", styleN))

            if len(comparison_keywords) > 0:
                elements.append(Paragraph("<i><font color='Darkslategray'>Keyword Hits: </font></i>", styleN))
                elements.append(Paragraph(" ", styleN))
                if len(match_keywords) == 0:
                    elements.append(Paragraph("No matching keywords found.", styleA))
                if len(match_keywords) > 0:
                    for hit in match_keywords:
                        elements.append(Paragraph("·&nbsp;&nbsp;" + hit, styleA))
                
            elements.append(Paragraph(" ", styleN))
            elements.append(HRFlowable(width=w, thickness=t, color=c, spaceBefore=2, vAlign='MIDDLE', lineCap='square'))
            elements.append(Paragraph(" ", styleN))

        elements.append(Paragraph("<i><font color='Darkslategray'>Examiner Notes: </font></i>", styleN))
        elements.append(Paragraph(notes, styleN))

        elements.append(Paragraph(" ", styleN))
        elements.append(HRFlowable(width=w, thickness=t, color=c, spaceBefore=2, vAlign='MIDDLE', lineCap='square'))    #   Border
        elements.append(Paragraph(" ", styleN))

        doc.build(elements) 

    # def afc_shell(lockdown: lock_Handshake):
    #     """ open an AFC shell rooted at /var/mobile/Media """
    #     AfcShell(lockdown=lockdown, service_name='com.apple.afc').cmdloop()

    def Get_file_list():            #   Walks the ios device at var/mobile/media 
        for path in AfcService(lockdown=lock_Handshake).dirlist(".", -1):
            path = path.upper()
            file_Listing.append(path)
            file_Listing.sort()

    def read_profile():                 #   function reads selected user created profile
        #   Reads triage profile. Grabs values between brackets to add to appropriate list in global variables
        clean_list = []
        if profile == "None Selected":
            pass
        if profile != "None Selected":
            parentname = os.path.dirname(pwd)
            pathtoprofile = (parentname + "/Profiles/")
            with open(pathtoprofile + profile, 'r') as selected_profile:
                
                prof = selected_profile.readlines()
                                
                for ele in prof:
                    ele = ele.upper()                   #   Makes all profile entries uppercase to prevent hash and string mismatches
                    cl = ele.replace('\n','')           #   removes '\n' from elements
                    clean_list.append(cl)
            clean_list = list(filter(None, clean_list))     #removes empty elements from list
            try:                    
                for i in clean_list:                        #   Loop gets list position for each bracketed marker, grabbing the data by type and adding them to a list
                    if '[FILENAMES]' in i:                  #   Making this uppercase because of ele.upper() above - still mixed case in profile file itself
                        first = clean_list.index(i)
                    if '[HASHES]' in i:
                        second = clean_list.index(i)
                    if '[KEYWORDS]' in i:
                        third = clean_list.index(i)
                #   Moves batches to respective lists
                comparison_filenames.extend(clean_list[first+1:second])       
                comparison_hashes.extend(clean_list[second+1:third])
                comparison_keywords.extend(clean_list[third+1:]) 
            except ValueError:
                st.error("Profile file is corrupt")

    def get_profiles():         #List of user created profiles
        # for profs in os.listdir(pwd + "/Profiles"):
        parentname = os.path.dirname(pwd)
        rootname = os.path.dirname(parentname)
        print(parentname)
        # point to the parent directory and then to the Profiles folder
        pathtoprofiles = (parentname + "/Profiles")
        # print(pathtoprofiles)
        for profs in os.listdir(pathtoprofiles):
            if not profs.startswith("."):
                profile_list.append(profs)
    
    work_site()
    get_report_settings()
    get_profiles()
    Lockdown_Identifiers()
    identifiers_view()
    Get_Applications()
    
    def show_triage_results():
        if len(match_filenames) > 0:            #   FILE MATCHES
            st.header("File Name Matches")
            for fil in match_filenames:
                st.write(fil)
            st.markdown("---")
        if len(match_keywords) > 0:             #   KEYWORD MATCHES
            st.header("Keyword Matches")
            for wd in match_keywords:
                st.write(wd)
            st.markdown("---")

    def ios_backup(store_location):
            
        backup_client = Mobilebackup2Service(lock_Handshake)
     
        # #   Try to enable encrypted backup
        # backup_client.change_password(backup_directory=store_location,new="1234")
        
        
        time.sleep(3)
        backup_client.backup(full=True, backup_directory=store_location)
       
        # try:
        #     backup_client.unback(backup_directory=(backuplocation + "/UnpackedData/"))   MOVED TO PREVIEW AREA
        # except Exception:
        #     pass

    def syslog_collect(lockdown, save_log_to, size_limit, age_limit, start_time):

        if os.path.isdir(save_log_to):
            out = os.path.join(save_log_to, 'system_logs.logarchive')

        if not os.path.exists(save_log_to):
            os.makedirs(save_log_to)

        
        OsTraceService(lockdown=lock_Handshake).collect(save_log_to, size_limit=size_limit, age_limit=age_limit, start_time=start_time)
 

    # def unpack_backup(backupfolder, unpacktothisfoler):                   # This got moved to preview area
    #     Mobilebackup2Service.unback(backup_directory=backupfolder, )
  
    inv, agency, report_root = get_report_settings() 
    

    # Backup Checkboxes & Button
    casenum = st.sidebar.text_input(":red[Case Number*]", key="CASENUM", )
    profile = st.sidebar.selectbox("Triage Profile", profile_list)
    # unpackiOS = st.checkbox("Unpack iOS Backup to Folder Structure")
    triage_Data = st.sidebar.checkbox("Triage Data", value=True)
    backup_check = st.sidebar.checkbox("iOS Backup", value=True)
    # pull_media_files = st.sidebar.checkbox("Copy Files From 'var/mobile/Media'")
    get_sytemlogs = st.sidebar.checkbox("Collect System Log Archive")
    get_Device_data = st.sidebar.button("Collect Data")
    st.sidebar.text("")
    st.sidebar.text("")
    st.sidebar.text("")
    st.sidebar.markdown("---")
    st.sidebar.text("© 2023 North Loop Consulting")
    notes = st.text_area(label=":red[Investigator Notes]",height=250,)
    # Run backup processes
    if get_Device_data == True:
        if len(casenum) == 0:
            with update_msg:
                st.error("Case Number must be provided.")
        else:
            make_report_folders()
            if triage_Data == True:
                read_profile()
                with update_msg:
                    with st.spinner("Creating Triage Report..."):
                        Get_file_list()    
                        make_report(Case_Folder)
                        
            if backup_check == True:
                with update_msg:
                    with st.spinner("Collecting Backup..."):
                        ios_backup(backuplocation)
            if get_sytemlogs == True:
                with update_msg:
                    with st.spinner("Collecting System Logs..."):
                        syslog_collect(lockdown=lock_Handshake,save_log_to=(backuplocation +"/system_logs.logarchive"),size_limit=None, start_time=None, age_limit=None)
           
            show_triage_results()
            update_msg.empty()