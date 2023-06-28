import spotipy, asyncio, discord, os, json, math
from spotipy.oauth2 import SpotifyOAuth
from discord.ext import commands, tasks
from multiprocessing import Process
import random as r

os.environ['SPOTIPY_CLIENT_ID'] = '46fb8175ac7c47a9879392454ac6a915'
os.environ['SPOTIPY_CLIENT_SECRET'] = '969b1815e6dc45bf8b5579d410cc0ef4'
os.environ['SPOTIPY_REDIRECT_URI'] = 'https://127.0.0.1:41601'

scope = 'app-remote-control playlist-read-private user-modify-playback-state user-read-playback-state user-read-currently-playing user-library-read'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

bot_author = '0x01FE#1244'
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot("-", intents=intents)
bot.remove_command('help')

first_ready = True
playlist_list = ['goreshit i like ', 'Glitchbreak', 'sewerslvt i like', 'SnB', 'loli in early 20s i like', 'phonk i enjoy', 'daft punk i enjoy', 'yakui the maid i enjoy']
djing = False
sorted_songs = []
one = "1\N{variation selector-16}\N{combining enclosing keycap}"
two = "2\N{variation selector-16}\N{combining enclosing keycap}"
three = "3\N{variation selector-16}\N{combining enclosing keycap}"
four = "4\N{variation selector-16}\N{combining enclosing keycap}"

# events

@bot.event
async def on_ready(): #stuff for the bot to do when it boots up. (this command actually will run multiple times if the bot is up for a while)
	global first_ready
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')
	await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name="with Spotify API."))
	
# basic commands

async def ping(ctx): # ping!
	await ctx.send("Pong")
	print("pinged")

@bot.command()
@commands.is_owner()
async def shutdown(ctx): #shutdown command
    await ctx.bot.logout()


# bot commands

@bot.command()
@commands.is_owner()
async def devices(ctx): #get all current devices of user linked to the spotify api
	devices = sp.devices()
	await ctx.send(devices)
		
@bot.command()
@commands.is_owner()
async def next(ctx): #skip to next song in queue
	device_id = None
	devices_list = sp.devices()
	for device in devices_list['devices']:
		if device['type'] == 'Smartphone':
			device_id = device['id']
	sp.next_track(device_id=device_id)
	await ctx.send("Track skipped!")

@bot.command()
@commands.is_owner()
async def rewind(ctx): #rewind to the last song (doesn't actually work with a queue system.)
	device_id = None
	devices_list = sp.devices()
	for device in devices_list['devices']:
		if device['type'] == 'Smartphone':
			device_id = device['id']
	sp.previous_track(device_id=device_id)
	await ctx.send("What the hell is a rewind message supposed to look like?!")

@bot.command()
@commands.is_owner()
async def playlists(ctx): #scrape user playlists
	global playlist_list
	playlist_ids = {}
	playlists = sp.current_user_playlists(limit=50, offset=0)
	for playlist in playlists['items']:
		if playlist['name'] in playlist_list:
			playlist_ids[playlist['name']] = playlist['id']
	await ctx.send(playlist_ids) #export {"Playlist Name" : "Playlist ID"}
	
@bot.command()
@commands.is_owner()
async def test(ctx):
	now = sp.currently_playing() ## CHECK YOUR MESSAGE TO YOURSELF ON DISCORD
	print(now['is_playing'])
	
@bot.command()
@commands.is_owner()
async def dj(ctx):
	global djing
	if not djing:
		djing = True
		voting_loop.start(ctx)
		await ctx.send("DJing now!")
	else:
		djing = False
		voting_loop.stop()
	

async def get_uri(url):
		uri = sp.track(url)['uri']
		return uri
		
@bot.command()
async def queue(ctx, url):
	if url is None:
		await ctx.send("no URL was provided.")
	else:
		uri = await get_uri(url)
		track = sp.track(uri)
		if track['artists'][0]['name'] != "Kanye West":
			device_id = None 
			devices_list = sp.devices()
			for device in devices_list['devices']:
				if device['type'] == 'Smartphone':
					device_id = device['id']
			sp.add_to_queue(uri,device_id)
			await ctx.send(" has been added to the queue!")
		else:
			await ctx.send("Nice try.")

		

