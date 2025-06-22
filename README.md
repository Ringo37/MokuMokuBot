# MokuMokuBot

ただ、特定のボイスチャンネルの滞在時間を記録するだけのボット

## 使い方

ディスコードボットのトークンとチャンネルのIDを取得して.envに入れる

Linux and Mac

```bash
cp .env.example .env
python3 -m venv venv
source/venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

Windows

```bash
cp .env.example .env
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
