import asyncio
import csv
import json
import re
import os 
import argparse
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

def clean_filename(name):
    # Convert to lower case and replace special characters with underscores
    return re.sub(r'[^a-z0-9]+', '_', name.lower())

async def scrape_spotify_playlist(url):
    print("Starting Playwright...")
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch() # remember headless=False if you want to see what its doing... 
        page = await browser.new_page()
        print(f"Navigating to {url}...")
        await page.goto(url)

        print("Waiting for playlist element to load...")
        try:
            await page.wait_for_selector('div[role="grid"][aria-label]', timeout=60000)
        except PlaywrightTimeoutError:
            print("Timeout: Playlist element not found.")
            await browser.close()
            return

        print("Finding playlist element...")
        playlist_element = await page.query_selector('div[role="grid"][aria-label]')
        
        if playlist_element:
            playlist_name = await playlist_element.get_attribute('aria-label')
            print(f"Playlist Name: {playlist_name}")
        else:
            print("Playlist element not found.")
            await browser.close()
            return

        print("Fetching song data...")
        song_data = []
        loaded_row_indices = set()
        last_song_count = 0
        same_count_iterations = 0

        # Select the first song element
        await page.focus('div[role="row"][aria-rowindex="2"]')
        print("Focusing on the first song...")

        while same_count_iterations < 25:  # Allow some iterations with no new songs to ensure all are loaded
            # TODO: this actually fails after a while, I suspect Spotify is stopping the scrape...
            song_elements = await page.query_selector_all('div[role="row"]')

            for song_element in song_elements:
                row_index = await song_element.get_attribute('aria-rowindex')
                if row_index and row_index not in loaded_row_indices:
                    loaded_row_indices.add(row_index)

                    play_button = await song_element.query_selector('button[aria-label^="Play "]')
                    if play_button:
                        aria_label = await play_button.get_attribute('aria-label')
                        if aria_label:
                            parts = aria_label.split(" by ")
                            if len(parts) == 2:
                                title = parts[0].replace("Play ", "").strip()
                                artist = parts[1].strip()
                                song_data.append({'title': title, 'artist': artist})
                                print(f"Fetched song - Title: {title}, Artist: {artist}")

            if len(song_elements) == last_song_count:
                same_count_iterations += 1
            else:
                same_count_iterations = 0

            last_song_count = len(song_elements)
            print("Pressing down to load more songs...")
            await page.keyboard.press('ArrowDown')
            await asyncio.sleep(0.01)  # Adjust sleep time as necessary

        print("Closing browser...")
        await browser.close()

        # Ensure the output directory exists
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        # Clean the playlist name for filenames
        cleaned_playlist_name = clean_filename(playlist_name)

        # Define the filenames with the output directory
        csv_filename = os.path.join(output_dir, f'{cleaned_playlist_name}.csv')
        json_filename = os.path.join(output_dir, f'{cleaned_playlist_name}.json')

        print(f"Writing data to {csv_filename}...")
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'artist']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for song in song_data:
                writer.writerow(song)

        print(f"Writing data to {json_filename}...")
        with open(json_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(song_data, jsonfile, indent=4)

def main():
    parser = argparse.ArgumentParser(description="Scrape Spotify playlist and save song data.")
    parser.add_argument('url', type=str, help='URL of the Spotify playlist')
    args = parser.parse_args()

    print("Running the async function...")
    asyncio.run(scrape_spotify_playlist(args.url))
    print("Script completed.")

if __name__ == '__main__':
    main()