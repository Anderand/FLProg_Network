# KC868-A16 RMII TCP/UDP echo gate

Продолжение RMII HTTP gate для KinCony KC868-A16. Тест использует
`FLProgNetworkTcpServer` и `FLProgNetworkUdp` на фиксированном маршруте RMII.
Wi‑Fi и W5500 отключены.

Файл `build_opt.h` включает профиль `FLPROG_NETWORK_BUILD_PROFILE=2`
(`WIRED_ONLY`) для **всей** компиляции этого gate. Поэтому Wi‑Fi и OTA не
попадают в прошивку; удаление вызовов Wi‑Fi из `setup()` само по себе этого
эффекта не даёт.

Там же задан `FLPROG_UTILITES_DISABLE_BLUETOOTH=1`. Для этого gate порт
Bluetooth UART 200 не используется, поэтому из ESP32-сборки исключается
Classic Bluetooth (`BluetoothSerial`). Флаг опционален и не меняет поведение
проектов, где Bluetooth нужен.

| Service | Port | Expected result |
| --- | ---: | --- |
| HTTP diagnostics | 80 | `/` and `/api/status` return HTTP 200 |
| TCP echo | 5001 | every transmitted byte is returned unchanged |
| UDP echo | 5002 | every datagram is returned to the sender unchanged |

## Windows client commands

### TCP

```powershell
$client = [Net.Sockets.TcpClient]::new('192.168.100.12', 5001)
$stream = $client.GetStream()
$bytes = [Text.Encoding]::UTF8.GetBytes('flprog-tcp-rmii')
$stream.Write($bytes, 0, $bytes.Length)
$reply = New-Object byte[] 64
$count = $stream.Read($reply, 0, $reply.Length)
[Text.Encoding]::UTF8.GetString($reply, 0, $count)
$client.Dispose()
```

### UDP

```powershell
$udp = [Net.Sockets.UdpClient]::new()
$udp.Client.ReceiveTimeout = 3000
$bytes = [Text.Encoding]::UTF8.GetBytes('flprog-udp-rmii')
[void]$udp.Send($bytes, $bytes.Length, '192.168.100.12', 5002)
$peer = [Net.IPEndPoint]::new([Net.IPAddress]::Any, 0)
[Text.Encoding]::UTF8.GetString($udp.Receive([ref]$peer))
$udp.Dispose()
```

PASS: both commands return their original string, and `/api/status` increments
the TCP/UDP RX/TX counters.
