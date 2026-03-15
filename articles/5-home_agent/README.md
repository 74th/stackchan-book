# 5. ホームエージェントにする

ここからはｽﾀｯｸﾁｬﾝをホームエージェント化する方法を解説していきます。

## 5.1. 赤外線リモコンをREST APIで操作できるようにする

技術書典17で頒布した同人誌「お家IoTリモコン全部作る」では、Atom Liteや独自基板を用いて、赤外線リモコンをREST APIで操作できるようにする方法を解説しています。
こちらでも解説しましたが、本書でも簡単に解説しようと思います。

M5Stack ATOM Lite（以下ATOM Lite）は、ESP32を搭載した小型開発モジュールで、赤外線LEDを搭載しています。
ESP32には、WiFiが搭載されているため、ATOM LiteをWebサーバとして動かすことができます。
REST APIのJSONリクエストに、赤外線LEDの信号を含ませて、ATOM Lite側で赤外線LEDを制御します。
これにより、REST APIで操作できる赤外線リモコンを作ることができます。

ATOM Liteは、2026年3現在、1,760円で販売されており、安価に赤外線リモコンを作ることができます。

ただし、ATOM Liteに搭載されている赤外線LEDの回路は余り性能が良くないため、距離があると送れないことがあります。
筆者は、赤外線受光部の近くにデバイスを設置したり、M5Stack Unit IRモジュールを用いて受光部の近くまでケーブルを伸ばすなどして、赤外線信号を送るようにしています。
また、Unit IRには赤外線の受信の機能もあるため、赤外線リモコンの信号を学習させるためにも1個あると便利です。

![TODO:写真: ATOM LiteとUnit IR]()

### 赤外線信号を受信する

ESP32のArduinoフレームワークに対応した、赤外線信号送受信ライブラリがあります。

> crankyoldgit/IRremoteESP8266: Infrared remote library for ESP8266/ESP32
>
> https://github.com/crankyoldgit/IRremoteESP8266

このライブラリを使うことで、赤外線信号の送信/受信と、コード/デコードを行うことができます。
このライブラリが優れた点は、デコードで規格を判別したり、規格を指定してコードを入れることで信号にして送信してくれることです。
赤外線信号を読ませて、SONY製品の信号や、三菱エアコンの信号かなど、信号の種類を判別できます。
また、その判別した結果をそのまま送信できます。
赤外線信号の送信と受信が、このライブラリで完結します。

このライブラリを追加するには、platformio.iniに以下を追加します。

```ini
# platformio.ini
lib_deps =
  https://github.com/crankyoldgit/IRremoteESP8266.git#v2.9.0
```

まずは、受信コードを記述してみましょう。
ボタンを押した後に、USBのシリアルコンソールに出力するコードは以、IRrecv.h、IRutils.hをインクルードして下のように記述できます。

```c
#include <Arduino.h>
#include <IRremoteESP8266.h>
#include <IRrecv.h>
#include <IRutils.h>

#define BUTTON_PIN GPIO_NUM_39      // ボタンピン
#define IR_RECEIVER_PIN GPIO_NUM_32 // 赤外線受信ピン

// 赤外線受信オブジェクト
// 引数: ピン番号、バッファサイズ、タイムアウト(ms)、デコード時に二次バッファを使うか
IRrecv irrecv(IR_RECEIVER_PIN, 1024, 50, true);

void setup()
{
  // シリアルコンソールの有効化
  Serial.begin(115200);

  // ボタン
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // 赤外線受信の初期化
  irrecv.setUnknownThreshold(12);
  irrecv.setTolerance(kTolerance);
  irrecv.enableIRIn();
}

bool ir_receive_mode = false;          // 受信中モード
uint32_t ir_receive_mode_start_ms = 0; // 受信中モード開始時刻
decode_results results;                // 受信結果を入れる構造体

void loop()
{
  bool button = digitalRead(BUTTON_PIN);
  if (!ir_receive_mode && button == LOW)
  {
    // ボタン押下検出
    // 受信モードに入る
    ir_receive_mode = true;
    ir_receive_mode_start_ms = millis();

    Serial.println("Start receive");
  }

  if (ir_receive_mode)
  {
    // 受信中
    if (millis() - ir_receive_mode_start_ms > 10000)
    {
      // 10秒受信がなければ終了
      ir_receive_mode = false;

      Serial.println("receive failed");
      return;
    }

    // 受信、デコード
    if (!irrecv.decode(&results))
    {
      // 受信できていない
      return;
    }

    // 受信、デコード結果をシリアルに出力
    Serial.println("received:");
    Serial.println(resultToHumanReadableBasic(&results).c_str());

    // モードを戻す
    ir_receive_mode = false;
  }
}
```

