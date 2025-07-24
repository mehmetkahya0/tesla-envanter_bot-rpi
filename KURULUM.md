# Tesla Envanter Bot - Kurulum Rehberi

Bu rehber, Tesla Envanter Bot'un Home Assistant add-on olarak kurulumu için adım adım talimatları içerir.

## Ön Gereksinimler

- Raspberry Pi 5 (veya desteklenen başka bir cihaz)
- Home Assistant OS kurulu
- İnternet bağlantısı
- Telegram hesabı

## 1. Telegram Bot Oluşturma

### Adım 1: BotFather ile Bot Oluşturun
1. Telegram'da [@BotFather](https://t.me/botfather)'ı bulun ve konuşmaya başlayın
2. `/newbot` komutunu gönderin
3. Bot için bir isim belirleyin (örn: "Tesla Envanter Bot")
4. Bot için bir kullanıcı adı belirleyin (örn: "tesla_envanter_bot")
5. BotFather size bir **Bot Token** verecek - bunu kaydedin!

### Adım 2: Chat ID'nizi Bulun
1. [@userinfobot](https://t.me/userinfobot)'a mesaj gönderin
2. Bot size **Chat ID**'nizi verecek - bunu kaydedin!

## 2. Home Assistant'a Repository Ekleme

### Adım 1: Supervisor'a Gidin
1. Home Assistant web arayüzünde **Supervisor**'a tıklayın
2. **Add-on Store** sekmesine gidin

### Adım 2: Repository Ekleyin
1. Sağ üst köşedeki **⋮** (üç nokta) menüsüne tıklayın
2. **Repositories** seçeneğini seçin
3. Aşağıdaki URL'yi ekleyin:
   ```
   https://github.com/mehmetkahya/tesla-envanter-bot-rpi
   ```
4. **Add** butonuna tıklayın

## 3. Add-on Kurulumu

### Adım 1: Add-on'u Bulun
1. Add-on Store'da **Tesla Envanter Bot**'u arayın
2. Add-on'a tıklayın

### Adım 2: Kurulum
1. **Install** butonuna tıklayın
2. Kurulum tamamlanana kadar bekleyin

## 4. Konfigürasyon

### Adım 1: Configuration Sekmesi
1. Add-on sayfasında **Configuration** sekmesine gidin

### Adım 2: Ayarları Yapın
```yaml
telegram_bot_token: "YOUR_BOT_TOKEN_HERE"
telegram_chat_id: "YOUR_CHAT_ID_HERE"
check_interval: 300
models:
  - "Model 3"
  - "Model Y"
  - "Model S"
  - "Model X"
```

**Önemli:** 
- `YOUR_BOT_TOKEN_HERE` yerine 1. adımda aldığınız bot token'ını yazın
- `YOUR_CHAT_ID_HERE` yerine 1. adımda aldığınız chat ID'yi yazın

### Adım 3: Ayarları Kaydedin
1. **Save** butonuna tıklayın

## 5. Add-on'u Başlatma

### Adım 1: Info Sekmesi
1. **Info** sekmesine gidin

### Adım 2: Otomatik Başlatmayı Etkinleştirin (Opsiyonel)
1. **Start on boot** seçeneğini etkinleştirin
2. **Watchdog** seçeneğini etkinleştirin

### Adım 3: Add-on'u Başlatın
1. **Start** butonuna tıklayın
2. Birkaç saniye sonra **Log** sekmesinden çalışıp çalışmadığını kontrol edin

## 6. Test

### Telegram'dan Test Mesajı
Add-on başarıyla başlatıldığında, Telegram'da bot'tan şu mesajı almalısınız:
```
🤖 Tesla Envanter Bot başlatıldı!

📊 Takip edilen modeller: Model 3, Model Y, Model S, Model X
⏰ Kontrol aralığı: 300 saniye
```

### Log Kontrolü
**Log** sekmesinde şuna benzer mesajlar görmelisiniz:
```
[INFO] Tesla Envanter Bot started!
[INFO] Bot initialized. Monitoring models: ['Model 3', 'Model Y', 'Model S', 'Model X']
[INFO] Checking Tesla inventory...
```

## 7. Sorun Giderme

### Bot mesaj gönderemiyor
- Bot token'ının doğru olduğundan emin olun
- Chat ID'nin doğru olduğundan emin olun
- Bot'u Telegram'da başlattığınızdan emin olun (`/start` komutu)

### Add-on başlamıyor
- Configuration'ın doğru olduğundan emin olun
- Log'ları kontrol edin
- İnternet bağlantınızı kontrol edin

### Envanter kontrolü çalışmıyor
- Tesla sitesinin erişilebilir olduğundan emin olun
- Home Assistant'ın İnternet'e çıkabildiğinden emin olun

## 8. Güncelleme

Add-on güncellemesi geldiğinde:
1. **Info** sekmesinde **Update** butonu görünecek
2. **Update** butonuna tıklayın
3. Güncelleme tamamlandıktan sonra add-on'u yeniden başlatın

---

## Destek

Sorun yaşıyorsanız:
1. Önce **Log** sekmesini kontrol edin
2. GitHub Issues'da sorun bildirin
3. Konfigürasyonunuzu tekrar kontrol edin

Başarılı kurulum! 🎉
