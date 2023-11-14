from pyiosbackup import Backup
import plistlib
import sqlite3
import os


    # Iterate over backup to find all image and video files. 
    # Identify interesting artifacts, get their file id and 
    # pull those files from the backup. 
    # Is there even a need to unpack the whole backup????

    # Safari history/download/autofill?

fileoutputdestination = "D:\\TESTOUTPUT"

backup_path = "D:\\MITE_Cases\\00008120-0016085A3A00C01E"
password = "MITE"

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
    act3query = """SELECT 
    datetime('2001-01-01', ZACCOUNT.ZDATE || ' seconds') AS "Account Date (UTC)",
    ZACCOUNT.ZUSERNAME AS "Username", 
    ZACCOUNT.ZACCOUNTDESCRIPTION AS "Description"
    FROM ZACCOUNT
    WHERE ZACCOUNT.ZDATE IS NOT NULL
    AND ZACCOUNT.ZUSERNAME IS NOT NULL
    AND ZACCOUNT.ZACCOUNTDESCRIPTION IS NOT NULL;"""

    cursor.execute(act3query)
    results = cursor.fetchall()
    connection.close()
    return results

def sqlite_run_addressbook(addressbookpath):
    connection = sqlite3.connect(addressbookpath)
    cursor = connection.cursor()
    addressbookquery = """Select 
                        abperson.Last,
                        abperson.First,
                        abperson.Organization,
                        (select 
                            value from ABMultiValue where property = 3 and record_id = ABPerson.ROWID and 
                            label = (select ROWID from ABMultiValueLabel where value = '_$!<Main>!$_')) as 'Main',
                        (select 
                            value from ABMultiValue where property = 3 and record_id = ABPerson.ROWID and 
                            label = (select ROWID from ABMultiValueLabel where value = 'iPhone')) as 'iPhone',	
                        (select 
                            value from ABMultiValue where property = 3 and record_id = ABPerson.ROWID and 
                            label = (select ROWID from ABMultiValueLabel where value = '_$!<Other>!$_')) as 'Other',	
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
                            label is null) as 'Email',
                        (select 
                            value from ABMultiValueEntry where parent_id in (select ROWID from ABMultiValue 
                            where record_id = ABPerson.ROWID) and key = (select ROWID from ABMultiValueEntryKey 
                            where lower(value) = 'street')) as 'Street',
                        (select 
                            value from ABMultiValueEntry where parent_id in (select ROWID from ABMultiValue 
                            where record_id = ABPerson.ROWID) and key = (select ROWID from ABMultiValueEntryKey 
                            where lower(value) = 'city')) as 'City',
                        datetime('2001-01-01', abperson.CreationDate || ' seconds') as 'CreationDate (UTC)'
                    
                        from abperson
                            join ABStore on abperson.StoreID = ABStore.ROWID
                            join ABAccount on ABStore.AccountID = ABAccount.ROWID"""
    cursor.execute(addressbookquery)
    results = cursor.fetchall()
    connection.close()
    return results

def sqlite_run_datausage(datausagepath):
    connection = sqlite3.connect(datausagepath)
    cursor = connection.cursor()
    datausequery = """SELECT 
                    ZLIVEUSAGE.ZTIMESTAMP, ZLIVEUSAGE.ZWIFIIN, 
                    ZLIVEUSAGE.ZWIFIOUT, ZLIVEUSAGE.ZWWANIN, ZLIVEUSAGE.ZWWANOUT, 
                    ZPROCESS.ZBUNDLENAME, ZPROCESS.ZPROCNAME 
                    FROM ZLIVEUSAGE
                    LEFT JOIN ZPROCESS ON ZPROCESS.Z_PK = ZLIVEUSAGE.ZHASPROCESS"""
    cursor.execute(datausequery)
    results = cursor.fetchall()
    connection.close()
    return results

def retrieve_files_from_backup(backup_path, filedestination, password):
    # File ids in manifest.db for artifacts
    # photos_Sqlite = '12b144c0bd44f2b3dffd9186d3f9c05b917cee25'
    # datausage_Sqlite = "0d609c54856a9bb2d56729df1d68f2958a88426b"
    # X addressbook_sqlitedb = "31bb7ba8914766d4ba40d6dfb6113c8b614be442"
    # X accounts3_sqlite = "943624fd13e27b800cc6d9ce1100c22356ee365c"
    # voicemail_db = "992df473bbb9e132f4b3b6e4d33f72171e97bc7a"  # can we do transcripts?
    # X sms_db = "3d0d7e5fb2ce288813306e4d4636395e047a3d28"  # giant csv? need to convert times
    # TCC_db = "64d0019cb3d46bfc8cce545a8ba54b93e7ea9347"  # limit to access to camera, microphone, photos, 
    # callhistory_sqlite = "5a4935c78a5255723f707230a451d79c540d2741"
    # safari_sqlite = "e74113c185fd8297e140cfcf9c99436c5cc06b57"  ?

    list_of_fileIDs = ['12b144c0bd44f2b3dffd9186d3f9c05b917cee25', "0d609c54856a9bb2d56729df1d68f2958a88426b", "1a0e7afc19d307da602ccdcece51af33afe92c53" ,
                    "31bb7ba8914766d4ba40d6dfb6113c8b614be442", "943624fd13e27b800cc6d9ce1100c22356ee365c", "992df473bbb9e132f4b3b6e4d33f72171e97bc7a", 
                    "3d0d7e5fb2ce288813306e4d4636395e047a3d28", "64d0019cb3d46bfc8cce545a8ba54b93e7ea9347", "5a4935c78a5255723f707230a451d79c540d2741"]

    backup = Backup.from_path(backup_path=backup_path, password=password)
    # try:
    #     testout = backup.unback("D:\\TESTOUTPUT")
    # except OSError:
    #     print("OS error on unpacking a folder")
    for ID in list_of_fileIDs:
        try:
            backupd_plist = backup.extract_file_id(ID,path=fileoutputdestination)
        except Exception as e:
            if isinstance(e, Backup) and 'ErrorCode' in e.args and e.args['ErrorCode'] == 207:
                print("Invalid password error. Please check your password.")
                # Additional handling for invalid password can go here
            else:
                # Handle other types of exceptions
                print(f"An unexpected exception occurred: {e}")



if os.path.isdir(fileoutputdestination) == False:
    os.makedirs(fileoutputdestination)

retrieve_files_from_backup(backup_path=backup_path, filedestination=fileoutputdestination, password=password)

recovered_files = os.listdir(fileoutputdestination)

for artifact in recovered_files:
    print(artifact)
    if "Accounts3" in artifact:
        accountdata = os.path.join(fileoutputdestination + '\\' + artifact)
        # print(accountdata)
        accourntquery = sqlite_run_accounts3(accountdata)
        
    if "sms.db" in artifact:
        accountdata = os.path.join(fileoutputdestination + '\\' + artifact)
        smsquery = sqlite_run_SMS(accountdata) 
        # print(smsquery)
    if "AddressBook.sqlitedb" in artifact:
        accountdata = os.path.join(fileoutputdestination + '\\' + artifact)
        print(accountdata)
        addressquery = sqlite_run_addressbook(accountdata) 
        print(addressquery)