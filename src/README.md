# MITE 

**What is MITE**

MITE is an Android preview tool designed to provide fast results related to specific file data and applications on a device.

**How MITE Works**

MITE issues requests via the Android Debugging Bridge (ADB) to collect information from the mobile device. The results of these requests can then be compared with information being sought by the investigator using "Profiles" containing search criteria like: file names, keywords, and/or MD5 hash values.

By default, MITE looks for device identifiers, wireless carrier information, file names, directory names, and installed applications. If the user chooses, it can gather image thumbnails and the MD5 hash values for media files (image and video). These elective actions will update timestamps on the target files.  

![alt text](https://user-images.githubusercontent.com/73806121/187032797-2f751d20-b915-404a-bc09-51e247705775.png)

**Running MITE**

To run the tool, unlock the target Android device.  Navigate to Settings. Under About Phone (or similar) locate the software Build Number and tap Build Number 7 times to become a Developer.  Return to the Settings menu and locate Developer Options.  Under Developer Options, enable Stay Awake and USB Debugging.

Connect the device to your workstation. You will be prompted by the device at some point to trust the attached computer.  Select "Always trust this computer" and approve the connection. This device/computer handshake may not take place until after starting MITE. If you have issues initiating the handshake, you can troubleshoot the connection by changing the USB connection method using Media Transfer Protocol (MTP) or Photo Transfer Protocol (PTP). These options are available under Developer Options under Default USB Configuration.   Another method to force the handshake is to disconnect the device, choose Revoke USB Debugging Authorizations under Developer Options, and reconnect the device via USB. (Just for clarity, connection issues are Android problems and not MITE problems 😀 )

The initial MITE window will allow you to enter case and investigator information, select modes of operation, and create case specific search profiles.    Case data input here will be used to create output directories and populate reports. The Case Name/Number field is the only required field.  

Profiles are intended to be case specific, but can be created in a manner that allows an investigator to create profiles for broader use. For example, a profile for narcotics terms could be created. The Profiles store file names, MD5 hashes, and keyword lists that will be compared with results collected from the target device. 

![alt text](https://user-images.githubusercontent.com/73806121/187036192-7383f42c-c386-453b-8491-2060c54371e4.png)

If a file name, MD5 value, or keyword from a Profile is found in data collected from the device, the user will be offered the option to create an Android backup of the device while the data is available.  The default password used for backups is "MITE".  The ADB backup will include shared storage space like an SD card, but remember this backup is limited and will not include major artifacts important in most examinations.  

MITE creates two report formats and they will both be present after each triage.  The first is a PDF report showing device identifiers, installed applications, and Profile hits. The next format can be found under the report directory "Raw Reports".  These reports are text files containing a listing of installed applications, a listing of all accessible/visible directories and file names, and, if selected, a list of all media file MD5 hash values. 

**What MITE is Not**

MITE is intended to be a very fast triage tool.  The goal is to provide device information in a couple of minutes which can help an investigator determine if a device is within the scope of their work.  It is not intended to be an extraction or analysis tool.  In fact, it was built to help determine which devices should make their way to those tools.  

Android protects user data by restricting ADB access using permissions. Some areas, like the "data/data" directory (the directory containing application data files), cannot be accessed using ADB due to these permission limitations.  This means MITE is a good option for a first review of a device, but reasonable investigative steps need to be applied as well to determine if a device is relevant to an investigation.   

This tool is best used for instances where the investigator is trying to determine what applications are being used, and what media files the user has stored on their device. 

Run the script from a folder containing: 

      MITE.py

      MITE_ADB.py

      MITE_Thumbs.py

      adb.exe

      AdbWinApi.dll

      AdbWinUsbApi.dll
  
  
  
Tips for success!
  
  On your phone. Enable USB debugging mode and choose "Stay Awake" in Developer Options.
  
  Keep device open and unlocked
  
  Keep vertical screen orientation or the backup method will require manual input.

This tool offers no guarantees or warranty. The operator/examiner assumes all risk and responsibility in its use.  Like any other tool used in relation to digital forensic work, MITE should be tested and validated prior to use. 
