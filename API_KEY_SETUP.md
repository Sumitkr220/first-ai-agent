# OpenAI API Key Setup Guide

## 🔑 **Where to Set Your OpenAI API Key**

### **Option 1: .env file (RECOMMENDED) ✅**
```bash
# File: .env (in your project root)
OPENAI_API_KEY=your-api-key-here
```

**Pros:**
- ✅ Secure (not in code)
- ✅ Easy to manage
- ✅ Works across sessions
- ✅ Can be gitignored

### **Option 2: Terminal Session (Temporary)**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

**Pros:**
- ✅ Quick setup
- ✅ No files needed

**Cons:**
- ❌ Lost when terminal closes
- ❌ Need to set again each time

### **Option 3: Shell Profile (Permanent)**
```bash
# Add to ~/.zshrc (macOS/Linux)
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

**Pros:**
- ✅ Permanent across sessions
- ✅ Available in all terminals

**Cons:**
- ❌ Global (affects all projects)
- ❌ Less secure

## 🚀 **Current Setup**

Your project is now configured to use the **.env file** method:

1. ✅ `.env` file created with your API key
2. ✅ `main.py` updated to load `.env` file
3. ✅ `python-dotenv` dependency already installed

## 🔧 **How to Update Your API Key**

### **If you get a new API key:**

1. **Edit the .env file:**
   ```bash
   nano .env
   # or
   code .env
   ```

2. **Replace the old key with the new one:**
   ```
   OPENAI_API_KEY=your-new-api-key-here
   ```

3. **Restart the server:**
   ```bash
   pkill -f "python main.py"
   python main.py
   ```

## 🛡️ **Security Best Practices**

1. **Never commit API keys to git:**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use environment variables** instead of hardcoding

3. **Rotate keys regularly** for security

## 🧪 **Testing Your Setup**

```bash
# Test if API key is loaded
curl http://localhost:8000/health

# Test the country count endpoint
curl -X POST http://localhost:8000/ask-country-count \
  -H "Content-Type: application/json" \
  -d '{}'
```

## 📝 **Troubleshooting**

### **If API key not found:**
```bash
# Check if .env file exists
ls -la .env

# Check if key is loaded
python -c "import os; print('API Key:', bool(os.getenv('OPENAI_API_KEY')))"
```

### **If quota exceeded:**
- Check your OpenAI billing at: https://platform.openai.com/account/billing
- Add payment method if needed
- Wait for quota reset (free tier) 