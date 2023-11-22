from pyiosbackup import Backup
import plistlib

import sqlite3
import os
from datetime import datetime, timedelta
import pandas as pd
from hashlib import sha1
import time
from reportlab.lib import pagesizes
from reportlab.pdfbase.pdfdoc import PDFText
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Frame, Spacer
from reportlab.platypus import KeepInFrame, HRFlowable
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import LETTER, landscape, portrait, legal
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas 
from reportlab.platypus.flowables import KeepTogether

start = time.process_time()   # for testing


    # Iterate over backup to find all image and video files. 
    # Identify interesting artifacts, get their file id and 
    # pull those files from the backup. 
    # Is there even a need to unpack the whole backup????
    # parse info.plist for report data
    # Safari history/download/autofill?
reportoutputdestination = "D:\\TESTOUTPUT"
fileoutputdestination = reportoutputdestination + "\\Artifacts"
photooutputdestination = reportoutputdestination + '\\Photos'
backup_path = "D:\\MITE_Cases\\TestRun_iPhone 12_Charlie Rubisoff_20231122141240\\Backups & Exports\\00008101-0008199926E9001E"
info_plist_path = f'{backup_path}/Info.plist'
password = "MITE"
if os.path.isdir(reportoutputdestination) == False:
    os.makedirs(reportoutputdestination)
if os.path.isdir(photooutputdestination) == False:
    os.makedirs(photooutputdestination)
if os.path.isdir(fileoutputdestination) == False:
    os.makedirs(fileoutputdestination)

phonetype = ""
devicename = ""
phonenum = ""
imei = ""
serialnum = ""

taxonomy_Dict = {
1605: "body_part",
1736: "child",
1622: "computer",
432: "credit_card",
450: "currency",
492: "document",
554: "firearm",
1664: "handwriting",
759: "keypad",
1668: "laptop",
881: "people",
983: "phone",
1665: "screenshot",
1758: "teen",
1777: "underwear",
1447: "vehicle",
1632: "weapon"
}
target = 'teen'

list_of_paths = []
now = datetime.now()

def parse_info_plist(file_path):
    try:
        with open(file_path, 'rb') as plist_file:
            plist_data = plistlib.load(plist_file)
            global phonetype
            phonetype = (plist_data['Product Type'])
            global devicename
            devicename = (plist_data['Device Name'])
            global imei
            imei = (plist_data['IMEI'])
            global phonenum
            phonenum = (plist_data['Phone Number'])
            global serialnum
            serialnum = (plist_data['Serial Number'])
            
    except Exception as e:
        print(f"Error: {e}")
        return None
parse_info_plist(info_plist_path) 
def make_portrait_report(outputfolder, report_title, sqlqueryresult):
    # Start with raw text reports for large output

    # PDF REPORT STUFF
    pdfReportPages = outputfolder + "/MITE_iOS_Report_" + report_title + "_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".pdf"
    doc = SimpleDocTemplate(pdfReportPages, pagesize=LETTER)

    # Container for the "Flowable" objects
    elements = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Table Normal', fontName='Helvetica', fontSize=8, leading=10,
                              backColor=colors.white, textColor=colors.black, alignment=1))
    styleA = styles["Table Normal"]
    styleN = styles["BodyText"]
    styleH = styles["Heading1"]

    w, t, c = '100%', 2, 'darkgrey'

    # Add title and border
    elements.append(Paragraph("<i><font color='Darkslategray'>Device Type:</font></i>" + phonetype, styleN))
    elements.append(Paragraph("<i><font color='Darkslategray'>Device Name:</font></i>" + devicename, styleN))
    elements.append(Paragraph("<i><font color='Darkslategray'>Phone Number:</font></i>" + phonenum, styleN))
    elements.append(Paragraph("<i><font color='Darkslategray'>Device IMEI:</font></i>" + imei, styleN))
    elements.append(Paragraph("<i><font color='Darkslategray'>Serial Number:</font></i>" + serialnum, styleN))
    elements.append(Paragraph("<i><font color='Darkslategray'>Report Date/Time: </font></i>" + datetime.now().strftime("%m/%d/%Y %H:%M:%S"), styleN))
    elements.append(Paragraph(" ", styleN))
    elements.append(HRFlowable(width=w, thickness=t, color=c, spaceBefore=2, vAlign='MIDDLE', lineCap='square'))    #   Border
    elements.append(Paragraph(" ", styleN))
    # Add title and border
    elements.append(Paragraph("<i><font color='Darkslategray'>{}</font></i>".format(report_title), styleH))
    elements.append(Paragraph(" ", styleN))

    # Create a table and add it to the elements
    table_data = [list(map(str, row)) for row in sqlqueryresult]
    table = Table(table_data)

    # Define the table style
    table_style = [
           ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkslateblue),  # Set text color for the first row
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Adjust vertical alignment as needed
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('WORDWRAP', (0, 1), (-1, -1), True),  # Enable word wrap for all cells except for all cells except the header
            ]

    # Apply the table style
    table.setStyle(table_style)
    elements.append(table)

    # Add border
    elements.append(HRFlowable(width=w, thickness=t, color=c, spaceBefore=2, vAlign='MIDDLE', lineCap='square'))

    # Build the PDF
    doc.build(elements)

