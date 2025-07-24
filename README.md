# Tesla Envanter Bot

Tesla Türkiye araç envanterini takip eden Home Assistant add-on'u. Yeni araçlar envantere eklendiğinde Telegram üzerinden bildirim gönderir.

## Özellikler

- Tesla Türkiye envanterini otomatik takip
- Yeni araç geldiğinde Telegram bildirimi
- Seçilebilir araç modelleri (Model 3, Model Y, Model S, Model X)
- Ayarlanabilir kontrol aralığı
- Home Assistant add-on olarak kolay kurulum

## Kurulum

### 1. Repository Ekleme

Home Assistant'ta **Supervisor > Add-on Store > ⋮ > Repositories**'den bu repository'yi ekleyin:

```
https://github.com/mehmetkahya0/tesla-envanter_bot-rpi
```

### 2. Telegram Bot Oluşturma

1. [@BotFather](https://t.me/botfather) ile konuşarak yeni bot oluşturun
2. `/newbot` komutu ile bot adını ve kullanıcı adını belirleyin
3. Bot token'ını kaydedin

### 3. Chat ID Bulma

1. [@userinfobot](https://t.me/userinfobot)'a mesaj gönderin
2. Chat ID'nizi kaydedin

### 4. Geliştirme/Test için .env Dosyası Oluşturma

Local geliştirme için:

```bash
cp .env.example .env
nano .env
```

.env dosyasını kendi değerlerinizle doldurun:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
CHECK_INTERVAL=300
MODELS=["Model 3", "Model Y", "Model S", "Model X"]
DEBUG=false
```

### 5. Add-on Konfigürasyonu

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

## Yapılandırma Seçenekleri

| Seçenek | Açıklama | Varsayılan |
|---------|----------|------------|
| `telegram_bot_token` | Telegram bot token'ı | - |
| `telegram_chat_id` | Telegram chat ID | - |
| `check_interval` | Kontrol aralığı (saniye) | 300 |
| `models` | Takip edilecek araç modelleri | ["Model 3", "Model Y"] |

## Kullanım

### Home Assistant Add-on Olarak

1. Add-on'u yapılandırın
2. "Start" butonuna tıklayın
3. Telegram'dan başlangıç mesajını bekleyin
4. Bot otomatik olarak envanteri kontrol etmeye başlayacak

### Local Test

```bash
# .env dosyasını oluşturun ve doldurun
cp .env.example .env
nano .env

# Test script'ini çalıştırın
./test.sh
```

## Log Takibi

Add-on'un çalışma durumunu **Log** sekmesinden takip edebilirsiniz.

## Sorun Giderme

### Bot mesaj gönderemiyor
- Bot token'ının doğru olduğundan emin olun
- Chat ID'nin doğru olduğundan emin olun
- Bot'u Telegram'da başlattığınızdan emin olun

### Envanter kontrolü çalışmıyor
- İnternet bağlantınızı kontrol edin
- Tesla sitesinin erişilebilir olduğundan emin olun
- Log'ları kontrol edin

## Lisans

MIT License
