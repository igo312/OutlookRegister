import requests
def create_ads_profile(api_address):
    '''
    return: profile_id
    '''
    fingerprint_config = {
        'random_ua':{
            'ua_browser': ['chrome'],
            'ua_system_version': ['windows 10', 'Windows 11'],
        }
    }
    profile = {
        'group_id': '0',
        'proxyid': 'random',
        'fingerprint_config': fingerprint_config
    }
    api = '/api/v2/browser-profile/create'
    response = requests.post(api_address + api, json=profile)
    if response.status_code == 200:
        return response.json()["data"]["profile_id"]

def delete_ads_profile(api_address, profile_id:list[str]):
    if isinstance(profile_id, str):
        profile_id = [profile_id]
    api = '/api/v2/browser-profile/delete'
    response = requests.post(api_address + api, json={'profile_id': profile_id})
    return response.json()

def start_ads_profile(api_address, profile_id:str):
    api = '/api/v2/browser-profile/start'
    response = requests.post(api_address + api, json={'profile_id': profile_id})
    return response.json()

def stop_ads_profile(api_address, profile_id:str):
    api = '/api/v2/browser-profile/stop'
    response = requests.post(api_address + api, json={'profile_id': profile_id})
    return response.json()
