import discord
from discord.ext import commands
import yt_dlp as youtube_dl
from asyncio import Queue
import os
import aiohttp

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='%', intents=intents)

# Fila de músicas
music_queue = Queue()

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

async def play_next(ctx):
    if not music_queue.empty():
        url = await music_queue.get()
        await play_music(ctx, url)

async def search_youtube(query):
    """Realiza a pesquisa no YouTube e retorna o URL do primeiro resultado."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'default_search': 'ytsearch',  # Pesquisar no YouTube
        'quiet': True
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if 'entries' in info:
            return info['entries'][0]['webpage_url']
        else:
            return None

async def play_music(ctx, url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(title)s.%(ext)s',  # Define o nome do arquivo de saída
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            audio_file = f"{info['title']}.mp3"

            # Verificar se o arquivo de áudio foi criado
            if not os.path.exists(audio_file):
                await ctx.send(f"O arquivo de áudio {audio_file} não foi encontrado!")
                return

            # Logs para depuração
            print(f"Audio file: {audio_file}")

            # Tocar o áudio
            ffmpeg_options = "-loglevel panic -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
            audio_source = discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=audio_file, options=ffmpeg_options)
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
            ctx.voice_client.play(audio_source, after=lambda e: bot.loop.create_task(play_next(ctx)))

            await ctx.send(f"Tocando: {info['title']}")
    except Exception as e:
        await ctx.send(f"Ocorreu um erro: {str(e)}")
        print(f"Erro: {str(e)}")

@bot.command(name='play')
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        await ctx.send("Você precisa estar em um canal de voz para usar este comando.")
        return

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    # Pesquisa a música no YouTube
    url = await search_youtube(search)
    if url:
        await music_queue.put(url)
        if not ctx.voice_client.is_playing():
            await play_next(ctx)
    else:
        await ctx.send("Não foi possível encontrar a música.")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Desconectado do canal de voz.")
    else:
        await ctx.send("O bot não está em um canal de voz.")

@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Faixa pulada.")
    else:
        await ctx.send("Não há nenhuma faixa tocando no momento.")

# Função para detectar palavrões e frases específicas
@bot.event
async def on_message(message):
    # Ignora mensagens enviadas pelo bot
    if message.author == bot.user:
        return

    # Lista de palavrões
    palavroes = ["porra", "caralho", "pqp", "puta que pariu", "toma no cu", "buceta", "tnc", "filha de uma meretriz", "fudeu", "vai se foder", "fds", "vai se fode", "fdp", 
                 "puta", "puto", "arrumbado", "arrombada", "filho de uma vadia", "filho de uma vadia", "filho de uma prostituda", 
                 "filha de uma prostituta", "filho do lula", "filha do lula", "filho do bolsonaro", "filha do bolsonaro", "vsfd", "acefalo", "acefala", "demente", "burro", "burra", "indigente",
                   "preto", "preta", "macaco", "macaca"]

    # Verifica se a mensagem contém algum palavrão
    if any(palavra in message.content.lower() for palavra in palavroes):
        await message.channel.send("Olha a boca caralho!")

    # Verifica se a frase "cr7 é melhor doq messi" foi enviada
    if "cr7 é melhor doq messi" in message.content.lower():
        await message.channel.send("Falou bosta")

    # Verifica se a frase "merda" foi enviada
    if "merda" in message.content.lower():
        await message.channel.send("merda é o que sai de vc otário!")

    # Verifica se a frase "cala a boca" foi enviada
    if "cala boca" in message.content.lower():
        await message.channel.send("cala vc!")

    # Verifica se a frase "quer ser meu amigo" foi enviada
    if "quer ser meu amigo?" in message.content.lower():
        await message.channel.send("Eu quero")
    
    # Verifica se a frase "depende" foi enviada
    if "depende" in message.content.lower():
        await message.channel.send("então va pra casa do carvalho")
    
    # Garante que os outros comandos ainda funcionem
    await bot.process_commands(message)

bot.run('SEU TOKEN AQUI')
