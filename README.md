# Spotty-McScraperface

Spotty McScraperface is a command line Python tool that takes a public Spotify playlist and returns a json and csv of the songs and artists in that playlist.

### How do I use it?

Just invoke it via Python with a reference to the full spotify playlist URL... 

`python getplaylist.py '<playlist url>'`

e.g., 

`python getplaylist.py 'https://open.spotify.com/playlist/1lJDx1lqWkjnh8D7VITEhC?si=68096054aee34fad'`

### Why though?

I've been exploring LLMs versus recommender systems and this is an easy way for you to retrieve a bunch of songs/artists to find relevant and similar artists. 

If you're working with agents you could easily leverage this logic to have an agent recommend similar music based on a playlist. 

### What's in there?
The challenge is that Spotify's API is not so good so I'm chosing to use Playwright to access the site and try and trick the playlist to load. Spotify's javascript is pretty heavy so it wasn't as easy or quick to access the songs/artists. It'll likely break as Spotify's code base changes but this was a toy project anyway.

It's relevatively chill, I'm using:
* Playwright (we're navigating to the browser via a headless browser)
* Everything else is core Python