# utility methods

async def play(uri): # play a song by adding it to the queue and skipping
	device_id = None 
	devices_list = sp.devices()
	for device in devices_list['devices']:
		if device['type'] == 'Smartphone':
			device_id = device['id']
	sp.add_to_queue(uri,device_id)
	sp.next_track(device_id)
	track_info = sp.track(uri)
	
	
async def get_songs():
	## TRACK NAME, ARTIST NAMES, ID
	playlist_ids = await get_playlists()
	playlist_tracks = {}
	for playlist in playlist_ids:
		tracks = sp.playlist_tracks(playlist_ids[playlist])
		sorted_tracks = []
		for item2 in tracks['items']:
			item = item2['track'] ## shit code btw !?!?! FIX LATER ?!?!
			track_name = item['name']
			artist_names = []
			for artist in item['artists']:
				artist_names.append(artist['name'])
			track_uri = item['uri']
			sorted_tracks.append([track_name, artist_names, track_uri]) ## string, list, string / name , artist names , uri
		playlist_tracks[playlist] = sorted_tracks
	return playlist_tracks


async def get_playlists():
	global playlist_list
	playlist_ids = {}
	playlists = sp.current_user_playlists(limit=50, offset=0)
	for playlist in playlists['items']:
		if playlist['name'] in playlist_list:
			playlist_ids[playlist['name']] = playlist['id']
	return playlist_ids







# task loops

@tasks.loop(seconds=0.0,count=None)
async def voting_loop(ctx):
	global sorted_songs
	selected_songs = sorted_songs[r.randint(0,len(sorted_songs)-1)] # bellow is pretty ugly, might re-code later
	vote_message_content = f":musical_note: Vote for the next song! :musical_note:\n\t1. {selected_songs[0][0]} by {selected_songs[0][1][0]}\n\t2. {selected_songs[1][0]} by {selected_songs[1][1][0]}\n\t3. {selected_songs[2][0]} by {selected_songs[2][1][0]}\n\t4. {selected_songs[3][0]} by {selected_songs[3][1][0]}"
	vote_message = await ctx.send(vote_message_content)
	highest = 0
	name = None

	await vote_message.add_reaction(one)
	await vote_message.add_reaction(two)
	await vote_message.add_reaction(three)
	await vote_message.add_reaction(four)

	now_playing = sp.currently_playing()
	if now_playing['is_playing']:
		duration = now_playing['item']['duration_ms']
		progress = now_playing['progress_ms']

		last_playing = now_playing['item']['name']
		while True:
			now_playing = sp.currently_playing()
			if last_playing != now_playing['item']['name']:
				break
			await asyncio.sleep(5)
	
	channel = vote_message.channel
	refreshed_message = await channel.fetch_message(vote_message.id)

	for reaction in refreshed_message.reactions:
		if reaction.emoji == one:
			if reaction.count > highest:
				highest = reaction.count
				name = 0 # one lower than it should be so it works with the selected_songs array
		elif reaction.emoji == two:
			if reaction.count > highest:
				highest = reaction.count
				name = 1
		elif reaction.emoji == three:
			if reaction.count > highest:
				highest = reaction.count
				name = 2
		elif reaction.emoji == four:
			if reaction.count > highest:
				highest = reaction.count
				name = 3

	device_id = None 
	devices_list = sp.devices()
	for device in devices_list['devices']:
		if device['type'] == 'Smartphone':
			device_id = device['id']
	sp.add_to_queue(selected_songs[name][2],device_id) # play the winner then it all repeats


@voting_loop.before_loop
async def sort_songs(): # sort all the songs before the voting loop
	global sorted_songs
	unsorted_songs = await get_songs()
	songs = []
	for key in unsorted_songs:
		for song in unsorted_songs[key]:
			songs.append(song)
	for num in range(0,math.floor(len(songs)/4)): ## JANKY AS FUCK PROBABLY SHOULDN'T WORK
		temp_list = []
		for n in range(0,4):
			randnum = r.randint(0,len(songs)-1)
			temp_list.append(songs[randnum])
			songs.remove(songs[randnum])
		sorted_songs.append(temp_list) # sorted list is a 2d array of songs in groups of four containing the info [name , artist names , uri]



bot.run('')
