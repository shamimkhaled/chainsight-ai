# ⚡ ChainSight AI - 5-Minute Postman Quick Start

## 🎯 Goal
Get ChainSight AI up and running in Postman in 5 minutes!

---

## Step 1: Start Backend (1 minute)

```bash
cd /home/shamimkhaled/chainsight-ai
source venv/bin/activate
python manage.py runserver
```

**Test it:**
```bash
curl http://localhost:8000/api/health/
```

You should see: `{"status": "healthy"}`

---

## Step 2: Import to Postman (1 minute)

1. Open **Postman**
2. Click **"Import"** button (top-left)
3. **Drag and drop** or select:
   - `ChainSight_AI_Postman_Collection.json`
   - `ChainSight_AI_Environment.postman_environment.json`
4. Click **"Import"**

5. **Activate Environment:**
   - Top-right dropdown
   - Select: **"ChainSight AI - Local Development"**
   - Click eye icon to verify variables

---

## Step 3: Register & Login (1 minute)

### A. Register Tenant
1. Expand: **🔐 Authentication**
2. Click: **"Register Tenant & Admin"**
3. Click: **"Send"**

**Check Response:**
```json
{
  "tenant": { "id": "..." },
  "access_token": "...",
  ...
}
```

✅ Variables `access_token` and `tenant_id` auto-saved!

### B. Login (Alternative)
If already registered, use **"Login"** request instead.

---

## Step 4: Upload Contract (1 minute)

1. Expand: **📄 Contract Management**
2. Click: **"Upload Contract"**
3. In **Body** tab:
   - Click **"file"** → Select a PDF
   - Keep defaults for other fields
4. Click: **"Send"**

**Response:**
```json
{
  "id": "contract-uuid",
  "status": "pending",
  "original_filename": "your-file.pdf"
}
```

✅ Variable `contract_id` auto-saved!

---

## Step 5: Chat with Contract (1 minute)

### A. Create Chat Session
1. Expand: **💬 RAG Chat System**
2. Click: **"Create Chat Session"**
3. Click: **"Send"**

✅ Variable `session_id` auto-saved!

### B. Ask a Question
1. Click: **"Send Chat Message"**
2. **Optional:** Edit the question in Body:
   ```json
   {
     "content": "What are the payment terms?"
   }
   ```
3. Click: **"Send"**

**Response:**
```json
{
  "assistant_message": {
    "content": "Based on Clause 1.1...",
    "sources": [
      {
        "clause_number": "1.1",
        "page_number": 3,
        ...
      }
    ]
  }
}
```

🎉 **You're chatting with your contract using AI!**

---

## 🎯 What You've Accomplished

In 5 minutes, you've:
- ✅ Started the backend
- ✅ Imported Postman collection
- ✅ Registered a tenant
- ✅ Uploaded a contract
- ✅ Created a chat session
- ✅ Asked AI a question about your contract!

---

## 🚀 Next Steps

### Try More Chat Questions:
```
"What are the termination conditions?"
"Are there any liability limitations?"
"What are the main risks?"
"When does this contract expire?"
```

### Explore More Features:
1. **Dashboard** → Get overview statistics
2. **Create Alert Rule** → Set up risk alerts
3. **Batch Upload** → Upload multiple contracts
4. **Generate Report** → Get risk assessment

---

## 📚 Full Documentation

- **Testing Guide:** `POSTMAN_TESTING_GUIDE.md`
- **Sample Data:** `SAMPLE_TEST_DATA.md`
- **API Docs:** `COMPLETE_API_DOCUMENTATION.md`
- **Swagger UI:** http://localhost:8000/api/docs/

---

## 🐛 Troubleshooting

### "Connection Refused"
→ Backend not running. Start with `python manage.py runserver`

### "401 Unauthorized"
→ Run "Login" request again to refresh token

### "404 Not Found"
→ Check that `base_url` = `http://localhost:8000/api/v1`

### Variables Not Saving
→ Make sure environment is selected (top-right dropdown)

---

## 🎨 Postman Pro Tips

1. **Check Environment Variables:**
   - Click eye icon (👁️) top-right
   - Verify `access_token` and `tenant_id` are set

2. **View Auto-Generated Variables:**
   After each request, check **Tests** tab to see how variables are saved

3. **Use Collection Runner:**
   - Click "▶ Run" on collection
   - Run all requests sequentially

4. **Export for Team:**
   - Right-click collection → Export
   - Share JSON with team

---

## ✅ Success Checklist

After 5 minutes, you should have:
- [x] Backend running on port 8000
- [x] Postman collection imported
- [x] Environment activated
- [x] Tenant registered
- [x] Contract uploaded
- [x] Chat session created
- [x] AI answered your question!

---

**🎉 You're ready to explore ChainSight AI!**

**Need Help?**
- Check Swagger UI: http://localhost:8000/api/docs/
- Read full guide: `POSTMAN_TESTING_GUIDE.md`
- Review API docs: `COMPLETE_API_DOCUMENTATION.md`

---

**Start Time:** _____
**End Time:** _____
**Total:** Should be ≤ 5 minutes! ⚡


