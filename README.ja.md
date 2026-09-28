# 花火 (Hanabi)

[English](README.md)

カードゲーム「花火」のマルチプレイヤー版です。Python のサーバーと Pygame のクライアントで動き、ロビーとセーブに対応しています。表示は英語で始まり、`L` キーで英語、ドイツ語、日本語の順に切り替わります。

## 起動

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

`src` フォルダで、ターミナルを二つ開きます。

```
python -m hanabi.core.server
python -m hanabi.core.client_launcher
```

プレイヤーを増やすときは、クライアントをもう一度起動します。

## 操作

- 言語切替（英語、ドイツ語、日本語）: `L`
- ナビゲーションメニュー: `Esc`
- セーブ: `S`
- セーブを読み込めるのは、同じプレイヤーがロビーの同じ席にいるときだけです

## 図

PlantUML ファイル（`*.puml`）は、中核、画面、メッセージの流れを表します。SVG はその描画結果です。`Anleitung zum Start von Hanabi.pdf` はドイツ語の起動手順です。
