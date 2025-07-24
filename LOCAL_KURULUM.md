# Tesla Envanter Bot - Local Home Assistant Add-on Kurulumu

Bu rehber, Tesla Envanter Bot'u GitHub Actions olmadan local add-on olarak kurmanız için hazırlanmıştır.

## Yöntem 1: Local Add-on (Önerilen)

### Adım 1: Projeyi Home Assistant'a Kopyalayın

1. **SSH/Terminal Add-on ile:**
   ```bash
   # Home Assistant'ta SSH add-on'u yükleyin ve aktifleştirin
   cd /config
   mkdir -p addons/tesla-envanter-bot
   ```

2. **Tüm dosyaları kopyalayın:**
   Bu proje klasöründeki tüm dosyaları `/config/addons/tesla-envanter-bot/` klasörüne kopyalayın.

### Adım 2: Home Assistant'ı Yeniden Başlatın

1. **Supervisor'ı yeniden başlatın:**
   - Settings > System > Restart > Restart Home Assistant Supervisor

### Adım 3: Add-on'u Kurun

1. **Supervisor > Add-on Store**'a gidin
2. **⋮ (üç nokta) > Refresh** yapın
3. **Local Add-ons** bölümünde **Tesla Envanter Bot**'u bulun
4. Add-on'u kurun

## Yöntem 2: Samba Share ile

### Adım 1: Samba Share Add-on'u Kurun

1. **Supervisor > Add-on Store**'dan **Samba share** add-on'unu kurun
2. Add-on'u başlatın

### Adım 2: Dosyaları Kopyalayın

1. **Windows/Mac Finder'da:**
   - `\\homeassistant.local\config` (Windows)
   - `smb://homeassistant.local/config` (Mac)

2. **Klasör oluşturun:**
   ```
   config/
   └── addons/
       └── tesla-envanter-bot/
           ├── config.yaml
           ├── Dockerfile
           ├── tesla_bot.py
           ├── requirements.txt
           ├── run.sh
           └── README.md
   ```

### Adım 3: Home Assistant'ı Yeniden Başlatın

## Yöntem 3: File Editor Add-on ile

### Adım 1: File Editor Add-on'u Kurun

1. **Supervisor > Add-on Store**'dan **File editor** add-on'unu kurun

### Adım 2: Klasör ve Dosyaları Oluşturun

1. **File Editor**'da `/config/addons/tesla-envanter-bot/` klasörü oluşturun
2. Her dosyayı tek tek oluşturun ve içeriklerini kopyalayın

## Konfigürasyon

Add-on kurulduktan sonra:

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

## Sorun Giderme

### Add-on Görünmüyor
- Supervisor'ı yeniden başlatın
- Add-on Store'da Refresh yapın
- Dosyaların doğru konumda olduğundan emin olun

### Build Hatası
- `config.yaml` syntax'ının doğru olduğundan emin olun
- Tüm gerekli dosyaların mevcut olduğunu kontrol edin

### Bot Çalışmıyor
- Telegram bot token'ının doğru olduğundan emin olun
- Chat ID'nizi kontrol edin
- Log'ları kontrol edin

## Dosya Yapısı

```
/config/addons/tesla-envanter-bot/
├── config.yaml          # Home Assistant add-on konfigürasyonu
├── Dockerfile           # Docker container tanımı
├── tesla_bot.py         # Ana bot kodu
├── requirements.txt     # Python dependencies
├── run.sh              # Container başlangıç script'i
├── README.md           # Proje dokümantasyonu
├── KURULUM.md          # Detaylı kurulum rehberi
└── build_local.sh      # Local build script'i (opsiyonel)
```

## Test

Add-on başarıyla kurulduktan sonra:

1. Telegram'dan bot'a `/start` komutu gönderin
2. `/ping` ile bot'un çalışıp çalışmadığını test edin
3. `/manuel-arama` ile envanter kontrolü yapın

Başarılı kurulum! 🎉
