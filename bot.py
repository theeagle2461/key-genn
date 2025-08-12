import discord
from discord.ext import commands
import json
import uuid
import time
import datetime
import asyncio
import os
import requests
from typing import Optional, Dict, List
import aiofiles

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Enable slash commands
bot.tree = discord.app_commands.CommandTree(bot)

# Configuration
GUILD_ID = 1402622761246916628
ROLE_ID = 1404221578782183556
ADMIN_ROLE_ID = 1402650246538072094  # Role that can manage keys
BOT_TOKEN = "MTQwNDUzMzQ5MDEwNzY4MjgzNg.G-eh7N.U7vZyJaEScHE-81IHtYqhYFpfm_V6pR3yo8De8"  # Replace with your actual bot token

# Special admin user IDs for key generation and management
SPECIAL_ADMIN_IDS = [485182079923912734, 485182079923912734]  # Add both user IDs here

# Webhook configuration for key notifications and selfbot launches
WEBHOOK_URL = "https://discord.com/api/webhooks/1404537582804668619/6jZeEj09uX7KapHannWnvWHh5a3pSQYoBuV38rzbf_rhdndJoNreeyfFfded8irbccYB"
CHANNEL_ID = 1404537582804668619  # Channel ID from webhook

# Data storage
KEYS_FILE = "keys.json"
BACKUP_FILE = "keys_backup.json"
USAGE_FILE = "key_usage.json"