def truncate_text(text, max_length):
    return text if len(text) <= max_length else text[:max_length - 3] + '...'

def make_landscape_report(outputfolder, report_title, sqlqueryresult, max_cell_width=60):
    # PDF REPORT STUFF
    pdfReportPages = outputfolder + "/MITE_iOS_Report_" + report_title + "_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".pdf"
    doc = SimpleDocTemplate(pdfReportPages, pagesize=landscape(legal))

    # Container for the "Flowable" objects
    elements = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Table Normal', fontName='Helvetica', fontSize=8, leading=10,
                              backColor=colors.white, textColor=colors.black, alignment=1))
    styleA = styles["Table Normal"]
    styleN = styles["BodyText"]
    styleH = styles["Heading1"]

    w, t, c = '100%', 2, 'darkgrey'

    elements.append(Paragraph("<i><font color='Darkslategray'>Device Type:</font></i>" + phonetype, styleN))
    elements.append(Paragraph("<i><font color='Darkslategray'>Device Name:</font></i>" + devicename, styleN))
    elements.append(Paragraph("<i><font color='Darkslategray'>Phone Number:</font></i>" + phonenum, styleN))
    elements.append(Paragraph("<i><font color='Darkslategray'>Device IMEI:</font></i>" + imei, styleN))
    elements.append(Paragraph("<i><font color='Darkslategray'>Serial Number:</font></i>" + serialnum, styleN))
    elements.append(Paragraph("<i><font color='Darkslategray'>Report Date/Time: </font></i>" + datetime.now().strftime("%m/%d/%Y %H:%M:%S"), styleN))
    elements.append(Paragraph(" ", styleN))
    elements.append(HRFlowable(width=w, thickness=t, color=c, spaceBefore=2, vAlign='MIDDLE', lineCap='square'))    #   Border
    elements.append(Paragraph(" ", styleN))
    # Add title and border
    elements.append(Paragraph("<i><font color='Darkslategray'>{}</font></i>".format(report_title), styleH))
    elements.append(Paragraph(" ", styleN))
   

    # Add date/time
    
    
  

    # Create a table and add it to the elements
    table_data = [[Paragraph(truncate_text(str(cell), max_cell_width), styleN) for cell in row] for row in sqlqueryresult]

    # Create the table
    table = Table(table_data)

    # Define the table style with wordWrap and max width for each cell
    table_style = [
    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkslateblue),  # Set text color for the first row
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Adjust vertical alignment as needed
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('WORDWRAP', (0, 1), (-1, -1), True),  # Enable word wrap for all cells except for all cells except the header
    ]

    # Apply the table style
    table.setStyle(table_style)
    elements.append(table)

    # Add border
    elements.append(HRFlowable(width=w, thickness=t, color=c, spaceBefore=2, vAlign='MIDDLE', lineCap='square'))

    # Build the PDF
    doc.build(elements)


def replace_taxonomy_id_w_descr(df):   # use string id rather than number
    df['Scene Classification'] = df['Scene Classification'].replace(taxonomy_Dict)

# Function to format a float as a percentage
def format_as_percentage(value):
    return f'{value * 100:.0f}'
    # return f'{value * 100:.0f}%' removed to just get integer
# Function to convert mac epoch to time
def mac_absolute_time_to_datetime(mac_time):
    mac_epoch = datetime(2001, 1, 1, 0, 0, 0)
    dt = mac_epoch + timedelta(seconds=mac_time)
    dt = dt.replace(microsecond=0)
    return str(dt) + " UTC"
