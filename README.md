# DiscordDPI
DiscordDPI, Discord'un IP tabanlı erişim engellerini aşmak için geliştirilmiş Python tabanlı bir araçtır. Bu araç, Chrome tarayıcısını kullanarak gizli modda Discord'a erişim sağlar ve bağlantı sorunlarını çözmeyi hedefler.

## Tüm Parametreler ve Açıklamaları
- --host        : Proxy sunucusu IP adresi (varsayılan: 127.0.0.1)
- --port        : Proxy sunucusu port numarası (varsayılan: 8080)
- --chunk-size  : Veri okuma/yazma boyutu (varsayılan: 8192)
- --window-size : DPI bypass boyutu (varsayılan: 64, agresif: 32, çok agresif: 16)
- --timeout     : Bağlantı zaman aşımı süresi (varsayılan: 30)
- --debug       : Debug modunu etkinleştir (detaylı loglar için)<br>
<i>Gelen/Giden paketleri görmek istemiyorsanız kaldırın.</i>
- --dns-addr    : Özel DNS sunucu adresi (varsayılan: 8.8.8.8)<br>
<i>Alternatifler: 1.1.1.1 (Cloudflare)</i>
- --dns-port    : Özel DNS sunucu portu (varsayılan: 53)
- --enable-doh  : DNS-over-HTTPS kullanımını etkinleştir (DNS sansürünü bypass etmek için)

## Tavsiye edilen ayarlar
- DPIBypass.exe --debug --window-size 16 --enable-doh --timeout 30 --dns-addr 1.1.1.1<br>
<i>Eğer siteye giriş yapamıyorsanız --window-size değerini düşürün.</i>

## Kullanım
- run.bat dosyasını açıp çalıştırın veya parametrelere göre düzenleyin.
- Cloudflare WARP uygulamasından 1.1.1.1 DNS özelliğini açın.

## Sorumluluk Reddi
**Bu program tamamen eğitim amaçlı bir projedir. Kullanımından doğabilecek sorunlardan kullanıcı sorumludur.**