class KeyManager:
    def __init__(self):
        self.keys = {}
        self.key_usage = {}
        self.load_data()
    
    def load_data(self):
        """Load keys and usage data from files"""
        try:
            if os.path.exists(KEYS_FILE):
                with open(KEYS_FILE, 'r') as f:
                    self.keys = json.load(f)
            
            if os.path.exists(USAGE_FILE):
                with open(USAGE_FILE, 'r') as f:
                    self.key_usage = json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
            self.keys = {}
            self.key_usage = {}
    
    def save_data(self):
        """Save keys and usage data to files"""
        try:
            with open(KEYS_FILE, 'w') as f:
                json.dump(self.keys, f, indent=2)
            
            with open(USAGE_FILE, 'w') as f:
                json.dump(self.key_usage, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def generate_key(self, user_id: int, channel_id: Optional[int] = None, duration_days: int = 30) -> str:
        """Generate a new key for a user"""
        key = str(uuid.uuid4())
        activation_time = int(time.time())
        expiration_time = activation_time + (duration_days * 24 * 60 * 60)
        
        self.keys[key] = {
            "user_id": user_id,
            "channel_id": channel_id,
            "activation_time": activation_time,
            "expiration_time": expiration_time,
            "duration_days": duration_days,  # Store duration for SelfBot
            "is_active": True,
            "machine_id": None,
            "activated_by": None,
            "created_by": user_id
        }
        
        self.key_usage[key] = {
            "created": activation_time,
            "activated": None,
            "last_used": None,
            "usage_count": 0
        }
        
        self.save_data()
        return key
    
    def revoke_key(self, key: str) -> bool:
        """Revoke a key"""
        if key in self.keys:
            self.keys[key]["is_active"] = False
            self.save_data()
            return True
        return False
    
    def activate_key(self, key: str, machine_id: str, user_id: int) -> Dict:
        """Activate a key for a specific machine"""
        if key not in self.keys:
            return {"success": False, "error": "Invalid key"}
        
        key_data = self.keys[key]
        
        if not key_data["is_active"]:
            return {"success": False, "error": "Key has been revoked"}
        
        if key_data["machine_id"] and key_data["machine_id"] != machine_id:
            return {"success": False, "error": "Key is already activated on another machine"}
        
        if key_data["expiration_time"] < int(time.time()):
            return {"success": False, "error": "Key has expired"}
        
        # Activate the key
        key_data["machine_id"] = machine_id
        key_data["activated_by"] = user_id
        key_data["activated"] = int(time.time())
        
        # Update usage
        if key in self.key_usage:
            self.key_usage[key]["activated"] = int(time.time())
            self.key_usage[key]["last_used"] = int(time.time())
            self.key_usage[key]["usage_count"] += 1
        
        self.save_data()
        
        return {
            "success": True,
            "expiration_time": key_data["expiration_time"],
            "channel_id": key_data["channel_id"]
        }
    
    def get_key_info(self, key: str) -> Optional[Dict]:
        """Get information about a key"""
        if key in self.keys:
            key_data = self.keys[key].copy()
            if key in self.key_usage:
                key_data.update(self.key_usage[key])
            return key_data
        return None
    
    def get_user_keys(self, user_id: int) -> List[Dict]:
        """Get all keys for a specific user"""
        user_keys = []
        for key, data in self.keys.items():
            if data["created_by"] == user_id:
                key_info = data.copy()
                if key in self.key_usage:
                    key_info.update(self.key_usage[key])
                user_keys.append({"key": key, **key_info})
        return user_keys
    
    def backup_keys(self) -> str:
        """Create a backup of all keys"""
        backup_data = {
            "timestamp": int(time.time()),
            "keys": self.keys,
            "usage": self.key_usage
        }
        
        with open(BACKUP_FILE, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        return BACKUP_FILE
    
    def restore_from_backup(self, backup_file: str) -> bool:
        """Restore keys from a backup file"""
        try:
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
            
            self.keys = backup_data.get('keys', {})
            self.key_usage = backup_data.get('key_usage', {})
            self.save_data()
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
    
    def generate_bulk_keys(self, daily_count: int, weekly_count: int, monthly_count: int, lifetime_count: int) -> Dict:
        """Generate multiple keys of different types"""
        generated_keys = {
            "daily": [],
            "weekly": [],
            "monthly": [],
            "lifetime": []
        }
        
        # Generate daily keys (1 day)
        for _ in range(daily_count):
            key = str(uuid.uuid4())
            activation_time = int(time.time())
            expiration_time = activation_time + (1 * 24 * 60 * 60)  # 1 day
            
            self.keys[key] = {
                "user_id": 0,  # 0 means unassigned
                "channel_id": None,
                "activation_time": activation_time,
                "expiration_time": expiration_time,
                "duration_days": 1,
                "key_type": "daily",
                "is_active": True,
                "machine_id": None,
                "activated_by": None,
                "created_by": 0
            }
            
            self.key_usage[key] = {
                "created": activation_time,
                "activated": None,
                "last_used": None,
                "usage_count": 0
            }
            
            generated_keys["daily"].append(key)
        
        # Generate weekly keys (7 days)
        for _ in range(weekly_count):
            key = str(uuid.uuid4())
            activation_time = int(time.time())
            expiration_time = activation_time + (7 * 24 * 60 * 60)  # 7 days
            
            self.keys[key] = {
                "user_id": 0,  # 0 means unassigned
                "channel_id": None,
                "activation_time": activation_time,
                "expiration_time": expiration_time,
                "duration_days": 7,
                "key_type": "weekly",
                "is_active": True,
                "machine_id": None,
                "activated_by": None,
                "created_by": 0
            }
            
            self.key_usage[key] = {
                "created": activation_time,
                "activated": None,
                "last_used": None,
                "usage_count": 0
            }
            
            generated_keys["weekly"].append(key)
        
        # Generate monthly keys (30 days)
        for _ in range(monthly_count):
            key = str(uuid.uuid4())
            activation_time = int(time.time())
            expiration_time = activation_time + (30 * 24 * 60 * 60)  # 30 days
            
            self.keys[key] = {
                "user_id": 0,  # 0 means unassigned
                "channel_id": None,
                "activation_time": activation_time,
                "expiration_time": expiration_time,
                "duration_days": 30,
                "key_type": "monthly",
                "is_active": True,
                "machine_id": None,
                "activated_by": None,
                "created_by": 0
            }
            
            self.key_usage[key] = {
                "created": activation_time,
                "activated": None,
                "last_used": None,
                "usage_count": 0
            }
            
            generated_keys["monthly"].append(key)
        
        # Generate lifetime keys (365 days = 1 year)
        for _ in range(lifetime_count):
            key = str(uuid.uuid4())
            activation_time = int(time.time())
            expiration_time = activation_time + (365 * 24 * 60 * 60)  # 365 days
            
            self.keys[key] = {
                "user_id": 0,  # 0 means unassigned
                "channel_id": None,
                "activation_time": activation_time,
                "expiration_time": expiration_time,
                "duration_days": 365,
                "key_type": "lifetime",
                "is_active": True,
                "machine_id": None,
                "activated_by": None,
                "created_by": 0
            }
            
            self.key_usage[key] = {
                "created": activation_time,
                "activated": None,
                "last_used": None,
                "usage_count": 0
            }
            
            generated_keys["lifetime"].append(key)
        
        self.save_data()
        return generated_keys
    
    def get_available_keys_by_type(self) -> Dict:
        """Get all available (unassigned) keys grouped by type"""
        available_keys = {
            "daily": [],
            "weekly": [],
            "monthly": [],
            "lifetime": []
        }
        
        for key, data in self.keys.items():
            if data["is_active"] and data["user_id"] == 0:  # Unassigned and active
                key_type = data.get("key_type", "unknown")
                if key_type in available_keys:
                    available_keys[key_type].append({
                        "key": key,
                        "created": data["activation_time"],
                        "expires": data["expiration_time"]
                    })
        
        return available_keys
    
    async def send_webhook_notification(self, key: str, user_id: int, machine_id: str):
        """Send webhook notification when a key is activated"""
        try:
            if not WEBHOOK_URL or WEBHOOK_URL == "YOUR_WEBHOOK_URL_HERE":
                return
            
            embed = {
                "title": "🔑 Key Activated",
                "color": 0x00ff00,
                "fields": [
                    {
                        "name": "Key",
                        "value": f"`{key}`",
                        "inline": True
                    },
                    {
                        "name": "User ID",
                        "value": f"<@{user_id}>",
                        "inline": True
                    },
                    {
                        "name": "Machine ID",
                        "value": f"`{machine_id}`",
                        "inline": True
                    },
                    {
                        "name": "Activation Time",
                        "value": f"<t:{int(time.time())}:F>",
                        "inline": False
                    }
                ],
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
            
            payload = {
                "embeds": [embed]
            }
            
            response = requests.post(WEBHOOK_URL, json=payload)
            if response.status_code != 204:
                print(f"Failed to send webhook notification: {response.status_code}")
                
        except Exception as e:
            print(f"Error sending webhook notification: {e}")

# Initialize key manager
key_manager = KeyManager()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Game(name="Managing Keys | /help"))
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="help", description="Show help information")
async def help_command(interaction: discord.Interaction):
    """Show help information"""
    if not await check_permissions(interaction):
        return
    
    embed = discord.Embed(
        title="🔑 Key Management Bot Help",
        description="Commands for managing Discord keys",
        color=0x2d6cdf
    )
    
    commands_info = {
        "/generate [@user] [channel_id] [days]": "Generate a new key for a user",
        "/activate [key]": "Activate a key and get the user role",
        "/sync [key]": "Sync key duration with SelfBot",
        "/revoke [key]": "Revoke a specific key",
        "/keys [@user]": "Show all keys for a user",
        "/info [key]": "Get detailed information about a key",
        "/backup": "Create a backup of all keys",
        "/restore [backup_file]": "Restore keys from backup",
        "/status": "Show bot status and statistics",
        "/generatekeys [daily] [weekly] [monthly] [lifetime]": "🔒 Generate bulk keys (Special Admin Only)",
        "/viewkeys": "🔒 View available keys by type (Special Admin Only)"
    }
    
    for cmd, desc in commands_info.items():
        embed.add_field(name=cmd, value=desc, inline=False)
    
    embed.set_footer(text="Only users with the required role can use these commands")
    await interaction.response.send_message(embed=embed)

async def check_permissions(interaction) -> bool:
    """Check if user has permission to use bot commands"""
    if not interaction.guild:
        await interaction.response.send_message("❌ This bot can only be used in a server.", ephemeral=True)
        return False
    
    if interaction.guild.id != GUILD_ID:
        await interaction.response.send_message("❌ This bot is not configured for this server.", ephemeral=True)
        return False
    
    member = interaction.guild.get_member(interaction.user.id)
    if not member:
        await interaction.response.send_message("❌ Unable to verify your permissions.", ephemeral=True)
        return False
    
    if ADMIN_ROLE_ID not in [role.id for role in member.roles]:
        await interaction.response.send_message("❌ You don't have permission to use this bot.", ephemeral=True)
        return False
    
    return True

@bot.tree.command(name="generate", description="Generate a new key for a user")
async def generate_key(interaction: discord.Interaction, user: discord.Member, channel_id: Optional[int] = None, duration_days: int = 30):
    """Generate a new key for a user"""
    if not await check_permissions(interaction):
        return
    
    if duration_days < 1 or duration_days > 365:
        await interaction.response.send_message("❌ Duration must be between 1 and 365 days.", ephemeral=True)
        return
    
    # Generate the key
    key = key_manager.generate_key(user.id, channel_id, duration_days)
    
    # Create embed
    embed = discord.Embed(
        title="🔑 New Key Generated",
        color=0x00ff00
    )
    
    embed.add_field(name="User", value=f"{user.mention} ({user.display_name})", inline=False)
    embed.add_field(name="Key", value=f"`{key}`", inline=False)
    embed.add_field(name="Duration", value=f"{duration_days} days", inline=True)
    embed.add_field(name="Expires", value=f"<t:{int(time.time()) + (duration_days * 24 * 60 * 60)}:R>", inline=True)
    
    if channel_id:
        embed.add_field(name="Channel Locked", value=f"<#{channel_id}>", inline=True)
    
    embed.set_thumbnail(url=user.display_avatar.url if user.display_avatar else None)
    embed.set_footer(text=f"Generated by {interaction.user.display_name}")
    
    # Send to channel and DM to user
    await interaction.response.send_message(embed=embed)
    
    try:
        dm_embed = discord.Embed(
            title="🔑 Your New Key",
            description=f"You have been given a new Discord key by {interaction.user.display_name}",
            color=0x00ff00
        )
        dm_embed.add_field(name="Key", value=f"`{key}`", inline=False)
        dm_embed.add_field(name="Duration", value=f"{duration_days} days", inline=True)
        dm_embed.add_field(name="Expires", value=f"<t:{int(time.time()) + (duration_days * 24 * 60 * 60)}:R>", inline=True)
        
        if channel_id:
            dm_embed.add_field(name="Channel Locked", value=f"<#{channel_id}>", inline=True)
        
        await user.send(embed=dm_embed)
    except:
        await interaction.followup.send("⚠️ Could not send DM to user. They may have DMs disabled.", ephemeral=True)

@bot.tree.command(name="activate", description="Activate a key and get the user role")
async def activate_key(interaction: discord.Interaction, key: str):
    """Activate a key and assign the user role"""
    try:
        # Get machine ID (using user's ID as a simple identifier)
        machine_id = str(interaction.user.id)
        user_id = interaction.user.id
        
        # Attempt to activate the key
        result = key_manager.activate_key(key, machine_id, user_id)
        
        if result["success"]:
            # Give the user the role
            role = interaction.guild.get_role(ROLE_ID)
            if role and role not in interaction.user.roles:
                await interaction.user.add_roles(role)
                role_message = f"✅ Role **{role.name}** has been assigned to you!"
            else:
                role_message = f"✅ You already have the **{role.name}** role!"
            
            # Get key duration info
            key_data = key_manager.get_key_info(key)
            duration_days = key_data.get("duration_days", 30)
            
            # Send success message
            embed = discord.Embed(
                title="🔑 Key Activated Successfully!",
                description=f"Your key has been activated and you now have access to the selfbot.",
                color=0x00ff00
            )
            embed.add_field(name="Role Assigned", value=role_message, inline=False)
            embed.add_field(name="Duration", value=f"{duration_days} days", inline=True)
            embed.add_field(name="Expires", value=f"<t:{result['expiration_time']}:R>", inline=True)
            
            if result.get('channel_id'):
                embed.add_field(name="Channel Locked", value=f"<#{result['channel_id']}>", inline=True)
            
            # Add SelfBot instructions
            embed.add_field(name="📱 SelfBot Setup", value=f"Use this key in SelfBot.py - it will automatically sync with {duration_days} days duration!", inline=False)
            
            await interaction.response.send_message(embed=embed)
            
            # Send webhook notification
            await key_manager.send_webhook_notification(key, user_id, machine_id)
            
        else:
            await interaction.response.send_message(f"❌ **Activation Failed:** {result['error']}", ephemeral=True)
            
    except Exception as e:
        await interaction.response.send_message(f"❌ **Error during activation:** {str(e)}", ephemeral=True)

@bot.tree.command(name="revoke", description="Revoke a specific key")
async def revoke_key(interaction: discord.Interaction, key: str):
    """Revoke a specific key"""
    if not await check_permissions(interaction):
        return
    
    if key_manager.revoke_key(key):
        embed = discord.Embed(
            title="🗑️ Key Revoked",
            description=f"Key `{key}` has been successfully revoked.",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("❌ Key not found or already revoked.", ephemeral=True)

@bot.tree.command(name="keys", description="Show all keys for a user")
async def show_keys(interaction: discord.Interaction, user: Optional[discord.Member] = None):
    """Show all keys for a user (or yourself if no user specified)"""
    if not await check_permissions(interaction):
        return
    
    target_user = user or interaction.user
    user_keys = key_manager.get_user_keys(target_user.id)
    
    if not user_keys:
        await interaction.response.send_message(f"🔍 No keys found for {target_user.display_name}.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title=f"🔑 Keys for {target_user.display_name}",
        color=0x2d6cdf
    )
    
    for key_data in user_keys[:10]:  # Limit to 10 keys to avoid embed limits
        key = key_data["key"]
        status = "✅ Active" if key_data["is_active"] else "❌ Revoked"
        expires = f"<t:{key_data['expiration_time']}:R>"
        
        embed.add_field(
            name=f"Key: {key[:8]}...",
            value=f"Status: {status}\nExpires: {expires}\nUsage: {key_data.get('usage_count', 0)} times",
            inline=True
        )
    
    if len(user_keys) > 10:
        embed.set_footer(text=f"Showing 10 of {len(user_keys)} keys")
    
    embed.set_thumbnail(url=target_user.display_avatar.url if target_user.display_avatar else None)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="info", description="Get detailed information about a key")
async def key_info(interaction: discord.Interaction, key: str):
    """Get detailed information about a key"""
    if not await check_permissions(interaction):
        return
    
    key_data = key_manager.get_key_info(key)
    if not key_data:
        await interaction.response.send_message("❌ Key not found.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title=f"🔍 Key Information",
        color=0x2d6cdf
    )
    
    # Get user info
    user = interaction.guild.get_member(key_data["created_by"])
    user_name = user.display_name if user else "Unknown User"
    
    embed.add_field(name="Created By", value=user_name, inline=True)
    embed.add_field(name="Status", value="✅ Active" if key_data["is_active"] else "❌ Revoked", inline=True)
    embed.add_field(name="Created", value=f"<t:{key_data['activation_time']}:R>", inline=True)
    embed.add_field(name="Expires", value=f"<t:{key_data['expiration_time']}:R>", inline=True)
    
    if key_data["channel_id"]:
        embed.add_field(name="Channel Locked", value=f"<#{key_data['channel_id']}>", inline=True)
    
    if key_data["machine_id"]:
        embed.add_field(name="Machine ID", value=f"`{key_data['machine_id']}`", inline=True)
        embed.add_field(name="Activated", value=f"<t:{key_data['activated']}:R>", inline=True)
    
    embed.add_field(name="Usage Count", value=key_data.get("usage_count", 0), inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="backup", description="Create a backup of all keys")
async def backup_keys(interaction: discord.Interaction):
    """Create a backup of all keys"""
    if not await check_permissions(interaction):
        return
    
    backup_file = key_manager.backup_keys()
    
    embed = discord.Embed(
        title="💾 Backup Created",
        description=f"Keys backup saved to `{backup_file}`",
        color=0x00ff00
    )
    
    embed.add_field(name="Total Keys", value=len(key_manager.keys), inline=True)
    embed.add_field(name="Backup Time", value=f"<t:{int(time.time())}:F>", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="restore", description="Restore keys from a backup file")
async def restore_keys(interaction: discord.Interaction, backup_file: str):
    """Restore keys from a backup file"""
    if not await check_permissions(interaction):
        return
    
    if not os.path.exists(backup_file):
        await interaction.response.send_message("❌ Backup file not found.", ephemeral=True)
        return
    
    if key_manager.restore_from_backup(backup_file):
        embed = discord.Embed(
            title="🔄 Backup Restored",
            description="Keys have been successfully restored from backup.",
            color=0x00ff00
        )
        
        embed.add_field(name="Total Keys", value=len(key_manager.keys), inline=True)
        embed.add_field(name="Restore Time", value=f"<t:{int(time.time())}:F>", inline=True)
        
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("❌ Failed to restore from backup.", ephemeral=True)

@bot.tree.command(name="status", description="Show bot status and statistics")
async def bot_status(interaction: discord.Interaction):
    """Show bot status and statistics"""
    if not await check_permissions(interaction):
        return
    
    total_keys = len(key_manager.keys)
    active_keys = sum(1 for k in key_manager.keys.values() if k["is_active"])
    revoked_keys = total_keys - active_keys
    
    # Calculate total usage
    total_usage = sum(k.get("usage_count", 0) for k in key_manager.key_usage.values())
    
    embed = discord.Embed(
        title="📊 Bot Status",
        color=0x2d6cdf
    )
    
    embed.add_field(name="Total Keys", value=total_keys, inline=True)
    embed.add_field(name="Active Keys", value=active_keys, inline=True)
    embed.add_field(name="Revoked Keys", value=revoked_keys, inline=True)
    embed.add_field(name="Total Usage", value=total_usage, inline=True)
    embed.add_field(name="Uptime", value=f"<t:{int(bot.start_time.timestamp())}:R>", inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_member_join(member):
    """Automatically give role to new members if they have a valid key"""
    # This would be triggered when someone joins with a valid key
    # Implementation depends on your activation flow
    pass

# Error handling for slash commands
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"❌ Command is on cooldown. Try again in {error.retry_after:.2f} seconds.", ephemeral=True)
    elif isinstance(error, discord.app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
    elif isinstance(error, discord.app_commands.BotMissingPermissions):
        await interaction.response.send_message("❌ I don't have the required permissions to execute this command.", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ An error occurred: {str(error)}", ephemeral=True)

# New bulk key generation command for special admins
@bot.tree.command(name="generatekeys", description="Generate multiple keys of different types (Special Admin Only)")
async def generate_bulk_keys(interaction: discord.Interaction, daily_count: int, weekly_count: int, monthly_count: int, lifetime_count: int):
    """Generate multiple keys of different types - Special Admin Only"""
    # Check if user is a special admin
    if interaction.user.id not in SPECIAL_ADMIN_IDS:
        await interaction.response.send_message("❌ **Access Denied:** Only special admins can use this command.", ephemeral=True)
        return
    
    if daily_count < 0 or weekly_count < 0 or monthly_count < 0 or lifetime_count < 0:
        await interaction.response.send_message("❌ **Invalid Input:** All counts must be 0 or positive numbers.", ephemeral=True)
        return
    
    if daily_count == 0 and weekly_count == 0 and monthly_count == 0 and lifetime_count == 0:
        await interaction.response.send_message("❌ **Invalid Input:** At least one key type must have a count greater than 0.", ephemeral=True)
        return
    
    # Generate the keys
    generated_keys = key_manager.generate_bulk_keys(daily_count, weekly_count, monthly_count, lifetime_count)
    
    # Create embed showing what was generated
    embed = discord.Embed(
        title="🔑 Bulk Keys Generated Successfully!",
        description="Keys have been generated and saved to the system.",
        color=0x00ff00
    )
    
    embed.add_field(name="📅 Daily Keys (1 day)", value=f"Generated: {len(generated_keys['daily'])}", inline=True)
    embed.add_field(name="📅 Weekly Keys (7 days)", value=f"Generated: {len(generated_keys['weekly'])}", inline=True)
    embed.add_field(name="📅 Monthly Keys (30 days)", value=f"Generated: {len(generated_keys['monthly'])}", inline=True)
    embed.add_field(name="📅 Lifetime Keys (365 days)", value=f"Generated: {len(generated_keys['lifetime'])}", inline=True)
    
    embed.add_field(name="💾 Status", value="✅ All keys saved to database and website", inline=False)
    embed.add_field(name="📱 Website", value="Keys are now available on your website!", inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# New command to view available keys by type
@bot.tree.command(name="viewkeys", description="View all available keys by type (Special Admin Only)")
async def view_available_keys(interaction: discord.Interaction):
    """View all available keys grouped by type - Special Admin Only"""
    # Check if user is a special admin
    if interaction.user.id not in SPECIAL_ADMIN_IDS:
        await interaction.response.send_message("❌ **Access Denied:** Only special admins can use this command.", ephemeral=True)
        return
    
    # Get available keys by type
    available_keys = key_manager.get_available_keys_by_type()
    
    # Create embed showing available keys
    embed = discord.Embed(
        title="🔑 Available Keys by Type",
        description="All unassigned keys currently in the system",
        color=0x2d6cdf
    )
    
    # Daily Keys
    daily_keys = available_keys["daily"]
    if daily_keys:
        daily_text = "\n".join([f"`{key['key']}` - Expires <t:{key['expires']}:R>" for key in daily_keys[:5]])
        if len(daily_keys) > 5:
            daily_text += f"\n... and {len(daily_keys) - 5} more"
        embed.add_field(name=f"📅 Daily Keys ({len(daily_keys)})", value=daily_text, inline=False)
    else:
        embed.add_field(name="📅 Daily Keys (0)", value="No daily keys available", inline=False)
    
    # Weekly Keys
    weekly_keys = available_keys["weekly"]
    if weekly_keys:
        weekly_text = "\n".join([f"`{key['key']}` - Expires <t:{key['expires']}:R>" for key in weekly_keys[:5]])
        if len(weekly_keys) > 5:
            weekly_text += f"\n... and {len(weekly_keys) - 5} more"
        embed.add_field(name=f"📅 Weekly Keys ({len(weekly_keys)})", value=weekly_text, inline=False)
    else:
        embed.add_field(name="📅 Weekly Keys (0)", value="No weekly keys available", inline=False)
    
    # Monthly Keys
    monthly_keys = available_keys["monthly"]
    if monthly_keys:
        monthly_text = "\n".join([f"`{key['key']}` - Expires <t:{key['expires']}:R>" for key in monthly_keys[:5]])
        if len(monthly_keys) > 5:
            monthly_text += f"\n... and {len(monthly_keys) - 5} more"
        embed.add_field(name=f"📅 Monthly Keys ({len(monthly_keys)})", value=monthly_text, inline=False)
    else:
        embed.add_field(name="📅 Monthly Keys (0)", value="No monthly keys available", inline=False)
    
    # Lifetime Keys
    lifetime_keys = available_keys["lifetime"]
    if lifetime_keys:
        lifetime_text = "\n".join([f"`{key['key']}` - Expires <t:{key['expires']}:R>" for key in lifetime_keys[:5]])
        if len(lifetime_keys) > 5:
            lifetime_text += f"\n... and {len(lifetime_keys) - 5} more"
        embed.add_field(name=f"📅 Lifetime Keys ({len(lifetime_keys)})", value=lifetime_text, inline=False)
    else:
        embed.add_field(name="📅 Lifetime Keys (0)", value="No lifetime keys available", inline=False)
    
    embed.set_footer(text="Use /generatekeys to create more keys")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Add a simple API endpoint for SelfBot to get key info
@bot.tree.command(name="sync", description="Sync your key duration with SelfBot")
async def sync_key(interaction: discord.Interaction, key: str):
    """Sync key duration with SelfBot"""
    try:
        key_data = key_manager.get_key_info(key)
        if not key_data:
            await interaction.response.send_message("❌ Key not found.", ephemeral=True)
            return
        
        if not key_data["is_active"]:
            await interaction.response.send_message("❌ Key has been revoked.", ephemeral=True)
            return
        
        # Check if user owns this key
        if key_data["user_id"] != interaction.user.id:
            await interaction.response.send_message("❌ This key doesn't belong to you.", ephemeral=True)
            return
        
        duration_days = key_data.get("duration_days", 30)
        expiration_time = key_data["expiration_time"]
        time_remaining = expiration_time - int(time.time())
        
        if time_remaining <= 0:
            await interaction.response.send_message("❌ This key has expired.", ephemeral=True)
            return
        
        days = time_remaining // 86400
        hours = (time_remaining % 86400) // 3600
        minutes = (time_remaining % 3600) // 60
        
        embed = discord.Embed(
            title="🔄 Key Sync Information",
            description="Use this information in your SelfBot",
            color=0x00ff00
        )
        embed.add_field(name="Key", value=f"`{key}`", inline=False)
        embed.add_field(name="Duration", value=f"{duration_days} days", inline=True)
        embed.add_field(name="Time Remaining", value=f"{days}d {hours}h {minutes}m", inline=True)
        embed.add_field(name="Expires", value=f"<t:{expiration_time}:F>", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Error syncing key: {str(e)}", ephemeral=True)

# Run the bot
if __name__ == "__main__":
    bot.run(BOT_TOKEN)
