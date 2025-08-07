import configparser
from facebook_business.api import FacebookAdsApi
import hashlib
import json
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.customaudience import CustomAudience
from facebook_business.adobjects.adimage import AdImage
from facebook_business.adobjects.advideo import AdVideo
from facebook_business.adobjects.page import Page
from facebook_business.adobjects.ad import Ad
from facebook_business.exceptions import FacebookRequestError

def initialize_api():
    """
    Initializes the Facebook Ads API with credentials from config.ini.
    """
    config = configparser.ConfigParser()
    config.read('config.ini')

    my_app_id = config['META_API']['my_app_id']
    my_app_secret = config['META_API']['my_app_secret']
    my_access_token = config['META_API']['my_access_token']

    FacebookAdsApi.init(my_app_id, my_app_secret, my_access_token)

def get_config():
    """
    Reads and returns the config object.
    """
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

def create_campaign(ad_account, name, objective, status='PAUSED', special_ad_categories=None, daily_budget=None):
    """
    Creates a new ad campaign.
    https://developers.facebook.com/docs/marketing-api/reference/ad-campaign-group#Creating
    """
    if special_ad_categories is None:
        special_ad_categories = []

    try:
        params = {
            'name': name,
            'objective': objective,
            'status': status,
            'special_ad_categories': special_ad_categories,
        }
        if daily_budget:
            params['daily_budget'] = daily_budget
            # When setting a campaign budget, this field is also required
            params['is_budget_optimization_active'] = True

        campaign = ad_account.create_campaign(params=params)
        print(f"Successfully created campaign '{name}'")
        print(f"  - Campaign ID: {campaign[Campaign.Field.id]}")
        return campaign
    except FacebookRequestError as e:
        print(f"Error creating campaign: {e}")
        print(f"  - Error Code: {e.api_error_code()}")
        print(f"  - Error Subcode: {e.api_error_subcode()}")
        print(f"  - Error Message: {e.api_error_message()}")
        return None

def get_campaigns(ad_account):
    """
    Fetches all campaigns in the ad account.
    """
    try:
        fields = [
            Campaign.Field.id,
            Campaign.Field.name,
            Campaign.Field.objective,
            Campaign.Field.status,
        ]
        campaigns = ad_account.get_campaigns(fields=fields)

        # Convert SDK objects to a list of dictionaries for easier handling
        campaign_list = [dict(c) for c in campaigns]

        return campaign_list
    except FacebookRequestError as e:
        print(f"Error getting campaigns: {e}")
        return None

def update_campaign(campaign_id, params):
    """
    Updates a campaign with the given parameters.
    """
    try:
        campaign = Campaign(campaign_id)
        campaign.remote_update(params=params)
        return True
    except FacebookRequestError as e:
        print(f"Error updating campaign {campaign_id}: {e}")
        return False

def delete_campaign(campaign_id):
    """
    Deletes a campaign.
    """
    try:
        campaign = Campaign(campaign_id)
        campaign.remote_delete()
        return True
    except FacebookRequestError as e:
        print(f"Error deleting campaign {campaign_id}: {e}")
        return False

def get_insights(object_id, object_type='campaign'):
    """
    Fetches insights for a given ad object (campaign, ad set, or ad).
    """
    try:
        fields = [
            'spend',
            'impressions',
            'clicks',
            'ctr', # Click-Through Rate
            'cpc', # Cost Per Click
        ]
        params = {
            'date_preset': 'last_7d',
        }

        if object_type == 'campaign':
            obj = Campaign(object_id)
        elif object_type == 'ad_set':
            obj = AdSet(object_id)
        elif object_type == 'ad':
            obj = Ad(object_id)
        else:
            raise ValueError(f"Unsupported object_type for insights: {object_type}")

        insights = obj.get_insights(fields=fields, params=params)

        if insights:
            # Insights usually return a list with one item for the summary
            return dict(insights[0])
        else:
            return {} # Return empty dict if no insights are available

    except FacebookRequestError as e:
        print(f"Error getting insights for {object_type} {object_id}: {e}")
        return None

