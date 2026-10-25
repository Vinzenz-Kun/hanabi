# 花火 (Hanabi)

[English](README.md) · [Deutsch](README.de.md) · **日本語**

カードゲーム「花火」のマルチプレイヤー版です。Python のサーバーと Pygame のクライアントで動き、ロビーとセーブに対応しています。表示は英語で始まり、`L` キーで英語、ドイツ語、日本語の順に切り替わります。

## 起動

`dist/Hanabi.exe` をダブルクリックします。ウィンドウは開いたままです。サーバーを一度起動し、プレイヤーごとにクライアントを起動します。それぞれ別ウィンドウで開きます。ランチャーを閉じても、サーバーとクライアントは動き続けます。

このフォルダで exe を作るには:

```
pip install pyinstaller
pyinstaller Hanabi.spec
```

ソースから動かすときは、`src` フォルダで:

```
python -m hanabi.launcher
```

個別に起動する場合も `src` から:

```
python -m hanabi.core.server
python -m hanabi.core.client_launcher
```

## 操作

- 言語切替（英語、ドイツ語、日本語）: `L`
- ナビゲーションメニュー: `Esc`
- セーブ: `S`
- セーブを読み込めるのは、同じプレイヤーがロビーの同じ席にいるときだけです

## 図

PlantUML ファイル（`*.puml`）は、中核、画面、メッセージの流れを表します。SVG はその描画結果です。`Anleitung zum Start von Hanabi.pdf` はドイツ語の起動手順です。
