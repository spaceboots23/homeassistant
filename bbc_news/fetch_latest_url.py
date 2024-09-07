import requests
from bs4 import BeautifulSoup

# Define the URL of the BBC episode list page
episode_list_url = 'https://www.bbc.co.uk/programmes/p002vsmz/episodes/player'

# Send a request to fetch the HTML content
response = requests.get(episode_list_url)
response.raise_for_status()  # Handle bad responses

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Find the first episode block
episode_block = soup.find('div', class_='programme--episode')

if episode_block:
    # Extract the episode PID
    data_pid = episode_block.get('data-pid')
    if data_pid:
        # Construct the URL for the episode page
        episode_page_url = f'https://www.bbc.co.uk/programmes/{data_pid}'
        
        # Fetch the episode page
        episode_response = requests.get(episode_page_url)
        episode_response.raise_for_status()
        
        # Parse the episode page
        episode_soup = BeautifulSoup(episode_response.text, 'html.parser')
        
        # Find the download link
        download_link = episode_soup.find('a', {'data-bbc-title': 'cta_download'})
        if download_link:
            download_url = download_link.get('href')
            download_url = f'https:{download_url}'  # Ensure the URL is absolute
            
            print(f'Download URL: {download_url}')
            
            # Home Assistant configuration
            home_assistant_url = 'http://localhost:8123'  # Ensure this URL matches Home Assistant instance (this assumes the script is run on the same host)
            long_lived_access_token = 'dont_ever_upload_your_token_publically'  # Replace with actual token

            headers = {
                'Authorization': f'Bearer {long_lived_access_token}',
                'Content-Type': 'application/json',
            }

            payload = {
                'state': download_url,
            }

            # Update the input_text entity in Home Assistant
            response = requests.post(
                f'{home_assistant_url}/api/states/input_text.latest_bbc_news_url',
                json=payload,
                headers=headers
            )

            if response.status_code == 200:
                print('URL successfully updated in Home Assistant')
            else:
                print(f'Failed to update URL: {response.content}')
        else:
            print('Download link not found.')
    else:
        print('Episode PID not found.')
else:
    print('Episode block not found.')