def create_custom_audience_from_emails(ad_account, name, description, user_emails):
    """
    Creates a new custom audience from a list of emails.
    """
    try:
        # Step 1: Create the empty audience
        params = {
            'name': name,
            'description': description,
            'subtype': CustomAudience.Subtype.custom,
            'customer_file_source': CustomAudience.CustomerFileSource.user_provided_only,
        }
        audience = ad_account.create_custom_audience(params=params)
        print(f"Successfully created empty audience '{name}' with ID: {audience[CustomAudience.Field.id]}")

        # Step 2: Normalize and hash the emails
        hashed_emails = []
        for email in user_emails:
            normalized_email = email.strip().lower()
            hashed_email = hashlib.sha256(normalized_email.encode('utf-8')).hexdigest()
            hashed_emails.append(hashed_email)

        # Step 3: Add users to the audience
        audience.add_users(
            schema=CustomAudience.Schema.email_sha256,
            users=hashed_emails
        )
        print(f"Successfully added {len(hashed_emails)} users to audience '{name}'.")

        return audience[CustomAudience.Field.id]

    except FacebookRequestError as e:
        print(f"Error creating custom audience: {e}")
        return None

def upload_image(ad_account, image_path):
    """
    Uploads an image to the ad account's library and returns the image hash.
    """
    try:
        params = {
            AdImage.Field.filename: image_path,
        }
        image = ad_account.create_ad_image(params=params)
        image_hash = image[AdImage.Field.hash]
        print(f"Successfully uploaded image. Hash: {image_hash}")
        return image_hash
    except FacebookRequestError as e:
        print(f"Error uploading image: {e}")
        return None

def upload_video(ad_account, video_path):
    """
    Uploads a video to the ad account's library and returns the video ID.
    """
    try:
        video = ad_account.create_ad_video(
            params={
                AdVideo.Field.filepath: video_path,
            }
        )
        video.remote_read(fields=[AdVideo.Field.id, AdVideo.Field.status])
        # Wait for the video to be processed
        video.waitUntilEncodingReady()
        video_id = video[AdVideo.Field.id]
        print(f"Successfully uploaded and processed video. ID: {video_id}")
        return video_id
    except FacebookRequestError as e:
        print(f"Error uploading video: {e}")
        return None

def create_lead_form(page_id, name, questions):
    """
    Creates a new Lead Generation Form for a given Page.
    https://developers.facebook.com/docs/marketing-api/guides/lead-ads/forms-questions
    """
    try:
        page = Page(page_id)
        params = {
            'name': name,
            'questions': json.dumps(questions), # Questions need to be a JSON string
            'privacy_policy': {
                'url': 'https://www.facebook.com/privacy/policy', # A placeholder privacy policy is required
                'link_text': 'Privacy Policy'
            }
        }
        form = page.create_lead_gen_form(params=params)
        form_id = form[Page.Field.id]
        print(f"Successfully created lead form '{name}' with ID: {form_id}")
        return form_id
    except FacebookRequestError as e:
        print(f"Error creating lead form: {e}")
        return None

def create_lead_ad_creative(ad_account, name, page_id, message, image_hash, lead_gen_form_id):
    """
    Creates a special ad creative for a Lead Ad.
    """
    try:
        link_data = {
            'link': 'http://fb.me/', # Required for lead ads
            'message': message,
            'image_hash': image_hash,
            'call_to_action': {
                'type': 'SIGN_UP',
                'value': {
                    'lead_gen_form_id': lead_gen_form_id,
                }
            }
        }
        object_story_spec = {
            'page_id': page_id,
            'link_data': link_data,
        }
        params = {
            'name': name,
            'object_story_spec': object_story_spec,
        }
        creative = ad_account.create_ad_creative(params=params)
        print(f"Successfully created lead ad creative '{name}'")
        print(f"  - Ad Creative ID: {creative[AdCreative.Field.id]}")
        return creative
    except FacebookRequestError as e:
        print(f"Error creating lead ad creative: {e}")
        return None

