import configparser
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
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

def get_ad_account():
    """
    Returns the AdAccount object.
    """
    config = configparser.ConfigParser()
    config.read('config.ini')
    ad_account_id = config['META_API']['ad_account_id']
    return AdAccount(ad_account_id)

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