def photo_taxonomy(photosqlitepath):        # query photo db to get scene descriptions
    sqlite_file = photosqlitepath
    if sqlite_file is None:
        print("The 'photos.sqlite' file was not found in the specified folder or its subfolders.")
        return

    conn = sqlite3.connect(sqlite_file)
    cur = conn.cursor()
   
    # Execute the SQL query
    query = """SELECT 

		   ZSCENECLASSIFICATION.ZSCENEIDENTIFIER as 'Scene Classification',
           ZSCENECLASSIFICATION.ZCONFIDENCE as 'Confidence',
           ZASSET.ZDIRECTORY as 'Path',
           ZASSET.ZFILENAME as 'Filename',
           ZASSET.ZDATECREATED as 'Date Created (UTC)',
           ZASSET.ZADDEDDATE as 'Date Added'
    FROM ZASSET
    INNER JOIN ZADDITIONALASSETATTRIBUTES ON ZADDITIONALASSETATTRIBUTES.ZASSET = ZASSET.Z_PK
    INNER JOIN ZSCENECLASSIFICATION ON ZSCENECLASSIFICATION.ZASSETATTRIBUTES = ZADDITIONALASSETATTRIBUTES.Z_PK
    """

    df = pd.read_sql_query(query, conn)
 
    # Reference taxonomy dictionary and replace numtag for word
    replace_taxonomy_id_w_descr(df=df)
    # Convert confidence to a percentile
    df['Confidence'] = df["Confidence"].apply(format_as_percentage)
    # Convert epoch to date time
    df["Date Created (UTC)"] = df["Date Created (UTC)"].apply(mac_absolute_time_to_datetime)
    df["Date Added"] = df["Date Added"].apply(mac_absolute_time_to_datetime)
    # Export to csv file
   
    conn.close()
    return(df)

def sqlite_run_SMS(SMSdbPath):
    connection = sqlite3.connect(SMSdbPath)
    cursor = connection.cursor()
    smsQuery = """select 
                case when message."date" != 0 then datetime((message."date" + 978307200000000000) / 1000000000, 'unixepoch') end as 'Message Date (UTC)', 
                handle.id as "Contact",
                handle.service as "Message Service",
                
                case message.is_from_me
                    when 1 then message.text
                    end as 'Sent',
                case message.is_from_me
                    when not 1 then message.text
                    end as 'Received',
                attachment.transfer_name as 'Attachment Name',
				case attachment.is_outgoing 
                    when 0 then 'Incoming Attachment'
                    when 1 then 'Outgoing Attachment'
                    end as 'Attachment State'
   
                from message
                left join handle on message.handle_id = handle.ROWID or message.other_handle = handle.ROWID
                join chat_message_join on chat_message_join.message_id = message.ROWID
                left join message_attachment_join on message.ROWID = message_attachment_join.message_id --A message can have multiple attachments 
                left join attachment on attachment.ROWID = message_attachment_join.attachment_id
                join chat on chat_message_join.chat_id = chat.ROWID

                order by 'Message Date (UTC)' desc"""
    cursor.execute(smsQuery)
    results = cursor.fetchall()
    connection.close()
    return results

def sqlite_run_accounts3(accounts3path):
    connection = sqlite3.connect(accounts3path)
    cursor = connection.cursor()
    
    # Your original query
    act3query = """
    SELECT 
        datetime('2001-01-01', ZACCOUNT.ZDATE || ' seconds') AS "Account Date (UTC)",
        ZACCOUNT.ZUSERNAME AS "Username", 
        ZACCOUNT.ZACCOUNTDESCRIPTION AS "Description"
    FROM ZACCOUNT
    WHERE ZACCOUNT.ZDATE IS NOT NULL
        AND ZACCOUNT.ZUSERNAME IS NOT NULL
        AND ZACCOUNT.ZACCOUNTDESCRIPTION IS NOT NULL;
    """

    # Execute the query
    cursor.execute(act3query)
    results = cursor.fetchall()

    # Fetch column headers using description
    column_headers = [description[0] for description in cursor.description]

    # Close the connection
    connection.close()

    # Combine column headers with data
    results_with_headers = [column_headers] + results

    return results_with_headers

