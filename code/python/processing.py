import requests

TEST_URL = 'http://www.pathofexile.com/api/public-stash-tabs'

if __name__ == "__main__":
    data = requests.get(TEST_URL)
    data = data.json())    

    next_change_id = data['next_change_id']
    print(next_change_id)
    print(data.keys())





