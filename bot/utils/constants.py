from bot.database.db import Users, GPTRequest, IMGRequest, DayCounter


bot_messages = {}
block = {}
rm_bg = {}
db_user = Users()
db_gpt = GPTRequest()
db_img = IMGRequest()
db_day = DayCounter()

styles_prompt = {
    "DEFAULT": "",
    "ANIME": "in anime style",
    "CYBERPUNK": "in cyberpunk style, futuristic cyberpunk",
    "UHD": "4k, ultra HD, detailed photo",
    "PENCILDRAWING": "pencil art, pencil drawing, highly detailed",
    "DIGITALPAINTING": "high quality, highly detailed, concept art, digital painting, by greg rutkowski trending on artstation",
    "MEDIEVALPAINTING": "medieval painting, 15th century, trending on artstation",
    "STUDIOPHOTO": "glamorous, emotional ,shot in the photo studio, professional studio lighting, backlit, rim lighting, 8k",
    "PORTRAITPHOTO": "50mm portrait photography, hard rim lighting photography",
    "OILPAINTING": "oil painting, oil",
    "RENDER": "3d render, graphic model",
    "CARTOON": "in cartoon style",
}
