import configparser
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.adcreative import AdCreative
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

def create_campaign(ad_account, name, objective, status='PAUSED', special_ad_categories=None):
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

def create_ad_set(ad_account, campaign_id, name, daily_budget_cents, start_time, end_time=None):
    """
    Creates a new ad set in a campaign.
    https://developers.facebook.com/docs/marketing-api/reference/ad-campaign/
    """
    try:
        # A basic targeting spec. This can be greatly expanded.
        targeting = {
            'geo_locations': {'countries': ['US']},
        }

        params = {
            'name': name,
            'campaign_id': campaign_id,
            'daily_budget': daily_budget_cents,
            'start_time': start_time.isoformat(),
            'targeting': targeting,
            'optimization_goal': AdSet.OptimizationGoal.reach,
            'billing_event': AdSet.BillingEvent.impressions,
            'status': AdSet.Status.paused,
        }
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
