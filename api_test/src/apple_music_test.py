import requests

# Requires authorization, presumably developer ID in particular. Didn't actually try to fix this.
# response = requests.get('https://api.music.apple.com/v1/catalog/ru/songs/900032829')
# print(response)

response = requests.get('https://itunes.apple.com/lookup?id=1553036783')
print(response)
print(response.json())

response = requests.get('https://itunes.apple.com/lookup?id=1553036788')
print(response)
print(response.json())

