<!-- PDFの時だけ有効にする -->

<div style="position: absolute; top:0px; height:100%; width:100%;">
  <img src="../../toppage/ebook.png" style="height: 100%; width: 100%; object-fit: contain" />
</div>

<div style="break-before: page;" />

<div height="10px"> </div>

<div style="break-before: page;" />

# まえがき

ｽﾀｯｸﾁｬﾝは、コミュニティベースのKawaiiロボット製作ムーブメントです。
M5Stack BASICなどのM5Stack社の製品を使います。

TODO: 写真

本書は、筆者がオープンソースハードウェアのｽﾀｯｸﾁｬﾝの部品を用いてｽﾀｯｸﾁｬﾝを製作し、それを筆者がお家AIエージェントとして使えるようにカスタマイズしていった記録になっています。
そこで必要だった知識や、筆者の考え方、構築の方法を解説します。
筆者のようにホームIoT化する以外にも、ｽﾀｯｸﾁｬﾝをより魅力的にカスタマイズするための知識として使えるように記述しました。

## 筆者がｽﾀｯｸﾁｬﾝに興味を持ったきっかけ

筆者は、X上でｽﾀｯｸﾁｬﾝの製作例が多数挙がっていたのと、「作ってみれば分かるｽﾀｯｸﾁｬﾝ」とタカヲさんが言われていたのを見て、興味を持ました。
2025年に、公開されているデータを元に基板を製造し、自宅の3Dプリンタでケースを印刷、さらにrobo8080さんのAIｽﾀｯｸﾁｬﾝファームウェアを入れていました。

カワイイ姿を動かして楽しんでいました。
製作は楽しめましたが、実用性を見出すことができず、戸棚にしまわれてしまいました。

筆者は2024年にIoTリモコンの製作にハマりました。
この頃お家の家電リモコンをスマホから操作できるように、M5Stack製品や、ESP32-C3を使って、REST APIベースのIoTを製作しました。
StreamlitというPythonのデータ可視化フレームワークを、Webアプリの操作盤として使い、スマホから家電が操作できる環境を作りました。
この製作を同人誌「お家IoTリモコン全部作る」にまとめ、技術書典17で頒布しました。
しかし、スマホを操作しなくても物理リモコンで操作した方が早いことが多く、活躍の機会は多くありませんでした。

世界ではAIエージェントが隆盛しており、活用できれば音声という手軽な手段で操作ができるようになります。
Google HomeのGeminiで全てができると良いのですが、ChatGPTと始めとするチャットエージェントが、自由なAPIにアクセスできるようにできるようにする機能はなかなか出てきません。
製品が出ないことにしびれを切らして、自作するならばｽﾀｯｸﾁｬﾝができるようになれば実用性もあってKawaiiと思い当たりました。
個人的にもAIエージェントの製作技術を習得したいと思っていました。

本書籍が、ご自身でのｽﾀｯｸﾁｬﾝのカスタマイズや、ホームAIエージェントの開発に参考になれば幸いです。

<div style="break-before: page;" />

# 目次

<nav id="toc" role="doc-toc">

<div class="toc">

<!-- ここから目次(深さ=2) -->
- [まえがき](../0-prologue/README.html#まえがき)
  - [筆者がｽﾀｯｸﾁｬﾝに興味を持ったきっかけ](../0-prologue/README.html#筆者がｽﾀｯｸﾁｬﾝに興味を持ったきっかけ)
- [目次](../0-prologue/README.html#目次)
- [1. ｽﾀｯｸﾁｬﾝ](../1-stachchan/README.html#1-ｽﾀｯｸﾁｬﾝ)
  - [ｽﾀｯｸﾁｬﾝとは](../1-stachchan/README.html#ｽﾀｯｸﾁｬﾝとは)
  - [ｽﾀｯｸﾁｬﾝの主な部品](../1-stachchan/README.html#ｽﾀｯｸﾁｬﾝの主な部品)
  - [ｽﾀｯｸﾁｬﾝのファームウェア](../1-stachchan/README.html#ｽﾀｯｸﾁｬﾝのファームウェア)
  - [可能な組み合わせ](../1-stachchan/README.html#可能な組み合わせ)
  - [自分で製造する方法](../1-stachchan/README.html#自分で製造する方法)
  - [M5Stack公式ｽﾀｯｸﾁｬﾝキット](../1-stachchan/README.html#m5stack公式ｽﾀｯｸﾁｬﾝキット)
  - [その他](../1-stachchan/README.html#その他)
- [2. 筆者のAIｽﾀｯｸﾁｬﾝ製作アーキテクチャ](../2-architecture/README.html#2-筆者のaiｽﾀｯｸﾁｬﾝ製作アーキテクチャ)
  - [2.1. AIエージェント開発](../2-architecture/README.html#21-aiエージェント開発)
  - [2.2. 筆者のホームAIエージェントｽﾀｯｸﾁｬﾝのアーキテクチャ](../2-architecture/README.html#22-筆者のホームaiエージェントｽﾀｯｸﾁｬﾝのアーキテクチャ)
  - [2.3. 今回作成したファームウェアとサーバのフレームワーク](../2-architecture/README.html#23-今回作成したファームウェアとサーバのフレームワーク)
- [3. ファームウェア開発](../3-firmware/README.html#3-ファームウェア開発)
  - [3.1. PlatformIO](../3-firmware/README.html#31-platformio)
  - [3.5. WebSocket通信](../3-firmware/README.html#35-websocket通信)
  - [3.2. M5Unified](../3-firmware/README.html#32-m5unified)
  - [3.3. サーボモータの操作](../3-firmware/README.html#33-サーボモータの操作)
  - [3.4. WakeupWord検出をESP-SRで実現する](../3-firmware/README.html#34-wakeupword検出をesp-srで実現する)
- [4. AIエージェント](../4-ai_agent/README.html#4-aiエージェント)
- [5. ホームエージェントにする](../5-home_agent/README.html#5-ホームエージェントにする)
- [Appendix 1. 自宅サーバに機能を立てる](../10-home_server/README.html#appendix-1-自宅サーバに機能を立てる)
- [おわりに](../99-epilogue/README.html#おわりに)
  - [著者](../99-epilogue/README.html#著者)
<!-- ここまで目次 -->

</nav>
</div>