def sqlite_run_addressbook(addressbookpath):
    connection = sqlite3.connect(addressbookpath)
    cursor = connection.cursor()
    addressbookquery = """Select 
                        abperson.Last as 'Last',
                        abperson.First as 'First',
                        (select 
                            value from ABMultiValue where property = 3 and record_id = ABPerson.ROWID and 
                            label = (select ROWID from ABMultiValueLabel where value = '_$!<Main>!$_')) as 'Main',
                        (select 
                            value from ABMultiValue where property = 3 and record_id = ABPerson.ROWID and 
                            label = (select ROWID from ABMultiValueLabel where value = 'iPhone')) as 'iPhone',		
                        (select 
                            value from ABMultiValue where property = 3 and record_id = ABPerson.ROWID and 
                            label = (select ROWID from ABMultiValueLabel where value = '_$!<Mobile>!$_')) as 'Mobile',
                        (select 
                            value from ABMultiValue where property = 3 and record_id = ABPerson.ROWID and 
                            label = (select ROWID from ABMultiValueLabel where value = '_$!<Home>!$_')) as 'Home',
                        (select 
                            value from ABMultiValue where property = 3 and record_id = ABPerson.ROWID and 
                            label = (select ROWID from ABMultiValueLabel where value = '_$!<Work>!$_')) as 'Work',
                        (select 
                            value from ABMultiValue where property = 4 and record_id = ABPerson.ROWID and 
                            label is null) as 'Email'

                        --datetime('2001-01-01', abperson.CreationDate || ' seconds') as 'CreationDate (UTC)'
                    
                        from abperson
                            join ABStore on abperson.StoreID = ABStore.ROWID
                            join ABAccount on ABStore.AccountID = ABAccount.ROWID
                            order by abperson.Last asc;"""
    cursor.execute(addressbookquery)
    results = cursor.fetchall()
    column_headers = [description[0] for description in cursor.description]

    # Close the connection
    connection.close()

    # Combine column headers with data
    results_with_headers = [column_headers] + results
 
    return results_with_headers

def sqlite_run_datausage(datausagepath):
    connection = sqlite3.connect(datausagepath)
    cursor = connection.cursor()
    datausequery = """SELECT 
                    datetime('2001-01-01', ZLIVEUSAGE.ZTIMESTAMP || ' seconds') as 'Date (UTC)', 
                    ZPROCESS.ZBUNDLENAME as 'Application Bundle', 
					ZLIVEUSAGE.ZWIFIIN as 'WiFi In', 
                    ZLIVEUSAGE.ZWIFIOUT as 'WiFi Out', 
					ZLIVEUSAGE.ZWWANIN as 'WWAN In', 
					ZLIVEUSAGE.ZWWANOUT as 'WWAN Out'
                    
                    FROM ZLIVEUSAGE
                    LEFT JOIN ZPROCESS ON ZPROCESS.Z_PK = ZLIVEUSAGE.ZHASPROCESS
                    ORDER BY datetime('2001-01-01', ZLIVEUSAGE.ZTIMESTAMP || ' seconds') ASC;"""
    cursor.execute(datausequery)
    results = cursor.fetchall()
    column_headers = [description[0] for description in cursor.description]

    # Close the connection
    connection.close()

    # Combine column headers with data
    results_with_headers = [column_headers] + results
 
    return results_with_headers

def sqlite_run_callhistory(callhistorypath):
    connection = sqlite3.connect(callhistorypath)
    cursor = connection.cursor()
    datausequery = """SELECT 
                    datetime('2001-01-01', zdate || ' seconds') as 'Date (UTC)',
                    time(ZDURATION,'unixepoch') as 'Duration',
                    ZADDRESS as 'Other Party',
                    CASE ZORIGINATED 
                        WHEN 0 THEN 'Incoming'
                        WHEN 1 THEN 'Outgoing'
                    END as 'Call Direction',
                    -- CASE ZANSWERED
                    --    WHEN 0 THEN 'No'
                    --    WHEN 1 THEN 'Yes'
                    -- END as 'Answered',
                    CASE ZCALLTYPE 
                        WHEN 1 THEN 'Standard Call'
                        WHEN 8 THEN 'Facetime Video Call'
                        WHEN 16 THEN 'Facetime Audio Call'
                        ELSE CAST(ZCALLTYPE AS TEXT)  -- Assuming ZCALLTYPE is a numeric type
                    END as 'CallType' 
                FROM zcallrecord
                ORDER BY datetime('2001-01-01', zdate || ' seconds') ASC;"""
    cursor.execute(datausequery)
    results = cursor.fetchall()
    column_headers = [description[0] for description in cursor.description]

    # Close the connection
    connection.close()

    # Combine column headers with data
    results_with_headers = [column_headers] + results

    return results_with_headers

