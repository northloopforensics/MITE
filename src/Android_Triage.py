# ###### To Do ######
#     More prominent button color and or size
#     see historical work xml or sqlite
#     parse creation dates install dates images and apps
#     stress test thumbnail presentation
#     disable triage button while running 
#       phone number ---- research service calls, this is os version dependant
#       warninng for file alteration


import streamlit as st
from tokenize import group
import os
import subprocess
from subprocess import PIPE, run, Popen, CREATE_NO_WINDOW, check_output
import time
import datetime
import sys
import pandas as pd
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
# from android_backup import AndroidBackup, CompressionType, EncryptionType
import MITE_ADB
import imghdr
import json
# from android_backup import AndroidBackup, CompressionType, EncryptionType
import tarfile
from abc import ABC, abstractmethod
from typing import BinaryIO, Callable, Tuple
from zlib import decompressobj
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

#   Easy mechanism for temporary use. 
now = datetime.datetime.now()
# expire = datetime.datetime(2022, 7, 29)
# if now > expire:
#     print("The tool expired - see line 44")
#     sys.exit()


################    GET PLATFORM    #################
#   Determines if Windows or MacOS is being used to appropriately open ADB
if sys.platform == "darwin":                                   
    adb = "./Support_Files/adb"
if sys.platform == "win32" or sys.platform == "win64":
    adb = ".\\Support_Files\\adb.exe"

#################   GLOBAL VARIABLES    ################

video_files = ['.mp4', '.m4v', '.avi', '.3gp', '.mov', '.flv', '.mkv', '.webm', '.m4v', '.webm', '.mpeg', '.mpe',
              '.ogg', '.m4p', '.mp2', '.swf', '.qt','.MP4', '.M4V', '.AVI', '.3GP', '.MOV', '.FLV', '.MKV', '.WEBM', 
              '.M4V', '.WEBM', '.MPEG', '.MPE','.OGG', '.M4P', '.MP2', '.SWF', '.QT']
picture_files = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', 'webp','.JPG', '.PNG', '.JPEG', '.GIF', '.BMP', '.WEBP']
Master_file_list = []               #   Contains list of queried files and directories
Master_application_list = []        #   Contains list of installed packages/apps
Master_hash_list = []               #   Hashes and file name in list
Master_user_list = []               #   List of device users
comparison_filenames = []           #   filenames from profile
comparison_hashes = []              #   hashes from profile
comparison_keywords = []            #   keywords from profile
match_filenames =[]                 #   Match results between device and profile
match_hashes = []
match_keywords = []
Upper_file_list = []                #   File listing in all upper case for non-case sensitive comparison purposes
profile_list = ["None Selected"]
casenum = ""
profile = ""
dat = now.strftime("%Y/%m/%d %H-%M-%S")
stamp = now.strftime("%Y%m%d%H%M%S")
build_version = ""
sim_Carrier = ""
home_Carrier = ""
wifi_mac = ""
phone_number = ""
imei = []
imsi = []
iccid = []
inv_name = ""
agency_name = ""
internal_info = ""
external_info = ""
backup_file = ""
status_message = st.empty()

screenshot_num = 1
backend = default_backend()
dev_Manufacturer = ""
dev_Model = ""
now = datetime.datetime.now()
Backup_status = st.empty() 

#######    Backup Global Variables            ########

big_img_list = []
big_vid_list = []
large_imgs = []     #larger than 800kb
med_img = []        #50k to 800mb
small_img = []      #smaller than 50k
large_vids = []     #larger than 1gb
med_vids = []       #10mb to 1gb
small_vids = []     #smaller than 10mb
unpack_to_dis = " "



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

#This removes Streamlit default settings icons
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

