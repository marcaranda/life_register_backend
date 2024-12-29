import re, requests

def get_url_data(url, code):
    if "strava.com" in url:
        id = extract_strava_id(url)
        token = get_strava_token(code)
        
        activity_url = f"https://www.strava.com/api/v3/activities/{id}"
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(activity_url, headers=headers)
        response.raise_for_status()
        
        stravaJson = response.json()
        stravaData = {
            "name" : stravaJson["name"],
            "distance" : stravaJson["distance"],
            "moving_time" : stravaJson["moving_time"],
            "type" : stravaJson["type"],
            "id" : stravaJson["id"],
            "start_date_local" : stravaJson["start_date_local"],
            "calories" : stravaJson["calories"],
            "start_date" : stravaJson["start_date"],
            "average_speed" : stravaJson["average_speed"],
            "splits_metric" : stravaJson["splits_metric"],
        }

        return stravaData
    
    else:
        return None

def extract_strava_id(stravaUrl):
    match = re.search(r"strava.com/activities/(\d+)", stravaUrl)
    if match:
        return match.group(1)  # Devuelve el ID de la actividad
    else:
        raise ValueError("URL de Strava no válida.")
    
def get_strava_token(code):
    CLIENT_ID = "142165"
    CLIENT_SECRET = "58b55e039725ca1a9d9cfcaff0e70fff0d707a00"

    token_url = "https://www.strava.com/oauth/token"
    response = requests.post(token_url, data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code'
    })

    response.raise_for_status()
    return response.json()['access_token']