def create_video_ad_creative(ad_account, name, page_id, message, video_id, thumbnail_url=None):
    """
    Creates a new video ad creative.
    """
    try:
        video_data = {
            'video_id': video_id,
            'message': message,
            'title': name, # Use the creative name as the title
            'call_to_action': {'type': 'WATCH_MORE'}, # A generic CTA
        }
        if thumbnail_url:
            video_data['image_url'] = thumbnail_url

        object_story_spec = {
            'page_id': page_id,
            'video_data': video_data,
        }
        params = {
            'name': name,
            'object_story_spec': object_story_spec,
        }
        creative = ad_account.create_ad_creative(params=params)
        print(f"Successfully created video ad creative '{name}'")
        print(f"  - Ad Creative ID: {creative[AdCreative.Field.id]}")
        return creative
    except FacebookRequestError as e:
        print(f"Error creating video ad creative: {e}")
        return None

def create_ad(ad_account, ad_set_id, creative_id, name):
    """
    Creates a new ad, linking an ad set and a creative.
    """
    try:
        params = {
            'name': name,
            'adset_id': ad_set_id,
            'creative': {'creative_id': creative_id},
            'status': Ad.Status.paused,
        }
        ad = ad_account.create_ad(params=params)
        print(f"Successfully created ad '{name}'")
        print(f"  - Ad ID: {ad[Ad.Field.id]}")
        return ad
    except FacebookRequestError as e:
        print(f"Error creating ad: {e}")
        print(f"  - Error Code: {e.api_error_code()}")
        print(f"  - Error Subcode: {e.api_error_subcode()}")
        print(f"  - Error Message: {e.api_error_message()}")
        return None

def create_ad_creative(ad_account, page_id, name, image_hash, link, message):
    """
    Creates a new ad creative.
    https://developers.facebook.com/docs/marketing-api/reference/ad-creative/
    """
    try:
        object_story_spec = {
            'page_id': page_id,
            'link_data': {
                'image_hash': image_hash,
                'link': link,
                'message': message,
            },
        }
        params = {
            'name': name,
            'object_story_spec': object_story_spec,
        }
        creative = ad_account.create_ad_creative(params=params)
        print(f"Successfully created ad creative '{name}'")
        print(f"  - Ad Creative ID: {creative[AdCreative.Field.id]}")
        return creative
    except FacebookRequestError as e:
        print(f"Error creating ad creative: {e}")
        print(f"  - Error Code: {e.api_error_code()}")
        print(f"  - Error Subcode: {e.api_error_subcode()}")
        print(f"  - Error Message: {e.api_error_message()}")
        return None

def create_ad_set(ad_account, campaign_id, name, daily_budget_cents, start_time, optimization_goal, targeting_spec, end_time=None):
    """
    Creates a new ad set in a campaign.
    https://developers.facebook.com/docs/marketing-api/reference/ad-campaign/
    """
    try:
        params = {
            'name': name,
            'campaign_id': campaign_id,
            'daily_budget': daily_budget_cents,
            'start_time': start_time.isoformat(),
            'targeting': targeting_spec,
            'optimization_goal': optimization_goal,
            'billing_event': AdSet.BillingEvent.impressions,
            'status': AdSet.Status.paused,
        }

        # Special parameters for Lead Ads
        if optimization_goal == 'LEAD_GENERATION':
            config = get_config()
            params['promoted_object'] = {'page_id': config['META_API']['page_id']}
            params['destination_type'] = 'ON_AD'


        if end_time:
            params['end_time'] = end_time.isoformat()

        ad_set = ad_account.create_ad_set(params=params)
        print(f"Successfully created ad set '{name}'")
        print(f"  - Ad Set ID: {ad_set[AdSet.Field.id]}")
        return ad_set
    except FacebookRequestError as e:
        print(f"Error creating ad set: {e}")
        print(f"  - Error Code: {e.api_error_code()}")
        print(f"  - Error Subcode: {e.api_error_subcode()}")
        print(f"  - Error Message: {e.api_error_message()}")
        return None