shrink_sidebar_top = st.markdown("""
  <style>
    .css-1helkxk.e1fqkh3o9 {
      margin-top: -50px;
    }
  </style>
""", unsafe_allow_html=True)
#This removes the arrow icon from the st.metric used to show device storage stats
st.write(
    """
    <style>
    [data-testid="stMetricDelta"] svg {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

#######      Backup Classes and Functions       ########

def get_password() -> bytes:
    """
    Get user password.

    Returns:
        UTF-8 encoded password.
    """

    pwd = "MITE"
    print(pwd.encode())

    return pwd.encode()

class AbstractWriter(ABC):
    """
    ABC for chaining output modifying funtions together.
    """

    @abstractmethod
    def write(self, buf: bytes) -> None:
        """
        Write buf to stream

        Args:
            buf: data to write
        """

    @abstractmethod
    def flush(self) -> None:
        """
        Finish output. Must not call write afterwards.
        """

class StreamWriter(AbstractWriter):
    """
    Write to python stream
    """

    def __init__(self, stream: BinaryIO) -> None:
        """
        Args:
            stream: Target stream
        """

        self.stream = stream

    def write(self, buf: bytes) -> None:
        """
        Write buf to stream

        Args:
            buf: data to write
        """

        self.stream.write(buf)

    def flush(self) -> None:
        """
        Finish output. Must not call write afterwards.
        """

        self.stream.flush()

class ZlibDecompressor(AbstractWriter):
    """
    Decompress zlib
    """

    def __init__(self, stream: AbstractWriter) -> None:
        """
        Args:
            stream: Target stream
        """

        self.stream = stream
        self.decompressor = decompressobj()

    def write(self, buf: bytes) -> None:
        """
        Write buf to stream

        Args:
            buf: data to write
        """

        self.stream.write(self.decompressor.decompress(buf))

    def flush(self) -> None:
        """
        Finish output. Must not call write afterwards.
        """

        self.stream.write(self.decompressor.flush())
        self.stream.flush()

class PKCS7Unpadder(AbstractWriter):
    """
    Unpad PKCS#7
    """

    def __init__(self, stream: AbstractWriter) -> None:
        """
        Args:
            stream: Target stream
        """

        self.stream = stream
        self.unpadder = padding.PKCS7(128).unpadder()

    def write(self, buf: bytes) -> None:
        """
        Write buf to stream

        Args:
            buf: data to write
        """

        self.stream.write(self.unpadder.update(buf))

    def flush(self) -> None:
        """
        Finish output. Must not call write afterwards.
        """
        
        self.stream.write(self.unpadder.finalize())
      
        self.stream.flush()

class Aes256Decryptor(AbstractWriter):
    """
    Decrypt AES-CBC stream
    """

    def __init__(self, stream: AbstractWriter, key: bytes, iv: bytes) -> None:
        """
        Args:
            stream: Target stream
            key: AES key (16, 24 or 32 bytes)
            iv: IV for CBC (16 bytes)
        """

        self.stream = PKCS7Unpadder(stream)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
        self.decryptor = cipher.decryptor()

    def write(self, buf: bytes) -> None:
        """
        Write buf to stream

        Args:
            buf: data to write
        """

        self.stream.write(self.decryptor.update(buf))

    def flush(self) -> None:
        """
        Finish output. Must not call write afterwards.
        """

        self.stream.write(self.decryptor.finalize())
        self.stream.flush()

def utf8_encode(buf: bytes) -> bytes:
    """
    Stupid java bytes-to-string-to-bytes encoding.

    Args:
        buf: data to encode

    Returns:
        utf8 encoded data
    """

    return "".join(chr(i if i < 0x80 else i + 0xFF00) for i in buf).encode()

def derive_aes_256_key(
    pwd: bytes, pwd_salt: bytes, mk_ck_salt: bytes, rounds: int, uk_iv: bytes, mk_blob: bytes,
) -> Tuple[bytes, bytes]:
    """
    Derive key and IV from password.

    Args:
        pwd: User's password, utf8 encoded
        pwd_salt: PBKDF2 salt for user password
        mk_ck_salt: PBKDF2 salt for master key
        rounds: Number of PBKDF2 rounds
        uk_iv: CBC IV for user key
        mk_blob: Encrypted master key blob

    Returns:
        Master key and IV
    """

    # Derive user key
    uk = PBKDF2HMAC(
        algorithm=hashes.SHA1(), length=32, salt=pwd_salt, iterations=rounds, backend=backend,
    ).derive(pwd)

    # Decrypt master key blob
    cipher = Cipher(algorithms.AES(uk), modes.CBC(uk_iv), backend=backend)
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(128).unpadder()
    blob = bytearray(unpadder.update(decryptor.update(mk_blob) + decryptor.finalize()) + unpadder.finalize())

    # Split values from master key blob
    mk_iv_len = blob[0]
    mk_iv = blob[1 : mk_iv_len + 1]
    del blob[: mk_iv_len + 1]

    mk_len = blob[0]
    mk = blob[1 : mk_len + 1]
    del blob[: mk_len + 1]

    mk_ck_len = blob[0]
    if len(blob) - 1 != mk_ck_len:
        raise ValueError
    mk_ck_0 = bytes(blob[1:])

    # Calculate and compare checksum
    mk_ck_1 = PBKDF2HMAC(
        algorithm=hashes.SHA1(), length=mk_ck_len, salt=mk_ck_salt, iterations=rounds, backend=backend,
    ).derive(utf8_encode(mk))

    if mk_ck_0 != mk_ck_1:
        raise ValueError("Bad password")

    return mk, mk_iv

def read_hex(stream: BinaryIO) -> bytes:
    """
    Read HEX line from stream and decode as bytes

    Args:
        stream: stream to read from

    Returns: decoded bytes
    """
    return bytes.fromhex(stream.readline().decode())

def decrypt_android_backup(in_stream: BinaryIO, out_stream: BinaryIO, pw_callback: Callable[[], bytes]) -> None:
    """
    Decrypt an android backup.

    Args:
        in_stream: Input stream
        out_stream: Output stream
        pw_callback: Callback function to retrieve user password
    """

    writer: AbstractWriter = StreamWriter(out_stream)

    if in_stream.readline() != b"ANDROID BACKUP\n":
        raise ValueError("Bad magic")
    version = int(in_stream.readline())
    compressed = int(in_stream.readline())
    encr_algo = in_stream.readline().strip().decode()

    if compressed:
        writer = ZlibDecompressor(writer)

    if encr_algo == "none":
        pass
    elif encr_algo == "AES-256":
        pwd = pw_callback()
        pwd_salt = read_hex(in_stream)
        mk_ck_salt = read_hex(in_stream)
        rounds = int(in_stream.readline())
        uk_iv = read_hex(in_stream)
        mk_blob = read_hex(in_stream)

        try:
            key, iv = derive_aes_256_key(pwd, pwd_salt, mk_ck_salt, rounds, uk_iv, mk_blob)
        except Exception as ex:
            raise ValueError("Bad password!") from ex

        writer = Aes256Decryptor(writer, key, iv)
    else:
        raise ValueError(f"Unknown encryption algorithm: {encr_algo}")

    while True:
        buf = in_stream.read(4096)
        if not buf:
            break
        writer.write(buf)
    writer.flush()

def make_backup_folder(case_folder):
    global BACKUP_Folder
    BACKUP_Folder = (case_folder + "/" + dev_Model +"-BACKUP-" + now.strftime("%Y%m%d%H%M%S")) 
    os.makedirs(BACKUP_Folder)
    return BACKUP_Folder

def make_backup(destination_folder, caseNumber):
    
    with Backup_status:
        st.warning("Keep device unlocked and the screen active! If necessary, hit 'Back up my data'. \nDefault password is 'MITE'")
    os.makedirs(destination_folder + "/Mite_Backup")
    global back_folder
    back_folder = destination_folder + "/Mite_Backup"
    # backingup = MITE_ADB.ADB_backup(back_folder, casenum, dev_Name)
    backup_file = back_folder + "/" + caseNumber + "_backup.ab"       #   name of backup
    # backup_folder = back_folder + "/" + casenum + "_" + dev_Name                    #   output directory for unpacked backup
    # backed = Popen([adb, "backup", "-apk", "-all", "-shared", "-f", backup_file])
    backed = Popen([adb, "backup", "-apk", "-all", "-f", backup_file], creationflags=CREATE_NO_WINDOW)
    time.sleep(2)
    touchy = Popen([adb, "shell", "input", "tap 220 820"], creationflags=CREATE_NO_WINDOW)
    time.sleep(2)
    password = Popen([adb, "shell", "input", "text 'MITE'"], creationflags=CREATE_NO_WINDOW)
    time.sleep(2)
    touch_2_backup = Popen([adb, "shell", "input", "tap 820 1440"], creationflags=CREATE_NO_WINDOW)     # keyboard on screen touch location (this is empty space when no keyboard present. use it first.)
    touch_3_backup = Popen([adb, "shell", "input", "tap 570 1415"], creationflags=CREATE_NO_WINDOW)     # keyboard not on screen touch location
        
    with Backup_status:
        st.info("Backup is starting")                   
    backsize = os.path.getsize(backup_file)
    time.sleep(5)
    backsize2 = os.path.getsize(backup_file)

    if backsize == backsize2:
        st.success("PRESS BACKUP MY DEVICE")
        time.sleep(3)
    
    if backsize2 != backsize:
        while backsize2 != backsize:
            backsize = os.path.getsize(backup_file)
            
            time.sleep(2)
            backsize2 = os.path.getsize(backup_file)
            backgigs = backsize2/1024/1024          # Convert from bytes to GB
            backgigs = round(backgigs)
            # backgig = format(int(backgigs),'.2f')       # limits to two decimal places
            backup_size_update = (str(backgigs) + " MB")
            with Backup_status:
                st.info("ADB Backup in Process - Size is: " + backup_size_update)
        with Backup_status:
            st.empty()
    return backup_file

def android_screenshot():
    if len(casenum) != 0:
        try:
            os.makedirs(report_root + "/MITE_Cases/" + casenum + "/Screenshots")
        except FileExistsError:
            pass
         # ADB command to capture the screenshot
        adb_command = [adb, "exec-out", "screencap", "-p"]

        # Run the ADB command and capture the screenshot data
        process = Popen(adb_command, stdout=PIPE,creationflags=CREATE_NO_WINDOW)
        screenshot_data, _ = process.communicate()

        # Check if the ADB command executed successfully
        if process.returncode == 0:
            # Save the screenshot data to a file on your computer
            with open(report_root + "/MITE_Cases/" + casenum + "/Screenshots/Screenshot_" +stamp +".png", "wb") as file:
                file.write(screenshot_data)
            print("Screenshot saved successfully.")
        else:
            print("Failed to capture the screenshot.")
        with status_message:
            st.info(report_root + "/MITE_Cases/" + casenum + "/Screenshots/Screenshot_" +stamp +".png created and added to case folder.")
    else:
        try:
            os.makedirs(report_root + "/MITE_Cases/Screenshots/")
        except FileExistsError:
            pass

        # ADB command to capture the screenshot
        adb_command = [adb, "exec-out", "screencap", "-p"]

        # Run the ADB command and capture the screenshot data
        process = Popen(adb_command, stdout=PIPE,creationflags=CREATE_NO_WINDOW)
        screenshot_data, _ = process.communicate()

        # Check if the ADB command executed successfully
        if process.returncode == 0:
            # Save the screenshot data to a file on your computer
            with open(report_root + "/MITE_Cases/Screenshots/Screenshot_" + stamp + ".png", "wb") as file:
                file.write(screenshot_data)
            print("Screenshot saved successfully.")
        else:
            print("Failed to capture the screenshot.")
        with status_message:
            st.info(report_root + "/MITE_Cases/Screenshots/Screenshot_" + stamp + ".png created and added to case folder.")
    
def get_Storage_size():
    howBigIsStorage = Popen([adb, "shell", "du", "-d 1", "-hc", "/storage"], stdout=PIPE, creationflags=CREATE_NO_WINDOW)
    storeLines = howBigIsStorage.stdout.readlines()
    if pull_storage == True:
        with update_msg:
            with st.spinner("Getting Storage Size..."):
                for line in storeLines:
                    line = line.decode('utf-8')
                    print(line)
                    if "storage" in line:
                        nums = line.split()
                        stored_size = nums[0] 
                        print(stored_size + "stored size")
                        if stored_size == "0" or stored_size == None:
                            emulated = Popen([adb, "shell", "du", "-d 1", "-hc", "/storage/emulated/0"], stdout=PIPE, creationflags=CREATE_NO_WINDOW)
                            em_lines = emulated.stdout.readlines()
                            for lined in em_lines:
                                lined = lined.decode('utf-8')
                                if "total" in lined:
                                    print(lined)
                                    numd = lined.split()
                                    emulated_size = numd[0] 
                            
                                    if stored_size == "0":
                                        return emulated_size 
                        return stored_size

def pull_storage_data(destination_folder, caseNumber):
    pull_folder = os.path.join(destination_folder, "Mite_Backup")
    if not os.path.isdir(pull_folder):
        os.makedirs(pull_folder)

    backup_file = os.path.join(pull_folder, f"{caseNumber}_Storage.tar")
    unpack_fold = os.path.join(pull_folder, "UnpackedData")
    if not os.path.isdir(unpack_fold):
        os.makedirs(unpack_fold)
   
    with update_msg:
        with st.spinner("Pulling storage data..."):
           
            get_pull_folders = run([adb, 'shell', 'ls', 'storage'],stdout=subprocess.PIPE,  # this code pulls the Storage subfolders and handles unique ids for SD cards
            stderr=subprocess.PIPE,
            text=True,  # Use text=True for string output, or omit for bytes
            check=True  # Raise an exception if the command returns a non-zero exit code
            )
            storage_subfolders_onphone = get_pull_folders.stdout.splitlines()
            
            for d in storage_subfolders_onphone:
                try:
                    pullit = run([adb, "pull", "-a", "/storage/"+ d, unpack_fold + '/storage'], shell=True, creationflags=CREATE_NO_WINDOW, check=True)
                except subprocess.CalledProcessError as e:
                    st.error(f"Error pulling storage data: {e}") 
                    pass
            try:   
                pullself = run([adb, "pull", "-a", "/storage/self/primary/DCIM", unpack_fold + '/self/primary/DCIM'], shell=True, creationflags=CREATE_NO_WINDOW, check=True)
            except subprocess.CalledProcessError as e:
                st.error(f"Error pulling storage data: {e}")
                pass
            try:    
                pullemulated = run([adb, "pull", "-a", "/storage/emulated/0/DCIM", unpack_fold + 'emulated/0/DCIM'], shell=True, creationflags=CREATE_NO_WINDOW, check=True)
            except subprocess.CalledProcessError as e:
                st.error(f"Error pulling storage data: {e}")
                pass

    with tarfile.open(backup_file, "w") as archive:
        archive.add(unpack_fold, recursive=True)

    return backup_file
def get_all_files_and_pull(output_folder):
    """
    Get all file paths on the Android device and pull them to a local folder.

    Args:
        device_folder (str): Path on the Android device to start listing files.
        local_folder (str): Local folder to store pulled files.
    """
    # Create the local folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    try:
        
        # Pull each file to the local folder
        for file_path in Master_file_list:
            # Normalize file path and extract the file name
            # file_path = file_path.strip()
            # file_name = os.path.basename(file_path)

            # Construct the local file path
            local_file_path = os.path.join(output_folder, file_path)

            # Pull the file using adb pull
            subprocess.run(["adb", "pull", file_path, local_file_path], shell=True, creationflags=CREATE_NO_WINDOW, check=True)
            # print(f"Successfully pulled: {file_path} to {local_file_path}")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

#############       Mighty land of functions        ##################
def work_site():                #cause script to execute in directory containing script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  #move to dir that holds this script and ADB (need to change for exe)
    global pwd
    pwd = os.path.dirname(os.path.abspath(__file__))
def get_report_settings():
    with open(pwd + "/Support_Files/last.config", "r") as last_input:
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
def opening_processes():    #Checks for Profiles directory and makes one if needed
    try:
        prof_list = os.listdir(pwd + '/Profiles')   # if script doesn't have the Profiles directory it makes one
    except FileNotFoundError:
        os.makedirs(pwd + '/Profiles')    
        prof_list = os.listdir(pwd + '/Profiles')  

def gallery_view(folder):   #Thumbnail gallery presentation
    thumb_Files = []
    for root, dirs, file in os.walk(folder):
        for f in file:
            fil = os.path.join(root,f)
            pictype = imghdr.what(fil)      #   verifies file is a valid image format
            if pictype != None:
                thumb_Files.append(fil)
        
    img_file_num = len(thumb_Files)
    print(img_file_num)

    st.header("Thumbnail Images")
    st.write(str(img_file_num) + " Thumbnails Located")
    idx = 0

    for _ in range(len(thumb_Files)-1):
        cols = st.columns(4)

        if idx < len(thumb_Files):
            cols[0].image(thumb_Files[idx],width=150, caption=thumb_Files[idx])
            idx += 1
        if idx < len(thumb_Files):
            cols[1].image(thumb_Files[idx],width=150, caption=thumb_Files[idx])
            idx += 1
        if idx < len(thumb_Files):
            cols[2].image(thumb_Files[idx],width=150, caption=thumb_Files[idx])
            idx += 1
        if idx < len(thumb_Files):
            cols[3].image(thumb_Files[idx],width=150, caption=thumb_Files[idx])
            idx += 1

        else:
            break

def store_new_user_inputs(old_user_entries):    #Keeps user inputs for form fields
    if old_user_entries[0] != inv:
        old_user_entries[0] = inv
    if old_user_entries[1] != agency:
        old_user_entries[1] = agency

    update_to_lastconfig = ",".join(old_user_entries)
    with open(pwd + "/Support_Files/last.config", "w") as new_input:
        new_input.write(update_to_lastconfig)
        
def access_user_inputs():       #   Function to read user last input for name agency & case folder fields
    try:
        with open(pwd + "/Support_Files/last.config", "r") as last_input:       # List layout = ['Investigator:', 'Agency:', 'CaseFolder:']
            inputs = last_input.readline()
            inputs = inputs.split(",")
            last_inv = inputs[0]
            last_agency = inputs[1]
            last_CaseFolder = inputs[2] 
    except IndexError:                      #   if the last.config file gets corrupted this resets it as empty
        with open(pwd + "/Support_Files/last.config", "w") as last_input:
            last_input.write(" , , ")
            last_inv = ""
            last_agency = ""
            last_CaseFolder = ""
    
    return [last_inv, last_agency, last_CaseFolder]
def check_for_device():     #Checks if adb device connected
    dev_state = run([adb, 'get-state'], stdout=PIPE, stderr=PIPE, universal_newlines=True, creationflags=CREATE_NO_WINDOW)
    #   get device details name model sn
    out = (dev_state.stdout)
        
    if 'device\n' in out:
        return True
        
    else:
        # time.sleep(2)
        # check_for_device()
        # time.sleep(1)
        return False
       
def Dev_properties():       #Collects basic device info
    dev_prop = run([adb, 'shell', 'getprop'], stdout=PIPE, stderr=PIPE, universal_newlines=True, creationflags=CREATE_NO_WINDOW)
    
    dat = now.strftime("%m_%d_%Y_%H-%M-%S")
   
    dev_state = run([adb, 'get-state'], stdout=PIPE, stderr=PIPE, universal_newlines=True, creationflags=CREATE_NO_WINDOW)
    #   get device details name model sn
    out = (dev_state.stdout)
        
    if 'device\n' in out:
        dev_prop = run([adb, 'shell', 'getprop'], stdout=PIPE, stderr=PIPE, universal_newlines=True, creationflags=CREATE_NO_WINDOW)
    
        props = dev_prop.stdout
        props = props.split('\n')
        for lines in props:
            try:
                if 'build.version.release' in lines:
                    key, value = lines.strip().split(':', 1)
                    value = value.replace('[', '')
                    value = value.replace(' ', '')
                    global build_version
                    build_version = value.replace(']', '')
            except NameError:
                print("Sim name error")
            try:
                if 'sim.operator.alpha' in lines:
                    key, value = lines.strip().split(':', 1)
                    value = value.replace('[', '')
                    value = value.replace(' ', '')
                    global sim_Carrier
                    sim_Carrier = value.replace(']', '')
            except NameError:
                print("Sim name error")
            try:
                if 'ro.build.date.utc' in lines:
                    key, value = lines.strip().split(':', 1)
                    value = value.replace('[', '')
                    # value = value.replace(' ', '')
                    global Build_date
                    Build_date = value.replace(']', '')  
                    Build_date = int(Build_date)
                    Build_date = datetime.datetime.utcfromtimestamp(Build_date).strftime('%d/%m/%Y %H:%M')
            except NameError:
                print("Build date name error")
            
            try:
                if 'ro.crypto.state' in lines:
                    key, value = lines.strip().split(':', 1)
                    value = value.replace('[', '')
                    value = value.replace(' ', '')
                    global encrypt_status
                    encrypt_status = value.replace(']', '')   
                    encrypt_status = encrypt_status.upper() 
            except NameError:
                print("crypto name error")
            # if 'ro.home.operator' in lines:
            try:
                if 'home.operator.carrierid' in lines:
                    key, value = lines.strip().split(':', 1)
                    value = value.replace('[', '')
                    value = value.replace(' ', '')
                    global home_Carrier
                    home_Carrier = value.replace(']', '')  
            except NameError:
                print("carrier name error")    
            try:
                if 'board.platform' in lines:
                    key, value = lines.strip().split(':', 1)
                    value = value.replace('[', '')
                    value = value.replace(' ', '')
                    global chipset
                    chipset = value.replace(']', '') 
                    chipset = chipset.upper()
            except NameError:
                print("chipset name error")
            try:
                if 'ro.hardware.chipname' in lines:
                    key, value = lines.strip().split(':', 1)
                    value = value.replace('[', '')
                    value = value.replace(' ', '')
                    chipset = value.replace(']', '') 
                    chipset = chipset.upper() 
            except NameError:
                print("chipname name error")
            try:
                if 'ro.product.manufacturer' in lines:
                    key, value = lines.strip().split(':', 1)
                    value = value.replace('[', '')
                    value = value.replace(' ', '')
                    global dev_Manufacturer
                    dev_Manufacturer = value.replace(']', '') 
                    dev_Manufacturer = dev_Manufacturer.upper()
            except NameError:
                print("manufacturer name error")
            try:
                if 'ro.product.model' in lines:
                    key, value = lines.strip().split(':', 1)
                    value = value.replace('[', '')
                    value = value.replace(' ', '')
                    global dev_Model
                    dev_Model = value.replace(']', '') 
            except NameError:
                print("device model name error")
            try:
                if 'ro.product.name' in lines:
                    key, value = lines.strip().split(':', 1)
                    value = value.replace('[', '')
                    value = value.replace(' ', '')
                    global dev_Name
                    dev_Name = value.replace(']', '') 
            except NameError:
                print("device name name error") 
            try:
                if 'ro.serialno' in lines:
                    key, value = lines.strip().split(':', 1)
                    value = value.replace('[', '')
                    value = value.replace(' ', '')
                    global dev_Serial
                    dev_Serial = value.replace(']', '')
            except NameError:
                print("device serial name error") 
            try:
                if 'airplane_mode_on' in lines:
                    key, value = lines.strip().split(':', 1)
                    value = value.replace('[', '')
                    value = value.replace(' ', '')
                    global wifi_mac
                    airplane_state = value.replace(']', '')
                    if airplane_state == "1":
                        wifi_mac = "N/A (Airplane Mode is Enabled)"
                    else:
                        get_mac_addr = run([adb, "shell", "cat /sys/class/net/wlan0/address"], stdout=PIPE, stderr=PIPE, universal_newlines=True, creationflags=CREATE_NO_WINDOW)
                        wifi_mac = get_mac_addr.stdout
            except:
                print("macaddresserror")
def read_profile():                 #   function reads selected user created profile
    #   Reads triage profile. Grabs values between brackets to add to appropriate list in global variables
    clean_list = []
    if profile == "None Selected":
        pass
    if profile != "None Selected":
        with open(pwd + '/Profiles/' + profile, 'r') as selected_profile:
            
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
    
def properties_view():      #Presents basic device info in a table
    # try:
        dd =  {"Attached Device":[dev_Model,dev_Manufacturer,dev_Name,dev_Serial, imei,
         chipset,phone_number,imsi,iccid,sim_Carrier,home_Carrier,encrypt_status,build_version, Build_date, wifi_mac]}
                
        props = pd.DataFrame(dd, index=["Model","Manufacturer","Device Name","Serial Number","IMEI","Processor","Phone Number", "IMSI", "ICCID",
        "SIM Carrier" ,"Home Network", "Encryption Status","Android Version", "System Build Date", "WiFi MAC"])
        st.table(props)

def get_profiles():         #List of user created profiles
    for profs in os.listdir(pwd + "/Profiles"):
        if not profs.startswith("."):
            profile_list.append(profs)
    
def make_report_folders():
    global Case_Folder
    # changed to use Windows user's documents folder
    # Case_Folder = (str(pwd) + '/Cases/' + str(casenum) + "_" + dev_Name + "_" + stamp) 
    Case_Folder = (report_root + '/MITE_Cases/' + str(casenum) + "_" + dev_Name + "_" + stamp) 

    os.makedirs(Case_Folder)
    os.makedirs(str(Case_Folder) + '/Raw_Reports')
    os.makedirs(str(Case_Folder) + '/Thumbnails')
   

def collect_Thumbnails():               #   currently only pulling small number of files despite adb saying all pulls are successful
    global active_thumb
    active_thumb = 0               # for progress bar increments
    thumb_paths = []
    maybe_list = []
    
    for ab_path in Master_file_list:
        if 'thumb' in ab_path :
            maybe_list.append(ab_path)
        # if '._' in ab_path and ".jpg" in ab_path:
        #     thumb_paths.append(ab_path)           
        # if 'thumbs' in ab_path:
        #     maybe_list.append(ab_path)
    # find_no_ext_img = re.compile("^([^.]+)$")
    # find_no_ext_img = re.compile("(^[^\./pro* | ](.+?)(\.[^.]*$|$)")
    # sneaky_list = list(filter(find_no_ext_img.match, Master_file_list))
    # print(sneaky_list)
    # no_ext_list.extend(sneaky_list) 
    
    for mystery_file in maybe_list:   
        # if os.path.isfile(mystery_file) == True:
        no_extension_search = run([adb, "shell", "file", mystery_file], stdout=PIPE, stderr=PIPE, universal_newlines=True, creationflags=CREATE_NO_WINDOW)
        mimeinfo = no_extension_search.stdout
        if "image data" in mimeinfo:
            thumb_paths.append(mystery_file)
    
    # print(thumb_paths)
    global thumb_count_total    
    thumb_count_total = len(thumb_paths)
    global thumb_folder
    thumb_folder = (Case_Folder + '/Thumbnails')
    for thing in thumb_paths:
        active_thumb = active_thumb + 1
        # if reportmode_thumbs == True:
        #     progress_window['ACTION'].update("Gathering thumbnails " + str(active_thumb) + " of " + str(thumb_count_total))
        #     progress_window.refresh()
        run([adb, 'pull', thing, thumb_folder],shell=False, creationflags=CREATE_NO_WINDOW)
        with status_message:
            st.info("Pulling thumbnail - " + thing)

def MD5_scan():
    media_list = []         #   List of movie and image absolute paths
    
    for ele in Master_file_list:
        if "\ " in ele:
            ele = ele.replace('\ ', '\\ ')      #   Added for funky whatsapp file paths

        for ext in picture_files: 
            if ele.endswith(ext):
                media_list.append(ele)
        for ext in video_files:
            if ele.endswith(ext):
                media_list.append(ele)
    n = 0
    media_count = len(media_list)
    
    for f in media_list:
        n = n + 1
        with status_message:
            st.info("Gathering hash for " + f)
        # progress_window['ACTION'].update("Gathering MD5 for " + f + " " + str(n) + " of " + str(media_count))
        # progress_window.refresh()
        # if reportmode_hashes == True:
        md5return = run([adb, 'shell', 'md5sum ' + '"' +f+ '"' + " | grep -v 'No such file or directory'"], stdout=PIPE, stderr=PIPE, universal_newlines=True, creationflags=CREATE_NO_WINDOW)  
        hash5 = (md5return.stdout)
        hash5 = hash5.upper()
        Master_hash_list.append(hash5)

            
    with open(Case_Folder + '/Raw_Reports/' + dev_Model + '_Media_Hashes.txt', 'a') as hashreport:
        # hashreport.write("MD5\tFilename\n")
        for result in Master_hash_list:
            hashreport.write(result)

    for inst in Master_hash_list:
        for eek in comparison_hashes:
            if eek in inst:
                match_hashes.append(inst)
    status_message.empty()

def make_report(folder):
    #   Start with raw text reports for large output
    print("make report test - folder = " + folder)
    with open(folder + '/Raw_Reports/' + dev_Model + '_' + now.strftime(" %Y%m%d%H%M%S") + '_Recovered_File_Names.txt', 'w', encoding='utf-8') as file_report:
        file_report.write('Case Number: ' + casenum +'\n\n')
        file_report.write('Device Name: ' + dev_Model +'\n\n')
        file_report.write('Recovered File/Directory Names\n\n')
        for ele in Master_file_list:
            file_report.write(ele + '\n')
    with open(folder +'/Raw_Reports/' + dev_Model + '_' + now.strftime(" %Y%m%d%H%M%S") + '_Recovered_Application_List.txt', 'w') as app_report:
        app_report.write('Case Number: ' + casenum +'\n\n' )
        app_report.write('Device Name: ' + dev_Model +'\n\n')
        app_report.write('Recovered Installed Applications\n\n')
        for op in Master_application_list:
            app_report.write(op + '\n') 
    # make lists of matches for filenames, hashes, and keywords 
    if len(comparison_filenames) > 0:
        for ele in Upper_file_list:
            for nam in comparison_filenames:
                if nam in ele:
                    match_filenames.append(ele)
                    # print('match name' + ele)
    if len(comparison_hashes) > 0:
        for ele in Master_hash_list:
            for num in comparison_hashes:
                if num in ele:
                    match_hashes.append(ele)
                    
    if len(comparison_keywords) > 0:
        for ele in Upper_file_list:
            for wrd in comparison_keywords:
                if wrd in ele:
                    match_keywords.append(ele)
                    # print('match key' + ele)

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
    elements.append(Paragraph("<font color='Darkslategray'>Investigator: </font>" + inv_name, styleN))
    elements.append(Paragraph("<font color='Darkslategray'>Agency: </font>" + agency_name, styleN))
    
    
    elements.append(Paragraph(" ", styleN))
    elements.append(HRFlowable(width=w, thickness=t, color=c, spaceBefore=2, vAlign='MIDDLE', lineCap='square'))    #   Border
    elements.append(Paragraph(" ", styleN))
    
    elements.append(Paragraph("<i><font color='Darkslategray'>Date/Time: </font></i>" + now.strftime("%m/%d/%Y %H:%M:%S"), styleN))
    elements.append(Paragraph("<i><font color='Darkslategray'>Case Number: </font></i>" + casenum, styleN))
    # elements.append(Paragraph("<font color='Darkslategray'>Search Authority: </font>" + search_authority, styleN))

    elements.append(Paragraph(" ", styleN))
    elements.append(HRFlowable(width=w, thickness=t, color=c, spaceBefore=2, vAlign='MIDDLE', lineCap='square'))    #   Border
    elements.append(Paragraph(" ", styleN))
    
    elements.append(Paragraph("<i><font color='Darkslategray'>Device Manufacturer: </font></i>" + dev_Manufacturer, styleN))
    elements.append(Paragraph("<i><font color='Darkslategray'>Device Model: </font></i>" + dev_Model, styleN))
    elements.append(Paragraph("<i><font color='Darkslategray'>Device Name: </font></i>" + dev_Name, styleN))
    elements.append(Paragraph("<i><font color='Darkslategray'>Device Serial: </font></i>" + dev_Serial, styleN))
    elements.append(Paragraph("<i><font color='Darkslategray'>IMEI: </font></i>" + imei, styleN))
    elements.append(Paragraph("<i><font color='Darkslategray'>Android Version: </font></i>" + build_version, styleN))

    elements.append(Paragraph(" ", styleN))
    elements.append(HRFlowable(width=w, thickness=t, color=c, spaceBefore=2, vAlign='MIDDLE', lineCap='square'))    #   Border
    elements.append(Paragraph(" ", styleN))

    elements.append(Paragraph("<i><font color='Darkslategray'>SIM Carrier: </font></i>" + sim_Carrier, styleN))
    elements.append(Paragraph("<i><font color='Darkslategray'>System Build Date: </font></i>" + Build_date, styleN))
    elements.append(Paragraph("<i><font color='Darkslategray'>Chipset: </font></i>" + chipset, styleN))
    elements.append(Paragraph("<i><font color='Darkslategray'>Encryption State: </font></i>" + encrypt_status, styleN))
    
    elements.append(Paragraph(" ", styleN))
    elements.append(HRFlowable(width=w, thickness=t, color=c, spaceBefore=2, vAlign='MIDDLE', lineCap='square'))    #   Border
    elements.append(Paragraph(" ", styleN))

    elements.append(Paragraph("<i><font color='Darkslategray'>Device User List</font></i>"))
    for line in Master_user_list:
        elements.append(Paragraph(line))
    for user in Master_user_list:
        if "150:" in user:
            elements.append(Paragraph('********    SECURE FOLDER IS IN USE ON DEVICE    ********\n', styleN)) 
    
    
    elements.append(Paragraph(" ", styleN))
    elements.append(HRFlowable(width=w, thickness=t, color=c, spaceBefore=2, vAlign='MIDDLE', lineCap='square'))    #   Border
    elements.append(Paragraph(" ", styleN))

    elements.append(Paragraph("<i><font color='Darkslategray'>File System Summary:</font></i>", styleN))
    elements.append(Paragraph("<i><font color='Darkslategray'>Total Files Located on Device: </font></i>" + str(file_count), styleN))
    elements.append(Paragraph("<i><font color='Darkslategray'>Image Files Located on Device: </font></i>" + str(imgcnt), styleN))
    elements.append(Paragraph("<i><font color='Darkslategray'>Video Files Located on Device: </font></i>" + str(vdcnt), styleN))

    elements.append(Paragraph(" ", styleN))
    elements.append(HRFlowable(width=w, thickness=t, color=c, spaceBefore=2, vAlign='MIDDLE', lineCap='square'))    #   Border
    elements.append(Paragraph(" ", styleN))

    elements.append(Paragraph("<i><font color='Darkslategray'>Installed 3rd Party Applications on Device:</font></i>", styleN))
    for item in Master_application_list:
        if len(item) > 3:
            elements.append(Paragraph("·&nbsp;&nbsp;" + item, styleA))
    elements.append(Paragraph("<i><font color='Darkslategray'>Installed 3rd Party Applications in Secure Folder:</font></i>", styleN))
    for app in sec_apps:
        elements.append(Paragraph("·&nbsp;&nbsp;" + app, styleA))

    elements.append(Paragraph(" ", styleN))
    elements.append(HRFlowable(width=w, thickness=t, color=c, spaceBefore=2, vAlign='MIDDLE', lineCap='square'))    #   Border
    elements.append(Paragraph(" ", styleN))

    elements.append(Paragraph("<i><font color='Darkslategray'>Examiner Notes: </font></i>", styleN))
    elements.append(Paragraph(notes, styleN))

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

        if len(comparison_hashes) > 0:
            elements.append(Paragraph("<i><font color='Darkslategray'>MD5 Hash Hits: </font></i>", styleN))
            elements.append(Paragraph(" ", styleN))
            # Make heading for each column and start data list
            column1Heading = "MD5"
            column2Heading = "File Path"
            data = [[column1Heading,column2Heading]]
            for entry in match_hashes:
                md5, name = entry.strip().split(' ', 1)
                                # print(name)
                                # print(md5)
                name = name.lower()
                name = Paragraph(name, styleA)
                md5 = Paragraph(md5, styleA)
                data.append([md5, name]) 
                
            tableThatSplitsOverPages = Table(data, [6.5 * cm, 9.6 * cm], repeatRows=1)
            
            tableThatSplitsOverPages.hAlign = 'CENTER'
            tblStyle = TableStyle([('TEXTCOLOR',(0,0),(-1,-1),colors.black),
                                ("ALIGN", (0,0), (-1,-1), "CENTER"),
                                ('VALIGN',(0,0),(-1,-1),'TOP'),            
                                ('BOX',(0,0),(-1,-1),2,colors.black),
                                ('GRID',(0,0),(-1,-1),1,colors.black)])
            tblStyle.add('BACKGROUND',(0,0),(4,0),colors.darkgrey)
            tblStyle.add('BACKGROUND',(0,1),(-1,-1),colors.white)
            tableThatSplitsOverPages.setStyle(tblStyle)
            # tableThatSplitsOverPages = KeepInFrame(0, 0, tableThatSplitsOverPages, mode='shrink')
            elements.append(tableThatSplitsOverPages) 
            
            elements.append(Paragraph(" ", styleN))
            if len(match_hashes) == 0:
                elements.append(Paragraph("No matching hashes found.", styleA))
            
        if len(comparison_hashes) == 0:
            pass
    if len(profile) == 0:
        pass
    doc.build(elements)  

def show_triage_results():
    st.header("Triage Summary")
    st.write("Total Files and Directories Found: " + str("{:,}".format(len(Master_file_list))))
    st.write("Image Files Found: " + str(imgcnt))
    st.write("Video Files Found: " + str(vdcnt))
    st.markdown("---")
    st.header("Installed Third Party Applications")
    for app in Master_application_list:
        st.write(app)
    if len(sec_apps) > 0:
        st.markdown("<h4 style='text-align: center; color: red;'>Applications in Secure Folder</h4>",unsafe_allow_html=True)
        for app in sec_apps:
            st.write(app)
        
    st.markdown("---")
    st.header("Device Users")
    
    for user in Master_user_list:           #   USER INFO
        if "150:" in user:
            st.markdown("<h4 style='text-align: center; color: red;'>Secure Folder is in Use on Device</h4>",unsafe_allow_html=True) 
    for line in Master_user_list:
        st.write(line)
    st.markdown("---")
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
    #   START OF HASH MATCH TABLE
    show_name_List = []
    show_Hashed_list = []
    
    if len(match_hashes) >0:
        st.header("MD5 Hash Matches")
        for entry in match_hashes:
            md5, name = entry.strip().split(' ', 1)
                            # print(name)
                            # print(md5)
            name = name.lower()
            show_name_List.append(name)
            show_Hashed_list.append(md5)
        datas = {"MD5": show_Hashed_list}   
        hash_table_show = pd.DataFrame(datas, index=pd.Index(show_name_List, name="File Path"))
        hash_table_show.index.name = None
        st.dataframe(hash_table_show)
        st.markdown("---")

#####   OPENING FUNCTIONS   #####
work_site() 
inv_name, agency_name, report_root = get_report_settings()       
print(inv_name, agency_name, report_root)     
opening_processes()
run([adb, 'start-server'], stdout=PIPE, stderr=PIPE, universal_newlines=True, creationflags=CREATE_NO_WINDOW)

check_for_device()
connected_to_Device = check_for_device()

if connected_to_Device == False:
    # print("False out")
    st.write("Attach an unlocked Android device with ADB Debugging enabled. Select the button below to connect. Then provide any trust/permission prompts that appear on the device's screen.")
    TESTCONNECTION = st.button("Test for Connection", key="TESTCONNECTION")
    st.write(" ")
    st.write(" ")
    st.caption("Tips: Enable USB debugging in Developer Options by navigating to:")
    st.caption("- Settings")
    st.caption("- About Device (or similiar)")
    st.caption("- Press Software Build Number 7 times to activate Developer Options") 
    st.caption("- In Developer Options, enable Stay Awake & USB Debugging") 
    st.caption("- When prompted on the device, choose to always trust this computer.") 
    st.caption("""If subject device is attached but not recognized, change USB connection to MTP (Media Transfer) or PTP (Photo Transfer) to 
    prompt handshake. If necessary, revoke previous ADB permissions and reconnect device.
    """)
    
    if TESTCONNECTION == True:
        check_for_device()

if connected_to_Device == True:
    st.header("Android Triage")
    update_msg = st.empty()
    try:
        stored = MITE_ADB.get_storage_info()
        colA, colB = st.columns(2)
        with colA:
            st.metric(label="Internal Storage", value=stored[0] + ' Used', delta=(stored[1] + " Total"), delta_color="off")
        with colB:
            st.metric(label="External Storage", value=stored[2] + ' Used', delta=(stored[3] + " Total"), delta_color="off")
    except UnboundLocalError:
        st.error("Reconnect unlocked device and try again.")
    
    get_profiles()
    Dev_properties()
    
    service_IDs = MITE_ADB.service_call_for_IDs()
    phone_number = ", ".join(service_IDs[0])
    imei = ", ".join(service_IDs[1])
    imsi = ", ".join(service_IDs[2])
    iccid = ", ".join(service_IDs[3])
    properties_view()
    # for place in stored:
    #     st.write(place)
    
    casenum = st.sidebar.text_input(":red[Case Number*]", key="CASENUM",)
    
    profile = st.sidebar.selectbox("Triage Profile", profile_list)
    Triage_Report = st.sidebar.checkbox("Collect Triage Info to Report",value=True)
    GETHASHES = st.sidebar.checkbox("Collect MD5 Hashes for Media", help="THIS IS SLOW! IT WILL ALSO CHANGE LAST ACCESSED TIMESTAMPS ON THE DEVICE! USE ONLY IF THAT IS ACCEPTABLE!")
    GETTHUMBS = st.sidebar.checkbox("Collect Thumbnails", help="THIS WILL CHANGE LAST ACCESSED TIMESTAMPS ON THE DEVICE! USE ONLY IF THAT IS ACCEPTABLE!")
    st.sidebar.markdown("---")
    adb_check = st.sidebar.checkbox("ADB Backup", value=True)
    storeMBsize = str(0)
    pull_storage = st.sidebar.checkbox("Pull Storage Areas", disabled=False)
    # storeMBsize = st.text("User Storage Selected for Pull - " + str(get_Storage_size()))
    # UNPACK = st.sidebar.checkbox("Attempt to Unpack ADB Backup", value=True)
    TRIAGE = st.sidebar.button("Begin Triage",)
    st.sidebar.markdown("---")
    st.sidebar.write("Capture Device Screen")
    screenshot = st.sidebar.button("Capture")
    st.sidebar.markdown("---")

    notes = st.text_area(label=":red[Investigator Notes]",height=250,)
    # st.sidebar.text_input("Case Folder", value=Case_Folder, help="Case data will be stored here in a folder using the provided case number") 
    st.sidebar.text("© 2023 North Loop Consulting")

    if TRIAGE == True:
        if len(casenum) == 0:
            with status_message:
                st.error("Case Number must be provided.")
        else:
            if Triage_Report == True:
                with update_msg:
                    with st.spinner("Gathering Device Info..."):
                        read_profile()
                        def_folder = (pwd + '/' + casenum + '_' + dev_Name + '_' + dat)
                        time_start = time.time()  
                        apps = MITE_ADB.application_info()  #gets app list
                        Master_application_list.extend(apps)
                        sec_apps = MITE_ADB.secure_folder_apps(Master_application_list)
                with update_msg:
                    with st.spinner("Digging into File and Application Info... "):
                        status_message = st.empty()
                        Users = MITE_ADB.ADB_get_users()    #gets user list
                        Master_user_list.extend(Users)

                        make_report_folders()

                        file_list = MITE_ADB.ADB_file_search()  #gets a list of files/directories
                        Master_file_list.extend(file_list)

                        file_count = (len(Master_file_list))
                        file_count = "{:,}".format(file_count)

                        for ins in file_list:               #   Upper case list for string comparisons
                            uPPed = ins.upper()
                            Upper_file_list.append(uPPed)

                        vdcnt = 0                       #   Getting type counts for video files
                        for fl in Master_file_list:
                            for ex in video_files:
                                if fl.endswith(ex):
                                    vdcnt = vdcnt + 1
                        vdcnt = "{:,}".format(vdcnt)

                        imgcnt = 0                      #   Getting type counts for img files
                        for fl in Master_file_list:
                            for ex in picture_files:
                                if fl.endswith(ex):
                                    imgcnt = imgcnt + 1
                        imgcnt = "{:,}".format(imgcnt)
                with update_msg:
                    with st.spinner("Collecting MD5 Hashes for Media Files..."):
                        if GETHASHES == True:
                            MD5_scan()
                with update_msg:
                    with st.spinner("Collecting Thumbnails..."): 
                        if GETTHUMBS == True:
                            collect_Thumbnails()
                            
                        make_report(Case_Folder)        #   MAKE REPORT
                        
                        time_end = time.time()                      #   Just for diagnostic testing for script run times
                        run_time = time_end - time_start
                        run_time = round(run_time)
                        run_time = str(run_time)
                        runtime = st.write("Triage complete in " + run_time + " seconds")
                        show_triage_results()
                        if GETTHUMBS == True:
                            gallery_view(thumb_folder)
                status_message.empty()      #removes update message
                if adb_check == True or pull_storage == True: 
                    folder = make_backup_folder(Case_Folder)
                if adb_check == True:
                    backed_up = make_backup(BACKUP_Folder, casenum)
              
                if pull_storage == True:
                    pulled_store = pull_storage_data(BACKUP_Folder, casenum)
                

                # if UNPACK == True:
                #     if adb_check == True:
                #         unpack_to_dis = back_folder + "/UnpackedData"
                #         tar_version = backed_up + ".tar"
                #     if pull_storage == True:
                #         unpack_pull = pull_folder + "/UnpackedData"
                #         pull_tar_version = pulled_store
                    
                #     try:
                #         with update_msg:
                #             with st.spinner("Unpacking Backup to .tar file..."):
                #                 with open(backed_up, "rb") as ab:
                #                     with open(tar_version, "wb") as tar:
                #                         decrypt_android_backup(in_stream=ab, out_stream=tar, pw_callback=get_password)
                #                 try:
                #                     with update_msg:    
                #                         with st.spinner("Unpacking .tar file to folders..."):
                #                             if tarfile.is_tarfile(tar_version) == True:
                #                                 with tarfile.open(tar_version) as f:
                #                                     f.extractall(path=unpack_to_dis) 
                #                 except tarfile.ReadError:
                #                     print("tar file read error")
                #                     pass
                #                 except NotADirectoryError:
                #                     with update_msg:
                #                         st.error("Error unpacking Android backup. Seek other tools for analysis")
                #                         pass
                #     except NameError:       # occurs when adb backup not run
                #         pass
                #     except AssertionError: 
                #         st.error("There was an error unpacking the backup. Use an alternative tool to review the collected data.")
                #     try:
                #         with update_msg:
                #             with st.spinner("Unpacking .tar file to folders..."):
                #                 if tarfile.is_tarfile(pull_tar_version) == True:
                #                     if not "Storage" in pull_tar_version:
                #                         with tarfile.open(pull_tar_version) as f:
                #                             f.extractall(path=unpack_to_dis) 
                #     except tarfile.ReadError:
                #         print("tar file read error")
                #         pass
                #     except NameError:
                #         print("pull not selected - passing")
                #         pass

    if screenshot == True:
        android_screenshot()

        
