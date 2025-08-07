# Meta Ad Creator

This is a simple Python tool to create Meta (Facebook) ad campaigns directly from the command line. It uses the Meta Business SDK for Python.

## ⚠️ Important Note

This tool requires you to have a Meta Developer account and an app with access to the Marketing API. It also requires you to manually generate an access token. **Never share your App Secret or Access Token with anyone.**

## 1. Installation

1.  Clone this repository or download the files.
2.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

## 2. Configuration: Getting Your Credentials

Before you can use the tool, you need to provide it with API credentials.

1.  **Copy the template:**
    ```bash
    cp config.ini.template config.ini
    ```
2.  **Edit `config.ini`** and fill in the following values. See the steps below for instructions on how to get each value.

### Step-by-Step Guide to Get Credentials

#### A. Create a Meta App

1.  Go to the [Meta for Developers](https://developers.facebook.com/apps/) page and click "Create App".
2.  Select "Business" as the app type.
3.  Follow the prompts to name your app and link it to your Business Manager account if you have one.

#### B. Get App ID and App Secret

1.  From your app's dashboard, go to **App Settings > Basic**.
2.  Your **App ID** and **App Secret** are displayed at the top of the page.
3.  Copy these values into your `config.ini` file.

#### C. Get Your Ad Account ID

1.  Go to your [Meta Ads Manager](https://www.facebook.com/ads/manager/).
2.  The URL in your browser will look something like this: `https://adsmanager.facebook.com/adsmanager/manage/campaigns?act=1234567890123456`.
3.  Your Ad Account ID is the number after `act=`. In this example, it's `1234567890123456`.
4.  Prefix it with `act_` and copy it into your `config.ini` file (e.g., `act_1234567890123456`).

#### D. Generate a Long-Lived User Access Token

This is the most critical step. You need to generate an access token that grants your app permission to manage ads on your behalf.

1.  Go to the [Graph API Explorer](https://developers.facebook.com/tools/explorer/).
2.  In the top-right corner, select the Meta App you just created.
3.  Below that, in the "User or Page" dropdown, select **"Get User Access Token"**.
4.  A popup will appear. In the "Permissions" list, find and check **`ads_management`**.
5.  Click **"Generate Access Token"**. You may need to re-enter your Facebook password.
6.  You will now have a short-lived access token. **We need to exchange this for a long-lived one.**
7.  Copy the short-lived token that was just generated.
8.  Go to the [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/).
9.  Paste your short-lived token into the input field and click "Debug".
10. Click the **"Extend Access Token"** button at the bottom. This will generate a new, long-lived token (valid for about 60 days).
11. **This is your final access token.** Copy this new, long-lived token into the `my_access_token` field in your `config.ini` file.

## 3. Usage

Once your `config.ini` is set up, you can run the application:

```bash
python main.py
```

Follow the on-screen prompts to create your campaign.
