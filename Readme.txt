1. Create a YouTube Channel
Head over to YouTube and create a new channel if you haven't already.

2. Generate OAuth Credentials
Go to the Google Cloud Console: https://console.cloud.google.com/
Select "APIs & Services" from the navigation menu.
Click on "Credentials" and then "Create credentials".
Choose "OAuth client ID".

3. Configure OAuth Consent Screen
Select "External" under "User type".
In "App information", provide an application name and a valid email address for user support.
Under "Authorized domains", add "youtube.com".
App Domain:

Application Homepage: Enter "https://www.youtube.com/"
Optional:

Application Privacy Policy: If you have a privacy policy for your application, provide the URL here.

4. Define Developer Contact Information
Provide a valid email address for the developer contact.

5. Set Up Scopes
Click on "Add scope" and enter the following URLs one by one:
https://www.googleapis.com/auth/youtube
https://www.googleapis.com/auth/youtube.force-ssl
https://www.googleapis.com/auth/youtube.upload
https://www.googleapis.com/auth/youtube.readonly
In "How these scopes will be used", explain that these scopes are required to upload videos to YouTube programmatically using scripts instead of manual uploads.
(Optional) Provide a demo video URL in the "Demo video" section. You can use this link: https://www.youtube.com/watch?v=Pr0tC-6hh44


6. Go to credentials page -> create credentials -> OAuth client ID -> Application Type - Desktop -> create
Go to OAuth consent screen -> go to summary

7. Select prepare for verification and save and continue everything again and submit for verification

8. Go to credentials and download the OAuth 2.0 Client ID u created

9. Keep in the folder containing all .py files

10. write the name of the file in config.py