まず、IRremoteESP8266のヘッダーを追加し、受信用のオブジェクト`irrecv`を定義します。
`setup()`で、その初期化を行います。
`loop()`で、ボタンの押下を読み取って受信中モードに入り、`rrevc.decode(&results)`で受信処理を発動します。
受信できて戻り値に`true`が返る場合には`printf`でその内容を出力します。
ログ出力に適した形に書き換える関数`resultToHumanReadableBasic(&results)`があるため、それを利用します。

では、実際にAtomに書き込み、シリアルコンソールで見ながら操作してみます。
ボタンを押して、受信中モードになったところで、SONY製TVのリモコンの電源ボタンを読ませてみました。
以下の通りデコード結果が表示されました。

```
Start receive
received:
Protocol  : SONY
Code      : 0xA90 (12 Bits)
```

ここまでで受信コードができました。

### 赤外線信号を送信する

次に赤外線を送信する処理をIRremoteESP8266で実装します。

IRremoteESP8266では、SONY製品や三菱エアコンなど信号の仕様ごとにメソッドが分かれており、それを呼び分けることで信号を送信できます。

ボタンを押したときに、先ほどのSONY製のTVに信号を送るコードはIRsend.hをインクルードして実装します。
以下のようになります。

```c
#include <Arduino.h>
#include <IRremoteESP8266.h>
#include <IRsend.h>

#define BUTTON_PIN GPIO_NUM_39  // ボタンピン
#define IR_SEND_PIN GPIO_NUM_26 // M5 IR赤外線送信ピン(Grove D2)

// 赤外線送信用オブジェクト
// 引数: ピン
IRsend irsend(IR_SEND_PIN);

// SONY TVの電源ボタンのコード
uint64_t sony_tv_power_code = 0xA90;

void setup()
{
  // シリアルコンソールの有効化
  Serial.begin(115200);

  // ボタン
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // 赤外線送信の初期化
  irsend.begin();
}

bool latest_button_state = HIGH;

void loop()
{
  bool button = digitalRead(BUTTON_PIN);
  if (button == LOW && latest_button_state == HIGH)
  {
    // ボタン押下検出
    Serial.println("Start send");

    // SONY製品の赤外線信号の送信
    // 引数: コード、ビット数、リピート回数
    irsend.sendSony(sony_tv_power_code, 12, 2);

    Serial.println("Done send");
  }

  latest_button_state = button;
}

```

受信の時と同じように送信用オブジェクト`irsend`を定義して、`setup()`内で初期化します。
`loop()`内で、ボタンが押されたイベントを拾って、`rsend.sendSony()`を呼び出すだけです。

これをビルドしてアップロードし、実際の筆者の家のSONY製TVの電源を付けられるか試したところ、無事操作することができました。

なお、Atomには赤外線LEDがついているため、M5 IRを使わなくても赤外線の送信ができます。
その場合には、`#define IR_SEND_PIN GPIO_NUM_12`とピンの番号を変えれば動作します。

### Webサーバを立てる

WiFi接続同様、Webサーバ構築も高度にライブラリ化されており、簡単な以下のようなコードで実現できます。

