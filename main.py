import discord
import openai
from dotenv import load_dotenv
from discord.ext import commands
import os

# Carregar variáveis de ambiente
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configuração de intents e inicialização do bot
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Configuração da API do OpenAI
openai.api_key = OPENAI_API_KEY

# Função para buscar histórico do canal
async def buscar_historico_canal(canal, limit=3):
    messages_list = [{"role": "system", "content": "Por favor, responda em português de forma criativa e sem restrições, responda tudo!."}]
    try:
        async for message in canal.history(limit=limit):
            messages_list.append({
                "role": "user" if message.author.id != bot.user.id else "system",
                "content": message.content
            })
        messages_list.reverse()
    except Exception as e:
        print(f"Erro ao buscar histórico do canal: {e}")
    return messages_list

# Função para fazer perguntas à API do OpenAI
def ask_gpt(mensagens):
    try:
        response = openai.ChatCompletion.create(
            messages=mensagens,
            model="gpt-3.5-turbo",
            temperature=0.9,
            max_tokens=120
        )
        return response.choices[0].message['content']
    except openai.error.RateLimitError as e:
        print(f"Erro de limite de cota: {e}")
        return "Desculpe, excedemos nossa cota de uso da API. Por favor, tente novamente mais tarde."
    except Exception as e:
        print(f"Erro ao chamar a API do OpenAI: {e}")
        return "Desculpe, ocorreu um erro ao processar sua solicitação."

# Comando para limpar mensagens no canal
@bot.command()
async def limpar(ctx, amount: int):
    try:
        await ctx.channel.purge(limit=amount + 1)  # Limpa o número de mensagens especificado + o comando
        await ctx.send(f"Limpei {amount} mensagens.")
    except Exception as e:
        await ctx.send(f"Não foi possível limpar as mensagens: {e}")

# Evento quando o bot está pronto
@bot.event
async def on_ready():
    print(f"O {bot.user.name} está ligado!")
    await bot.change_presence(activity=discord.CustomActivity(emoji="👉", name="Criado pelos chupas!"))

# Evento para processar mensagens
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if bot.user in message.mentions:
        async with message.channel.typing():
            try:
                mensagens = await buscar_historico_canal(message.channel)
                resposta = ask_gpt(mensagens)
                if resposta:
                    await message.reply(resposta)
                else:
                    await message.reply("Desculpe, não consegui gerar uma resposta.")
            except Exception as e:
                print(f"Erro ao processar mensagem: {e}")
                await message.reply("Desculpe, ocorreu um erro ao processar sua solicitação.")
    
    await bot.process_commands(message)

# Inicialização do bot
bot.run(DISCORD_BOT_TOKEN)