def sqlite_run_safarihistory(safarihistorypath):
    connection = sqlite3.connect(safarihistorypath)
    cursor = connection.cursor()
    datausequery = """SELECT 
                    datetime('2001-01-01', history_visits.visit_time || ' seconds') as 'Date (UTC)',
                    history_visits.title as 'Page Title',
                    history_items.url as 'URL',
                    case history_visits.load_successful
                        when 0 then 'No'
                        when 1 then 'Yes'
                        end "Page Loaded",
                    history_items.visit_count as 'Total Visit Count'
                    FROM history_visits LEFT JOIN history_items on history_items.id = history_visits.history_item"""
    cursor.execute(datausequery)
    results = cursor.fetchall()
    column_headers = [description[0] for description in cursor.description]

    # Close the connection
    connection.close()

    # Combine column headers with data
    results_with_headers = [column_headers] + results

    return results_with_headers
def sqlite_run_TCC(TCCpath):
    connection = sqlite3.connect(TCCpath)
    cursor = connection.cursor()
    datausequery = """SELECT
                    access.service as 'Device Permission',                       
                    ACCESS.client as 'Application Bundle'
                    FROM access """
    cursor.execute(datausequery)
    results = cursor.fetchall()
    column_headers = [description[0] for description in cursor.description]

    # Close the connection
    connection.close()

    # Combine column headers with data
    results_with_headers = [column_headers] + results

    return results_with_headers

def retrieve_files_from_backup(backup_path, filedestination, password):
    # File ids in manifest.db for artifacts
    # photos_Sqlite = '12b144c0bd44f2b3dffd9186d3f9c05b917cee25'
    # datausage_Sqlite = "0d609c54856a9bb2d56729df1d68f2958a88426b"
    # X addressbook_sqlitedb = "31bb7ba8914766d4ba40d6dfb6113c8b614be442"
    # X accounts3_sqlite = "943624fd13e27b800cc6d9ce1100c22356ee365c"
    # voicemail_db = "992df473bbb9e132f4b3b6e4d33f72171e97bc7a"  # can we do transcripts?
    # X sms_db = "3d0d7e5fb2ce288813306e4d4636395e047a3d28"  # giant csv? pdf takes forever
    # TCC_db = "64d0019cb3d46bfc8cce545a8ba54b93e7ea9347"  # limit to access to camera, microphone, photos, 
    # callhistory_sqlite = "5a4935c78a5255723f707230a451d79c540d2741"
    # safari_sqlite = "e74113c185fd8297e140cfcf9c99436c5cc06b57"  ?

    list_of_fileIDs = ['12b144c0bd44f2b3dffd9186d3f9c05b917cee25', "0d609c54856a9bb2d56729df1d68f2958a88426b", "1a0e7afc19d307da602ccdcece51af33afe92c53" ,
                    "31bb7ba8914766d4ba40d6dfb6113c8b614be442", "943624fd13e27b800cc6d9ce1100c22356ee365c",  "3d0d7e5fb2ce288813306e4d4636395e047a3d28", 
                    "64d0019cb3d46bfc8cce545a8ba54b93e7ea9347", "5a4935c78a5255723f707230a451d79c540d2741"]

    backup = Backup.from_path(backup_path=backup_path, password=password)
    
    for ID in list_of_fileIDs:
        try:
            backupd_plist = backup.extract_file_id(ID,path=filedestination)
        except Exception as e:
            if isinstance(e, Backup) and 'ErrorCode' in e.args and e.args['ErrorCode'] == 207:
                print("Invalid password error. Please check your password.")
                # Additional handling for invalid password can go here
            else:
                # Handle other types of exceptions
                print(f"An unexpected exception occurred: {e}")

def calculate_itunes_photofile_name(filepathinbackup):
    builtpath = ('CameraRollDomain-Media/' + filepathinbackup)
    builtpath = builtpath.encode(encoding='UTF-8', errors='strict')
    filehash = sha1(builtpath).hexdigest()
    return str(filehash)

