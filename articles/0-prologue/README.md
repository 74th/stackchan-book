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
- [目次](../0-prologue/README.html#目次)
- [1. DevContainerのアーキテクチャ](../1-architecture/README.html#1-devcontainerのアーキテクチャ)
  - [1.1. DevContainerとは](../1-architecture/README.html#11-devcontainerとは)
  - [1.2. DevContainerのアーキテクチャ](../1-architecture/README.html#12-devcontainerのアーキテクチャ)
  - [1.3. DevContainerの制約](../1-architecture/README.html#13-devcontainerの制約)
  - [1.4. DevContainerの利用開始には一定の準備が必要](../1-architecture/README.html#14-devcontainerの利用開始には一定の準備が必要)
- [2. DevContainerの構築を考える](../2-build_devcontainer/README.html#2-devcontainerの構築を考える)
  - [2.1. DevContainer構築に必要なものを考える](../2-build_devcontainer/README.html#21-devcontainer構築に必要なものを考える)
  - [2.2. コンテナの構成を考える](../2-build_devcontainer/README.html#22-コンテナの構成を考える)
  - [2.3. DevContainerコンテナ構築のフェーズを理解する](../2-build_devcontainer/README.html#23-devcontainerコンテナ構築のフェーズを理解する)
  - [2.4. よってどうするべきか](../2-build_devcontainer/README.html#24-よってどうするべきか)
- [3. DevContainer設定と、各IDE、CLIでの使い方](../3-tools/README.html#3-devcontainer設定と各idecliでの使い方)
  - [3.1. DevContainer構築の設定ファイル](../3-tools/README.html#31-devcontainer構築の設定ファイル)
  - [3.2. VS Code](../3-tools/README.html#32-vs-code)
  - [3.3. Cursor](../3-tools/README.html#33-cursor)
  - [3.4. JetBrains IDE](../3-tools/README.html#34-jetbrains-ide)
  - [3.5. DevContainer CLI](../3-tools/README.html#35-devcontainer-cli)
  - [3.6. GitHub Codespaces](../3-tools/README.html#36-github-codespaces)
  - [3.7. Docker Desktop以外のコンテナランタイムアプリケーションは使えるか](../3-tools/README.html#37-docker-desktop以外のコンテナランタイムアプリケーションは使えるか)
- [4. DevContainerの細かい使い方](../4-devcontainer_howto/README.html#4-devcontainerの細かい使い方)
  - [4.1. ファイルシステムへのアクセスが遅い問題への対処](../4-devcontainer_howto/README.html#41-ファイルシステムへのアクセスが遅い問題への対処)
  - [4.2. 非rootユーザを利用する](../4-devcontainer_howto/README.html#42-非rootユーザを利用する)
  - [4.3. Windowsで改行コードの差分が出る問題](../4-devcontainer_howto/README.html#43-windowsで改行コードの差分が出る問題)
  - [4.4. ホストに影響を与えること](../4-devcontainer_howto/README.html#44-ホストに影響を与えること)
  - [4.5. シークレットの持ち込み方](../4-devcontainer_howto/README.html#45-シークレットの持ち込み方)
  - [4.6. GitHubの認証情報の持ち込み方](../4-devcontainer_howto/README.html#46-githubの認証情報の持ち込み方)
  - [4.7. dotfilesの利用](../4-devcontainer_howto/README.html#47-dotfilesの利用)
  - [4.8. 個人の設定を使う](../4-devcontainer_howto/README.html#48-個人の設定を使う)
  - [4.9. ここで書かなかったこと](../4-devcontainer_howto/README.html#49-ここで書かなかったこと)
- [5. DevContainer Features](../5-devcontainer_features/README.html#5-devcontainer-features)
  - [5.1. DevContainer Featuresとは](../5-devcontainer_features/README.html#51-devcontainer-featuresとは)
  - [5.2. Featuresの使い方](../5-devcontainer_features/README.html#52-featuresの使い方)
  - [5.3. 有用なFeatures](../5-devcontainer_features/README.html#53-有用なfeatures)
  - [5.4. Featuresを自作する](../5-devcontainer_features/README.html#54-featuresを自作する)
- [6. DevContainer構築例](../6-samples/README.html#6-devcontainer構築例)
  - [6.1. Go](../6-samples/README.html#61-go)
  - [6.2. Python](../6-samples/README.html#62-python)
  - [6.3. Node.js](../6-samples/README.html#63-nodejs)
  - [6.4. DBをDocker Composeで立ち上げる](../6-samples/README.html#64-dbをdocker-composeで立ち上げる)
- [7. ネットワーク隔離環境](../7-network_dedicated_environment/README.html#7-ネットワーク隔離環境)
  - [7.1. LLMコーディングエージェントとセキュリティリスクの議論](../7-network_dedicated_environment/README.html#71-llmコーディングエージェントとセキュリティリスクの議論)
  - [7.2. DevContainerで必要なネットワーク通信](../7-network_dedicated_environment/README.html#72-devcontainerで必要なネットワーク通信)
  - [7.3. Docker Composeでネットワークを作り、ホストと分離する](../7-network_dedicated_environment/README.html#73-docker-composeでネットワークを作りホストと分離する)
  - [7.4. IP制限をする](../7-network_dedicated_environment/README.html#74-ip制限をする)
- [8. ローカルでのLLMコーディングエージェントでのDevContainerの利用](../8-local_agentic_coding/README.html#8-ローカルでのllmコーディングエージェントでのdevcontainerの利用)
  - [8.1. 考慮すること](../8-local_agentic_coding/README.html#81-考慮すること)
  - [8.2. Claude Code](../8-local_agentic_coding/README.html#82-claude-code)
  - [8.3. Codex CLI](../8-local_agentic_coding/README.html#83-codex-cli)
  - [8.4. Gemini CLI](../8-local_agentic_coding/README.html#84-gemini-cli)
  - [8.5. Copilot CLI](../8-local_agentic_coding/README.html#85-copilot-cli)
  - [8.6. Container Useを使う](../8-local_agentic_coding/README.html#86-container-useを使う)
  - [8.7. コンテナ隔離環境を使えなかったもの](../8-local_agentic_coding/README.html#87-コンテナ隔離環境を使えなかったもの)
- [9. クラウドLLMコーディングエージェントの環境セットアップ方法](../9-cloud_agentic_coding/README.html#9-クラウドllmコーディングエージェントの環境セットアップ方法)
  - [9.1. GitHub Copilot Coding Agent](../9-cloud_agentic_coding/README.html#91-github-copilot-coding-agent)
  - [9.2. Codex](../9-cloud_agentic_coding/README.html#92-codex)
  - [9.3. Jules](../9-cloud_agentic_coding/README.html#93-jules)
- [おわりに](../99-epilogue/README.html#おわりに)
  - [著者](../99-epilogue/README.html#著者)
<!-- ここまで目次 -->

</nav>
</div>