```c
#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ssid.hpp>

// 略: WiFi接続

// WebServerオブジェクト（引数はポート番号）
WebServer server(80);

// GET /
void handleRootAPI()
{
  Serial.println("access GET /");

  server.send(200, "application/json", "{}");
}

// POST /ir/send
void handleIRSendAPI()
{
  Serial.println("access POST /ir/send");

  // リクエストボディを出力
  String request_body = server.arg("plain");
  Serial.print("request body:");
  Serial.println(request_body);

  server.send(200, "application/json", "{}");
}

// 404 Not Found
void handleNotFoundAPI()
{
  server.send(404, "application/json", "{\"message\": \"Not Found.\"}");
}

void setup()
{
  Serial.begin(115200);

  // 略: WiFi接続

  // Webサーバの開始
  server.on("/", HTTP_GET, handleRootAPI);
  server.on("/ir/send", HTTP_POST, handleIRSendAPI);
  server.onNotFound(handleNotFoundAPI);
  server.begin();
}

// 最後のモニター出力
uint32_t last_monitor_time = 0;

void loop()
{
  if (millis() - last_monitor_time > 1000)
  {
    // モニター出力を1秒ごとにする
    last_monitor_time = millis();
    Serial.print("IP:");
    Serial.println(WiFi.localIP());
  }

  // サーバのリクエストを処理する
  server.handleClient();
}
```

まず、`#include <WebServer.h>`を記述して、ライブラリをインクルードします。
Webサーバのポートを記述したWebServerオブジェクトを `WebServer server(80);`と作成します。

このserverオブジェクトに対して、パスとそのパスを処理するコールバック関数を`server.on("/ir/send", HTTP_POST, handleIRSendAPI);`のように登録します。
コールバック関数内では、`server.arg("plain")`でリクエストボディを取得でき、レスポンスを`server.send(200, "application/json", "{}");`のように返します。

これでWebサーバの構築が完了です。
実際にファームウェアをアップロードし、ブラウザに`http://<IPアドレス>/`にアクセスしたり、curlで`http://<IPアドレス>/ir/send`にPOSTリクエストを送信してみましょう。

```
$ curl -X POST -H "Content-Type: application/json" -d "{\"hoge\" : \"fuga\"}" ⏎
      192.168.1.113/ir/send
{}

# シリアルコンソール
access POST /ir/send
request body:{"hoge" : "fuga"}
```

リクエストボディを取得して、レスポンスを返すことができました。
あとはここまでに行った赤外線の送受信処理をコールバック関数中で行えば、WebAPIとして利用できます。

### リクエストとレスポンスのJSONを扱って、WebAPIを完成させる

最後に、リクエストとレスポンスのJSONを扱って、WebAPIを完成させましょう。
送信、受信のAPIはそれぞれ、以下のようなリクエストとレスポンスをもつ仕様にします。

#### 仕様 POST /ir/send 赤外線送信API

リクエストボディには、以下の通り信号のタイプと、信号データを16進数の文字列表現（hex）で渡すようにします。

```json
{
  "type": "SONY",
  "hex": "0xA90"
}
```

成功時のレスポンスボディは、成功可否を返します。成功した場合にはステータスコード200を返します。

```json
{
  "success": true
}
```

エラー時には、エラー理由をレスポンスボディに含めます。入力に問題がある場合ステータスコード401を返します。

```json
{
  "success": false,
  "error": "type is required."
}
```

#### GET /ir/receive 赤外線受信API

メソッドGETのため、リクエストボディはありません。

レスポンスボディには、信号データを含みます。

```json
{
  "success": true,
  "data": {
    "type": "SONY",
    "hex": "0xAF0"
  }
}
```

10秒以上受信できなかった場合には、エラーを返します。

```json
{
  "success": false,
  "error": "timeout"
}
```

#### ArduinoJsonでリクエストとレスポンスのJSONを操作する

ArduinoでJSONを扱うためのライブラリは、ArduinoJsonが有名です。

> ArduinoJson: Efficient JSON serialization for embedded C++
>
> https://arduinojson.org/

このライブラリを使うには、今までと同様にplatformio.iniに追加します。

