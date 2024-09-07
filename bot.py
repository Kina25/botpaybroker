import discord
from discord.ext import commands
from discord.ui import Button, View
import requests

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

PRODUCT_API_URL = 'http://localhost:5000/api/products'  # Atualize para o URL real
catalog = []  # Lista para armazenar o catálogo de produtos
cart = {}  # Dicionário para armazenar o carrinho dos usuários

class ProductView(View):
    def __init__(self, products):
        super().__init__()
        self.products = products

    @discord.ui.button(label="Adicionar ao Carrinho", style=discord.ButtonStyle.green, custom_id="add_to_cart")
    async def add_to_cart(self, button: discord.ui.Button, interaction: discord.Interaction):
        product_id = int(button.custom_id.split("_")[-1])
        user_id = interaction.user.id
        if user_id not in cart:
            cart[user_id] = []
        cart[user_id].append(self.products[product_id])
        await interaction.response.send_message(f"Produto adicionado ao carrinho!", ephemeral=True)

    @discord.ui.button(label="Ver Carrinho", style=discord.ButtonStyle.blurple, custom_id="view_cart")
    async def view_cart(self, button: discord.ui.Button, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id not in cart or not cart[user_id]:
            await interaction.response.send_message("Seu carrinho está vazio!", ephemeral=True)
            return

        cart_items = cart[user_id]
        cart_total = sum(item['price'] for item in cart_items)
        cart_list = '\n'.join([f"{item['name']} - {item['description']} - ${item['price']}" for item in cart_items])

        embed = discord.Embed(title="Seu Carrinho", description=f"Total: ${cart_total}", color=discord.Color.blue())
        embed.add_field(name="Itens:", value=cart_list, inline=False)
        embed.set_footer(text="Use os botões abaixo para atualizar ou remover itens.")

        view = View()
        view.add_item(Button(label="Remover Itens", style=discord.ButtonStyle.red, custom_id="remove_items"))

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="Remover Itens", style=discord.ButtonStyle.red, custom_id="remove_items")
    async def remove_items(self, button: discord.ui.Button, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id in cart and cart[user_id]:
            cart[user_id] = []  # Limpa o carrinho
            await interaction.response.send_message("Todos os itens foram removidos do carrinho!", ephemeral=True)
        else:
            await interaction.response.send_message("Seu carrinho já está vazio!", ephemeral=True)

@bot.event
async def on_ready():
    print(f'Bot {bot.user} está pronto!')

@bot.command(name='update_catalog')
async def update_catalog(ctx):
    """Atualiza o catálogo com os produtos da API."""
    response = requests.get(PRODUCT_API_URL)
    if response.status_code == 200:
        global catalog
        products = response.json()
        catalog = products  # Atualiza o catálogo com os produtos da API
        await ctx.send("Catálogo atualizado com sucesso!")
    else:
        await ctx.send("Falha ao atualizar o catálogo.")

@bot.command(name='show_catalog')
async def show_catalog(ctx):
    """Mostra o catálogo de produtos."""
    if not catalog:
        await ctx.send("O catálogo está vazio! Use `!update_catalog` para atualizar.")
        return

    embed = discord.Embed(title="Catálogo de Produtos", color=discord.Color.green())
    for index, product in enumerate(catalog):
        embed.add_field(name=f"{index + 1}. {product['name']}", value=f"{product['description']} - ${product['price']}", inline=False)

    view = ProductView(catalog)
    await ctx.send(embed=embed, view=view)

@bot.command(name='setup')
async def setup(ctx):
    """Envia um link para o formulário de configuração de produtos."""
    await ctx.send("Por favor, acesse o seguinte link para adicionar produtos ao catálogo: [Formulário de Produtos](http://localhost:5000)")

bot.run('MTI4MTc2ODI4MjY2MzI5MzAwMA.GYCvX3.VJFNrhcEKwCjZT1ySV9Q6iZ_2ohFA5ktpCuNi8')
