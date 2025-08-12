# 🚀 Discord Bot Deployment Guide

## **What You've Built:**

✅ **Discord Bot** with bulk key generation system  
✅ **4 Key Types:** Daily (1 day), Weekly (7 days), Monthly (30 days), Lifetime (365 days)  
✅ **Special Admin Commands:** Only user ID `485182079923912734` can use `/generatekeys` and `/viewkeys`  
✅ **Automatic Website Sync:** Keys automatically appear on your website  
✅ **Role Management:** Users get Discord roles when activating keys  
✅ **SelfBot Integration:** Keys work with SelfBot.py for real-time countdown  

## **📁 Files to Upload to GitHub:**

### **Essential Files:**
```
Your-Repository/
├── bot.py                    ← Main Discord bot (MOST IMPORTANT)
├── requirements.txt          ← Python dependencies
├── runtime.txt              ← Python version for Render
├── Procfile                 ← Tells Render how to run the bot
├── .gitignore               ← Excludes sensitive files
├── DEPLOYMENT_GUIDE.md      ← This guide
└── README.md                ← Project description
```

### **What NOT to Upload:**
- ❌ `SelfBot.py` - Runs on users' computers
- ❌ `app.py` - Web GUI (not needed for Discord bot)
- ❌ `templates/` folder - Not needed
- ❌ `.env` file - Contains your bot token (sensitive!)
- ❌ Any data files (keys.json, etc.)

## **🔧 Step-by-Step GitHub Setup:**

### **1. Create GitHub Repository:**
- Go to [github.com](https://github.com)
- Click "New repository"
- Name it: `discord-key-bot` (or whatever you want)
- Make it **Public** (Render needs this)
- Don't initialize with README (we'll add files manually)

### **2. Upload Your Files:**
- Drag and drop these files into your repository:
  - `bot.py`
  - `requirements.txt`
  - `runtime.txt`
  - `Procfile`
  - `.gitignore`
  - `DEPLOYMENT_GUIDE.md`

### **3. Commit and Push:**
- Add commit message: "Initial Discord bot setup"
- Click "Commit changes"

## **🚀 Deploy to Render (Free 24/7 Hosting):**

### **1. Connect to Render:**
- Go to [render.com](https://render.com)
- Sign up with GitHub
- Click "New +" → "Web Service"

### **2. Connect Your Repository:**
- Select your GitHub repository
- Render will auto-detect it's a Python app

### **3. Configure the Service:**
- **Name:** `discord-key-bot` (or whatever you want)
- **Environment:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python bot.py`
- **Plan:** `Free`

### **4. Add Environment Variables:**
Click "Environment" tab and add:
```
BOT_TOKEN = MTQwNDUzMzQ5MDEwNzY4MjgzNg.G-eh7N.U7vZyJaEScHE-81IHtYqhYFpfm_V6pR3yo8De8
```

### **5. Deploy:**
- Click "Create Web Service"
- Wait for build to complete (usually 2-3 minutes)
- Your bot will be online 24/7!

## **🎯 How to Use Your Bot:**

### **Special Admin Commands (Only for user ID 485182079923912734):**

**Generate Bulk Keys:**
```
/generatekeys 5 3 2 1
```
- 5 daily keys
- 3 weekly keys  
- 2 monthly keys
- 1 lifetime key

**View Available Keys:**
```
/viewkeys
```
Shows all unassigned keys grouped by type

### **Regular User Commands:**
```
/activate [key]     ← Activate a key and get role
/sync [key]         ← Check key info
/help               ← See all commands
```

## **🔑 Key System Flow:**

1. **Admin generates keys** using `/generatekeys`
2. **Keys automatically save** to database and website
3. **Users activate keys** with `/activate`
4. **Users get Discord role** automatically
5. **Keys work with SelfBot** for real-time countdown
6. **Keys expire** and roles are removed automatically

## **📱 Website Integration:**

Your keys automatically sync to the website because:
- `bot.py` saves keys to `keys.json`
- Website reads from the same `keys.json` file
- Real-time updates when new keys are generated

## **⚠️ Important Notes:**

- **Bot Token:** Never share your bot token publicly
- **Special Admin:** Only user ID `485182079923912734` can generate/view keys
- **24/7 Operation:** Render keeps your bot running even when your PC is off
- **Free Hosting:** Render gives you 750 hours/month free (enough for 24/7)

## **🚨 Troubleshooting:**

**Bot won't start:**
- Check your bot token is correct
- Make sure all files are uploaded to GitHub
- Check Render logs for errors

**Commands not working:**
- Wait for slash commands to sync (can take up to 1 hour)
- Make sure bot has proper permissions in Discord server

**Keys not generating:**
- Verify you're using the correct user ID
- Check if you're in the right Discord server

## **🎉 You're All Set!**

Your Discord bot will now:
- ✅ Run 24/7 for free on Render
- ✅ Generate unlimited keys of all types
- ✅ Automatically sync with your website
- ✅ Manage Discord roles automatically
- ✅ Work with SelfBot for real-time countdown

**Next Steps:**
1. Test the bot in Discord
2. Generate some keys with `/generatekeys`
3. Check your website to see the keys appear
4. Share keys with users to test activation

**Need Help?** Check the Render logs or Discord bot console for error messages!