def retrieve_photos_from_backup(backup_path, filedestination, password, list_of_fileIDs):
    
    backup = Backup.from_path(backup_path=backup_path, password=password)
    # try:
    #     testout = backup.unback("D:\\TESTOUTPUT")
    # except OSError:
    #     print("OS error on unpacking a folder")
    for ID in list_of_fileIDs:
        try:
            backupd_plist = backup.extract_file_id(ID,path=filedestination)
        except Exception as e:
            if isinstance(e, Backup) and 'ErrorCode' in e.args and e.args['ErrorCode'] == 207:
                print("Invalid password error. Please check your password.")
                # Additional handling for invalid password can go here
            else:
                # Handle other types of exceptions
                print(f"An unexpected exception occurred: {e}")


retrieve_files_from_backup(backup_path=backup_path, filedestination=fileoutputdestination, password=password)

recovered_files = os.listdir(fileoutputdestination)

for artifact in recovered_files:
    # print(artifact)
    if "Accounts3" in artifact:
        accountdata = os.path.join(fileoutputdestination + '\\' + artifact)
        # print(accountdata)
        accourntquery = sqlite_run_accounts3(accountdata)
        # print(accourntquery)
        make_portrait_report(outputfolder=reportoutputdestination, report_title="Accounts",sqlqueryresult=accourntquery)
    
    if "AddressBook.sqlitedb" in artifact:
        accountdata = os.path.join(fileoutputdestination + '\\' + artifact)
        addressquery = sqlite_run_addressbook(accountdata) 
        
        make_landscape_report(outputfolder=reportoutputdestination, report_title="Address Book",sqlqueryresult=addressquery)
    
    if 'CallHistory.storedata' in artifact:
        accountdata = os.path.join(fileoutputdestination + '\\' + artifact)
        callquery = sqlite_run_callhistory(accountdata) 
        # print(callquery)
        make_portrait_report(outputfolder=reportoutputdestination, report_title="Call History",sqlqueryresult=callquery)
    if 'DataUsage.sqlite' in artifact:
        accountdata = os.path.join(fileoutputdestination + '\\' + artifact)
        datausequery = sqlite_run_datausage(accountdata) 
        # print(datausequery)
        make_landscape_report(outputfolder=reportoutputdestination, report_title="Data Usage",sqlqueryresult=datausequery)
    if "History.db" in artifact:
        accountdata = os.path.join(fileoutputdestination + '\\' + artifact)
        safariquery = sqlite_run_safarihistory(accountdata) 
        # print(safariquery)   
        make_landscape_report(outputfolder=reportoutputdestination, report_title="Safari History",sqlqueryresult=safariquery)
    if "sms.db" in artifact:
        accountdata = os.path.join(fileoutputdestination + '\\' + artifact)
        smsquery = sqlite_run_SMS(accountdata) 
        make_landscape_report(outputfolder=reportoutputdestination, report_title="Messages",sqlqueryresult=smsquery,max_cell_width=25)


        # print(smsquery)
    if "TCC.db" in artifact:
        accountdata = os.path.join(fileoutputdestination + '\\' + artifact)
        tccquery = sqlite_run_TCC(accountdata) 
        # print(tccquery)
        make_portrait_report(outputfolder=reportoutputdestination, report_title="App Permissions",sqlqueryresult=tccquery)
    if "Photos.sqlite" in artifact:
        
        accountdata = os.path.join(fileoutputdestination + '\\' + artifact)
        taxonomyquery = photo_taxonomy(accountdata)
        taxonomyquery['Confidence'] = pd.to_numeric(taxonomyquery['Confidence'], errors='coerce')
        # finds target search term and confidence level increased to avoid false positives
        filtered_df = taxonomyquery[(taxonomyquery['Scene Classification'] == target) & (taxonomyquery['Confidence'] > 25)] 
        print(filtered_df) 
        #gets the image file path
        pathdf = (filtered_df['Path'] + '/' + filtered_df['Filename'])
        for thing in pathdf:
            #converts the path to sha1 hash in backup
            fileid = calculate_itunes_photofile_name(thing)
            list_of_paths.append(fileid)

        retrieve_photos_from_backup(backup_path=backup_path, filedestination=photooutputdestination, password=password,list_of_fileIDs=list_of_paths)

end = time.process_time() - start
print(end)
