import streamlit as st
import os
import json
import wx
import pathlib




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

#Custom button
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
def work_site():                #cause script to execute in directory containing script and adb
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  #move to dir that holds this script and ADB (need to change for exe)
    global pwd
    pwd = os.path.dirname(os.path.abspath(__file__))
    pwd = os.path.dirname(pwd)
work_site()

def select_folder():
    
    app = wx.App(None)
    dialog = wx.DirDialog(None, "Select a folder:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
    # Set the window style to include wx.STAY_ON_TOP
    dialog.SetWindowStyleFlag(dialog.GetWindowStyleFlag() | wx.STAY_ON_TOP)

    if dialog.ShowModal() == wx.ID_OK:
        folder_path = dialog.GetPath()
    else:
        folder_path = Last_Used["Report Location"]
    dialog.Raise()
    dialog.Destroy()
    app.MainLoop()  # Don't forget to call MainLoop to properly handle events
    folder_path = folder_path.replace('\\','/')
    return folder_path
def get_folder_input(folder_value):
    folderinput = st.text_input("Report Location", value=folder_value)
    return folderinput
def add_logo():     #Places MITE logo in upper left
    st.markdown(
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



def list_profiles():
    st.sidebar.markdown("<h4 style='text-align: center; color: red;'>Stored Profiles</h4>",unsafe_allow_html=True)
    profiles_loc = pwd + "/Profiles/"
    list_of_profiles = os.walk(profiles_loc)
    for root, dirs, files in list_of_profiles:
        for f in files:
            if not f.startswith(".DS"):
                st.sidebar.write(f)

def store_new_user_inputs(old_user_entries):    #Keeps user inputs for form fields
    if old_user_entries["Examiner"] != inv:
        old_user_entries["Examiner"] = inv
    if old_user_entries["Organization"] != agency:
        old_user_entries["Organization"] = agency
    if old_user_entries["Report Location"] != selected_folder_path:
        old_user_entries["Report Location"] = selected_folder_path
    # update_to_lastconfig = ",".join(old_user_entries)
    with open(pwd + "/Support_Files/last.config", "w") as new_input:
        json.dump(old_user_entries, new_input)
        
def access_user_inputs():       #   Function to read user last input for name agency & case folder fields
    try:
        with open(pwd + "/Support_Files/last.config", "r") as last_input:
            content = last_input.read()
            result_dict = json.loads(content)
            last_inv = result_dict["Examiner"]
            last_agency = result_dict["Organization"]
            last_ReportFolder = result_dict["Report Location"]
                    
            print(result_dict)
    except IndexError or TypeError:
        with open(pwd + "/Support_Files/last.config", "w") as last_input:
            last_input.write("""{"Examiner": "Your Name Here", 
                    "Organization": "Your Organization Here", 
                    "Report Location": "/"}""")
        last_inv = ""
        last_agency = ""
        last_ReportFolder = ""
    
    return {"Examiner": last_inv, "Organization": last_agency, "Report Location": last_ReportFolder}
          


st.header("Generate a Triage Profile")

prof_name = st.text_input("Profile Name*", help="Profile Name is required. Prohibited characters = /, \\\, <, >, :, |, ?, *")
file_inputs = st.text_area(label="File Names", help="Provide one (1) filename per line.")
keyword_inputs = st.text_area(label="Keywords", help="Provide one (1) keyword per line.")
hash_inputs = st.text_area(label="MD5 Hashes", help="Provide one (1) hash value per line.")

collapsable_box = st.expander("Help",)
with collapsable_box:    
    st.write("")
    st.write("""Profiles work by comparing data you provide to data found during the triage process.""") 
    st.write("Searches are not case sensitive, but character matches are exact (ex. 'IMG_00025' will not find 'IMG_0002').")
    st.write("""Once generated, the profile file is a flat text file stored in the 'Profiles' directory of the tool. 
    You may edit or delete the file in that location.""")
    st.write("To run your profile, select it in the Android Triage window under 'Triage Profile'.")

make_prof = st.button("Generate Profile")

list_profiles()

## Create a Profile ###
if make_prof == True:           #   Enforce investigator descriptions
    if len(prof_name) == 0:
        st.error("Profile Name is required")
    if len(prof_name) > 0:
        with open(pwd + '/Profiles/' + prof_name, 'w') as added_Profile:
            added_Profile.write('[Filenames]\n')
            if len(file_inputs) > 1:
                for line in file_inputs:
                    added_Profile.write(line)
            
            added_Profile.write('\n\n[Hashes]\n')
            for h in hash_inputs:
                added_Profile.write(h)
             
            added_Profile.write('\n\n[Keywords]\n')
            for h in keyword_inputs:
                added_Profile.write(h)

st.header("Default Report Fields")            
Last_Used = access_user_inputs()
inv = st.text_input("Investigator", Last_Used["Examiner"])
agency = st.text_input("Agency", Last_Used["Organization"])
selected_folder_path = Last_Used["Report Location"]
update_report_fields = st.button("Save Fields")
if update_report_fields == True:
    store_new_user_inputs(Last_Used)
col1, col2 = st.columns(2)
with col1:
    st.write("MITE Reports are located at: " + Last_Used["Report Location"])
with col2:
    
    folder_select_button = st.button("Select Report Location",)

if folder_select_button:
    selected_folder_path = select_folder()
    store_new_user_inputs(Last_Used)
    st.write("Report path is now:", selected_folder_path)

        

        
        