```ini
# platformio.ini
# 略
lib_deps =
    adafruit/Adafruit NeoPixel @ 1.12.2
    https://github.com/crankyoldgit/IRremoteESP8266.git#v2.8.6
    bblanchon/ArduinoJson @ 7.0.4
```

まず、このライブラリをインクルードします。

```c
#include <ArduinoJson.h>
```

ArduinoJsonはJSONドキュメントのオブジェクトJsonDocumentを使い、リクエストボディをパースしたり、レスポンスのJSONとしてセリアライズしたりします。
JsonDocumentは、仮想配列として `reqDoc["type"]`というように各属性にアクセスできます。

`POST /ir/send` において、リクエストボディをJSONとしてパースします。
以下のように実装できます。

```c
// POST /ir/send
void handleIRSendAPI()
{
  Serial.println("access POST /ir/send");

  JsonDocument resDoc;       // レスポンスのJSON
  JsonDocument reqDoc;       // リクエストのJSON
  char resBodyBuf[1024 * 2]; // レスポンスのバッファ

  // リクエストボディのJSONデシリアライズ
  String requestBody = server.arg("plain");
  Serial.print("request body:");
  Serial.println(requestBody);
  DeserializationError err = deserializeJson(reqDoc, requestBody);
  if (err)
  {
    // デシリアライズ失敗した場合のエラー
    resDoc["error"] = "failed to deserialize Json";
    resDoc["error_detail"] = err.c_str();
    resDoc["success"] = false;

    // JSONをレスポンス
    serializeJson(resDoc, resBodyBuf, sizeof(resBodyBuf));
    Serial.println(resBodyBuf);
    server.send(401, "application/json", resBodyBuf);
    return;
  }

  // 信号のタイプのプロパティを取得
  const char *type = reqDoc["type"];
  if (type == NULL || strlen(type) == 0)
  {
    // プロパティがないエラー
    resDoc["error"] = "type is required.";
    resDoc["success"] = false;

    // JSONをレスポンス
    serializeJson(resDoc, resBodyBuf, sizeof(resBodyBuf));
    Serial.println(resBodyBuf);
    server.send(401, "application/json", resBodyBuf);
    return;
  }

  // 信号データのプロパティを取得
  const char *hexData = reqDoc["hex"];
  if (hexData == NULL || strlen(hexData) == 0)
  {
    // 取得できない場合エラーを返す
    String errorMessage = "hex is required.";
    resDoc["error"] = errorMessage;
    resDoc["success"] = false;
    serializeJson(resDoc, resBodyBuf, sizeof(resBodyBuf));
    Serial.println(errorMessage);
    server.send(401, "application/json", resBodyBuf);
    return;
  }

  // 略
}
```

冒頭に、JsonDocument型の`resDoc`、`reqDoc`を定義しておきます。

`deserializeJson(reqDoc, requestBody);`でリクエストボディをパースし、`reqDoc`に展開します。
展開後は`const char *type = reqDoc["type"];`などの仮想配列としてアクセスして、JSONオブジェクトのプロパティにアクセスできます。

レスポンスは`resDoc`に対して、仮想配列のアクセスをして`resDoc["error"] = "type is required";`のようにプロパティを埋めて作っていきます。
`serializeJson(resDoc, resBodyBuf, sizeof(resBodyBuf));`で、バッファ`resBodyBuf`にシリアライズしたJSONテキストを格納します。
このバッファを、server.send()関数で送ればJSONのレスポンスを実現できます。

リクエストのJSONのパースエラーや、パラメータとなるプロパティがないことをチェックし、必要に応じてエラー応答を返しましょう。

#### 赤外線送信処理のWebAPI化

では赤外線送信処理となるWebServerのコールバック関数を作っていきましょう。

信号データをパラメータとするためにバイナリデータを受け取れば良いですが、JSONにはバイナリを送る仕様はありません。
そのため、`"0xA90"`などの16進数テキスト値をやりとりに使い、バイナリに変換して利用します。

テキストをバイナリに変換する関数は、Uint64の値として出力する`hexStringToUint64()`と、バイト列として出力する`hexStringToByteArray()`として以下のように作りました。

