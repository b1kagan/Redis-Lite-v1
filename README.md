## Kurulum (Windows)

```powershell
python -m venv venv
venv\Scripts\activate

pip install fastapi uvicorn pytest httpx
```

## Sunucuyu Çalıştırma

```powershell
uvicorn app.main:app --reload
```

Sunucu `http://127.0.0.1:8000` adresinde ayağa kalkar. Sağlık kontrolü:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

## Testleri Çalıştırma

```powershell
python -m pytest
```

Tüm testleri ayrıntılı çıktıyla print ifadeleri dahil çalıştırmak için:

```powershell
python -m pytest -s
```

Şu an 36 test var (29 domain katmanı + 7 HTTP API testi), hepsi geçiyor.

## Mimari

app/
├── main.py ->  Uygulamayı başlatan giriş noktası
├── api.py -> HTTP endpoint'leri, komut yönlendirme, loglama
├── store.py -> Ham veri saklama (Entry, Store) — komut mantığı içermiyor
├── errors.py -> Domain hata sınıfları
└── commands/
├── string_commands.py -> SET, GET, DEL, INCR
├── hash_commands.py -> HSET, HGET, HDEL, HGETALL
└── zset_commands.py -> ZADD, ZRANGE, ZREM, ZSCORE

## Desteklenen Komutlar

Komut -> Argümanlar | Örnek |

 SET -> key value | `{"command":"SET","args":["user:1","Cuneyt"]}` |
 GET -> key | `{"command":"GET","args":["user:1"]}` |
 DEL -> key | `{"command":"DEL","args":["user:1"]}` |
 INCR -> key | `{"command":"INCR","args":["counter"]}` |
 HSET -> key field value | `{"command":"HSET","args":["user:2","name","Ayse"]}` |
 HGET -> key field | `{"command":"HGET","args":["user:2","name"]}` |
 HDEL -> key field | `{"command":"HDEL","args":["user:2","name"]}` |
 HGETALL -> key | `{"command":"HGETALL","args":["user:2"]}` |
 ZADD -> key score member | `{"command":"ZADD","args":["leaderboard","150","player1"]}` |
 ZRANGE -> key start stop | `{"command":"ZRANGE","args":["leaderboard","0","-1"]}` |
 ZREM -> key member | `{"command":"ZREM","args":["leaderboard","player1"]}` |
 ZSCORE -> key member | `{"command":"ZSCORE","args":["leaderboard","player1"]}` |

Tüm komutlar `POST /command` endpoint'ine gönderilir, komut adları büyük küçük harfe
duyarsızdır.

### Örnek İstek/Cevap

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/command" -Method Post -ContentType "application/json" -Body '{"command":"SET","args":["user:1","Cuneyt"]}'
```

```json
{"ok": true, "result": "OK", "error": null}
```

Hata durumunda (örnek: `user:1` zaten string olarak varken üzerine `HSET` denenmesi):

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/command" -Method Post -ContentType "application/json" -Body '{"command":"HSET","args":["user:1","name","Ayse"]}'
```

```json
{"ok": false, "result": null, "error": {"code": "WRONG_TYPE", "message": "Key exists with a different data type"}}
```

## Sorted Set — Performans Notu

Sorted set'ler `dict(member -> score)` yapısıyla tutuluyor; `ZRANGE` her çağrıldığında
üyeleri skora göre sıralıyor (`O(n log n)`).

**Ölçüm:** 10.000 üyeli bir sorted set'te `ZRANGE` çağrısı ortalama 5.5 ms sürdü
(`tests/test_zset_commands.py::test_zrange_performance_at_scale`).

**Sonuç:** Bu sistem için bu yaklaşım yeterli. Fakat üye sayısı milyonlara çıkarsa her ZRANGE çağrısında O(n log n) sıralama işlemi pahalılaşır, skip list gibi "her zaman sıralı tutulan" bir veri yapısına geçmek gerekir. Gerçek daha büyük redis sistemlerinin skip list kullanmasının sebebi bu

## Eşzamanlılık

`Store`, `threading.Lock` kullanır. `INCR` gibi "oku -> hesapla -> yaz" şeklindeki
çok adımlı işlemler bu kilit altında çalışır, böylece aynı key'e aynı anda gelen
çoklu istekler birbirinin güncellemesini kaybetmez