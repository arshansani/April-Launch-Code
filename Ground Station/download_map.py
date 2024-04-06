import os
import requests
import math
import time

# Coordinates for Waco and Dallas
waco_coords = (31.5493, -97.1467)
dallas_coords = (32.7767, -96.7970)

# Zoom levels to download (adjust as needed)
min_zoom = 7
max_zoom = 15

# Tile server URL
tile_url = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"

# Function to convert coordinates to tile numbers
def coords_to_tile(lat, lon, zoom):
    x = math.floor((lon + 180) / 360 * (2 ** zoom))
    y = math.floor((1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * (2 ** zoom))
    return (x, y)

# Function to download a tile
def download_tile(url, tile_path, cache_expiry=14 * 24 * 60 * 60):  # Cache expiry in seconds (default: 14 days)
    os.makedirs(os.path.dirname(tile_path), exist_ok=True)
    if os.path.exists(tile_path):
        tile_age = time.time() - os.path.getmtime(tile_path)
        if tile_age < cache_expiry:
            return  # Tile is already cached and hasn't expired
    headers = {"User-Agent": "Ballooning Project GUI/1.0"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(tile_path, "wb") as file:
            file.write(response.content)
    else:
        print(f"Failed to download tile: {url}")
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.content}")

# Create the tiles directory if it doesn't exist
os.makedirs("tiles", exist_ok=True)

# Download tiles for Waco and Dallas
for coords in [waco_coords, dallas_coords]:
    for zoom in range(min_zoom, max_zoom + 1):
        x, y = coords_to_tile(coords[0], coords[1], zoom)
        
        # Download tiles within a square area around the coordinates
        area_size = 10  # Adjust the area size as needed
        for i in range(x - area_size, x + area_size + 1):
            for j in range(y - area_size, y + area_size + 1):
                tile_path = f"tiles/{zoom}/{i}/{j}.png"
                tile_url_formatted = tile_url.format(z=zoom, x=i, y=j)
                print(f"Downloading tile: {tile_url_formatted}")
                download_tile(tile_url_formatted, tile_path)

print("Tile download completed.")