```c
// hexの文字列をuint64_tに変換
uint64_t hexStringToUint64(const char *hexString)
{
  // 冒頭の`0x`を除く
  if (hexString[0] == '0' && (hexString[1] == 'x' || hexString[1] == 'X'))
  {
    hexString += 2;
  }

  uint64_t result = strtoull(hexString, NULL, 16);

  return result;
}

// 16進数文字を対応する数値に変換
unsigned char hexCharToValue(char hexChar)
{
  if ('0' <= hexChar && hexChar <= '9')
  {
    return hexChar - '0';
  }
  else if ('a' <= hexChar && hexChar <= 'f')
  {
    return hexChar - 'a' + 10;
  }
  else if ('A' <= hexChar && hexChar <= 'F')
  {
    return hexChar - 'A' + 10;
  }
  else
  {
    return 0;
  }
}

// HEX文字列をバイト列に変換する関数
void hexStringToByteArray(const char *hexString, unsigned char *byteArray, size_t *byteArraySize)
{
  // 冒頭の`0x`を除く
  if (hexString[0] == '0' && (hexString[1] == 'x' || hexString[1] == 'X'))
  {
    hexString += 2;
  }

  size_t hexLen = strlen(hexString);
  *byteArraySize = hexLen / 2;

  for (size_t i = 0; i < hexLen / 2; ++i)
  {
    byteArray[i] = (hexCharToValue(hexString[2 * i]) << 4) | hexCharToValue(hexString[2 * i + 1]);
  }
}
```

では実際のコードを見ていきましょう。
前節でパースまで実装した`handleIRSendAPI()`の続きとして、`type`変数を読み取って分岐し、信号のテキストは先に作った関数でバイナリに変換して、赤外線送信関数を呼び出して送ります。
SONY TVと三菱エアコンに対応しました。

```c
void handleIRSendAPI()
{
  // 略

  // タイプごとに送信
  if (strcmp(type, "SONY") == 0)
  {
    // SONY TV

    // hexテキストをuint64_tにパース
    uint64_t data_u64 = hexStringToUint64(hexData);
    Serial.printf("data: %x\r\n", data_u64);

    // データ長を特定（SONYは、12、15、20ビットの3種類）
    int16_t dataSize_bits;
    if (data_u64 <= 1 << 12)
    {
      dataSize_bits = 12;
    }
    else if (data_u64 <= 1 << 15)
    {
      dataSize_bits = 15;
    }
    else
    {
      dataSize_bits = 20;
    }

    // 送信
    irsend.sendSony(data_u64, dataSize_bits, 2);
  }
  else if (strcmp(type, "MITSUBISHI_AC") == 0)
  {
    // 三菱エアコン
    unsigned char data_bytes[64];
    size_t dataSize_bytes;

    // hexデータ
    hexStringToByteArray(hexData, data_bytes, &dataSize_bytes);
    Serial.printf("data: %llx\r\n", data_bytes);

    // 送信
    irsend.sendMitsubishiAC(data_bytes, dataSize_bytes);
  }
  else
  {
    // 不明なタイプのエラーレスポンス
    resDoc["error"] = "unknown type";
    resDoc["success"] = false;

    // JSONをレスポンス
    serializeJson(resDoc, resBodyBuf, sizeof(resBodyBuf));
    Serial.println(resBodyBuf);
    server.send(401, "application/json", resBodyBuf);
    return;
  }

  // 成功時の応答のレスポンス
  resDoc["success"] = true;

  // JSONをレスポンス
  serializeJson(resDoc, resBodyBuf, sizeof(resBodyBuf));
  Serial.println(resBodyBuf);
  server.send(200, "application/json", resBodyBuf);
}
```

三菱エアコンではchar\*型のバイト列を渡すだけで良いのですが、SONYの場合はbit数を指定する必要があります。
SONY TVの信号は、12、15、20ビットの3種類があり、それを判別して送信できるようにしています。

その他の実装内容は、技術的には今まで解説した内容の組み合わせであるため、詳しくは説明しません。
コード中のコメントを参照してください。

