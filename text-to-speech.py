import cv2
import os
import time
import base64
from PIL import Image
from gtts import gTTS
import google.generativeai as genai

# 設定 Google API Key
GOOGLE_API_KEY = "AIzaSyAJm0QM0qajDdnZrHMjP9G6K_BMqk4rJdg"
genai.configure(api_key=GOOGLE_API_KEY)

# 設置OpenCV用於人體偵測的Haar Cascade分類器
human_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')

# 初始化攝影機
cap = cv2.VideoCapture(0)

# 設定回收桶的高度，這是一個簡單的模擬，您可以根據實際情況進行調整
RECYCLING_BIN_HEIGHT_THRESHOLD = 400

# 設置時間參數，防止錯誤處理過於頻繁
time_elapsed = 0
user_warning_given = False

# 主要處理循環
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 轉換為灰階圖像進行人體偵測
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 偵測人體
    humans = human_cascade.detectMultiScale(gray, 1.1, 3)
    
    # 如果偵測到人體，播放歡迎語音
    if len(humans) > 0 and not user_warning_given:
        tts = gTTS("挖西分笨叟ㄟ，哩齁挖看哩手上ㄟGarbage？", lang="zh-TW")
        tts.save('greeting.mp3')
        os.system('cmdmp3 greeting.mp3')  # Windows播放音效
        user_warning_given = True

    # 顯示畫面
    cv2.imshow('Camera', frame)

    # 處理拍照並進行回收物辨識
    if cv2.waitKey(10) & 0xFF == ord(' '):  # 空格鍵拍照
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        
        # 轉換圖片為base64格式
        _, img_encoded = cv2.imencode('.jpg', frame)
        img_base64 = base64.b64encode(img_encoded.tobytes()).decode()
        
        prompt = "請問照片中是哪類的回收物？"
        
        # 呼叫Google的生成模型進行回收物識別
        try:
            result = genai.GenerativeModel("gemini-1.5-flash").generate_content([prompt, img_base64])
            print(result.text)
            
            # 使用TTS將辨識結果讀出來
            tts = gTTS(result.text, lang="zh-TW")
            tts.save('recycling_result.mp3')
            os.system('cmdmp3 recycling_result.mp3')
        
        except Exception as e:
            print(f"錯誤: {e}")

    # 按G鍵表示正確投放，播放表揚語音
    if cv2.waitKey(10) & 0xFF == ord('g'):  # 按G鍵
        print("你真棒！")
        tts = gTTS("你真棒！你真棒！", lang="zh-TW")
        tts.save('correct.mp3')
        os.system('cmdmp3 correct.mp3')

    # 檢查回收桶是否滿了（簡單的範例，可以根據需要調整）
    if cv2.waitKey(10) & 0xFF == ord('r'):  # 按R鍵模擬回收桶滿的情況
        print("回收桶已滿，發送訊息給清潔人員！")
        tts = gTTS("回收桶已滿，請清空回收桶", lang="zh-TW")
        tts.save('bin_full.mp3')
        os.system('cmdmp3 bin_full.mp3')

    # 處理錯誤處理：當丟錯回收物時
    if cv2.waitKey(10) & 0xFF == ord('e'):  # 按E鍵模擬丟錯回收物
        tts = gTTS("哀噁！哀噁！你給我撿起來！", lang="zh-TW")
        tts.save('error.mp3')
        os.system('cmdmp3 error.mp3')

        # 等待5秒鐘，看使用者是否會撿回錯誤的回收物
        time_elapsed = 0
        while time_elapsed < 5:
            time_elapsed += 1
            time.sleep(1)

            if time_elapsed >= 5:  # 假設用戶不撿回
                tts = gTTS("你個拉基！你個拉基！", lang="zh-TW")
                tts.save('insult.mp3')
                os.system('cmdmp3 insult.mp3')
                
                # 再等10秒鐘
                time_elapsed = 0
                while time_elapsed < 10:
                    time_elapsed += 1
                    time.sleep(1)

                    if time_elapsed >= 10:  # 用戶仍然不撿回
                        tts = gTTS("你這個沒禮貌的臭拉基！", lang="zh-TW")
                        tts.save('final_insult.mp3')
                        os.system('cmdmp3 final_insult.mp3')
                
    # 按Q鍵退出循環
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# 釋放攝像頭並關閉所有窗口
cap.release()
cv2.destroyAllWindows()
