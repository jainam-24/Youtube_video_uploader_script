Certainly! Below is the provided text converted into Markdown format:

```markdown
1. **Create a YouTube Channel**
   - Head over to YouTube and create a new channel if you haven't already.

2. **Generate OAuth Credentials**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Select "APIs & Services" from the navigation menu.
   - Click on "Credentials" and then "Create credentials".
   - Choose "OAuth client ID".

3. **Configure OAuth Consent Screen**
   - Select "External" under "User type".
   - In "App information", provide an application name and a valid email address for user support.
   - Under "Authorized domains", add "youtube.com".
     - App Domain:
     - Application Homepage: Enter "https://www.youtube.com/"
     - Optional:
       - Application Privacy Policy: If you have a privacy policy for your application, provide the URL here.

4. **Define Developer Contact Information**
   - Provide a valid email address for the developer contact.

5. **Set Up Scopes**
   - Click on "Add scope" and enter the following URLs one by one:
     - `https://www.googleapis.com/auth/youtube`
     - `https://www.googleapis.com/auth/youtube.force-ssl`
     - `https://www.googleapis.com/auth/youtube.upload`
     - `https://www.googleapis.com/auth/youtube.readonly`
   - In "How these scopes will be used", explain that these scopes are required to upload videos to YouTube programmatically using scripts instead of manual uploads.
   - (Optional) Provide a demo video URL in the "Demo video" section. You can use this link: [Demo Video](https://www.youtube.com/watch?v=Pr0tC-6hh44)

6. **Create OAuth Client ID**
   - Go to the credentials page and create an OAuth client ID.
   - Choose "Application Type - Desktop" and create the client ID.

7. **OAuth Consent Screen Summary**
   - Go to the OAuth consent screen and review the summary.

8. **Prepare for Verification**
   - Select "prepare for verification" and save your changes.
   - Continue with any additional steps required for verification.

9. **Download OAuth 2.0 Client ID**
   - Go to the credentials page and download the OAuth 2.0 Client ID you created.

10. **Organize Files**
    - Keep the downloaded OAuth 2.0 Client ID file in the folder containing all your `.py` files.

11. **Update Configuration**
    - Write the name of the file (OAuth 2.0 Client ID) in your `config.py`.
```