このコードをアップロードした後は、実際にcurlなどでリクエストして、TVなどの家電が操作できているか確認してみましょう。
HTTPのレスポンスと、シリアルコンソールには以下のように出力されます。

```
$curl -X POST -H 'Content-Type: application/json' ⏎
 -d '{"type" : "SONY", "hex": "0xA90"}' 192.168.1.113/ir/send
{"success":true}

# シリアルコンソール
access POST /ir/send
request body:{"type" : "SONY", "hex": "0xA90"}
data: a90
{"success":true}
```

これで送信のAPIが完成しました。

#### 赤外線受信処理のWebAPI化

つづいて受信処理を実装していきます。
先に実装したコードを示します。

```c
void handleIRReceiveAPI()
{
  Serial.println("access GET /ir/receive");

  JsonDocument resDoc;       // レスポンスのJSON
  char resBodyBuf[1024 * 2]; // レスポンスのバッファ

  uint32_t start_time = millis();
  while (true)
  {
    if (millis() > start_time + 10000)
    {
      // タイムアウトのエラー
      resDoc["success"] = false;
      resDoc["error"] = "timeout";

      // JSONをレスポンス
      serializeJson(resDoc, resBodyBuf, sizeof(resBodyBuf));
      Serial.println(resBodyBuf);
      server.send(400, "application/json", resBodyBuf);
      break;
    }

    // 受信デコード結果
    decode_results results;
    if (!irrecv.decode(&results))
    {
      // 受信できていない
      continue;
    }

    // 受信、デコード結果をシリアルに出力
    Serial.println("received:");
    Serial.println(resultToHumanReadableBasic(&results));

    // 受信、デコード結果をJSON形式でレスポンス
    resDoc["data"]["type"] = typeToString(results.decode_type, results.repeat);
    resDoc["data"]["hex"] = resultToHexidecimal(&results);
    resDoc["success"] = true;

    // JSONをレスポンス
    serializeJson(resDoc, resBodyBuf, sizeof(resBodyBuf));
    Serial.println(resBodyBuf);
    server.send(200, "application/json", resBodyBuf);
    break;
  }
}
```

受信した赤外線信号をレスポンスデータとして格納するため、IRutils.hにある`resultToHexidecimal()`と`typeToString()`を使って、受信データをテキストにしてJSONのプロパティに格納しています。

今回の製作では、同時に複数リクエストを処理することを想定していないため、APIのコールバック内で受信の待ち処理を行います。
そのため、受信処理中に他のリクエストを受け付けることができません。

こちらについても、今まで解説した内容の組み合わせになるため、細かい実装内容については説明しません。
コード中のコメントを参照してください。

また、`GET /ir/receive`でこの関数をコールバックするように、setup()内に記述を追加します。

```c
void setup()
{
  // 略

  // Webサーバの開始
  server.on("/", HTTP_GET, handleRootAPI);
  server.on("/ir/send", HTTP_POST, handleIRSendAPI);
  server.on("/ir/receive", HTTP_GET, handleIRReceiveAPI);
  server.onNotFound(handleNotFoundAPI);
  server.begin();
}
```

これで受信のAPIが完成しました。
実際にcurlなどでリクエストし、すぐさまTVリモコン等で信号を受信機に送ってみましょう。
以下のようにレスポンスに、受信データが含まれていれば成功です。

```
$curl -X GET 192.168.1.113/ir/receive
{"data":{"type":"SONY","hex":"0xAF0"},"success":true}

# シリアルコンソール
access GET /ir/receive
received:
Protocol  : SONY
Code      : 0xAF0 (12 Bits)

{"data":{"type":"SONY","hex":"0xAF0"},"success":true}
```

### Claude Agent SDKのツール化する

WebAPIが完成したら、あとはClaude Agent SDKのツールとして呼び出せるようにするだけです。



## 5.2. バス時刻表を入れる

筆者の自宅は駅から1kmほど離れているため、市のコミュニティバスが利用できると便利です。
