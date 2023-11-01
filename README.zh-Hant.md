# 訂票機器人

[![zh](https://img.shields.io/badge/lang-中文-blue)](https://github.com/wayneclub/Ticket-Bot/blob/main/README.md) [![python](https://img.shields.io/badge/python-3.8-blue)](https://www.python.org/downloads/)

**禁止營利使用，只限個人研究使用**

訂票機器人目前支援自動購買 [台灣高鐵](https://irs.thsrc.com.tw/IMINT/)車票。

## 說明

訂票機器人是一個方便幫您從各個平台自動購買票券的小幫手。需要安裝 [Python 3.8+](https://www.python.org/downloads/) 和 [NodeJS](https://nodejs.org/en/download)。可以在 Linux、Windows 或 macOS 上執行。

## 安裝方式

- Linux, macOS:

```bash
pip install -r requriements
```

- Windows: 執行 `install_requirements.bat`

## 使用方式

### 線上執行 **_(Colab環境在美國，如果訪問受限制，請在本機執行)_**

1. 複製一份到自己的雲端
2. 連結 Colab
3. 環境設定，安裝必要程式（執行第ㄧ個按鈕）
4. 依照不同購票平台填入各項購票資料
5. 填完後按下執行，會自動買票，複製成功購票連結到瀏覽器即可繳費

<a href="https://colab.research.google.com/drive/1NUeypohFO___pW9Ou6lvOPUfn_tCoF9N?usp=sharing" target="_blank"><img src="https://colab.research.google.com/assets/colab-badge.svg" title="Open this file in Google Colab" alt="Colab"/></a>

### Local

1. 根據不同購票平台服務填寫購票參數 `Ticket-Bot/user_config.toml`

    ```toml
    [fields]

    [fields.THSRC]
    id = ''             # ROC ID No. 身分證字號 (e.g. AXXXXXXXXX)
    start-station = ''  # Start-station 出發站 (e.g. Taipei)
    dest-station = ''   # Dest-station 抵達站 (e.g. Tainan)
    outbound-date = ''  # Outbound date 出發日期 (e.g. 2023-01-01)
    outbound-time = ''  # Outbound time 出發時間 (e.g. 09:00)
    inbound-time = ''   # Inbound time 抵達時間 (e.g. 12:00)
    preferred-seat = '' # Preferred seat 座位偏好 (e.g. window/aisle)
    car-type = ''       # Car Type 車廂類型 (e.g. normal/business)
    train-no = ''       # Train No. 車次 (e.g. 001)
    email = ''          # E-mail for notification
    phone = ''          # Phone number for SMS notification 手機號碼
    tgo-id = ''         # TSHRC member ID TGO會員ID (e.g. AXXXXXXXXX)

    [fields.THSRC.ticket]
    adult = 1    # 全票
    child = 0    # 孩童票 (6-11)
    disabled = 0 # 愛心票
    elder = 0    # 敬老票
    college = 0  # 大學生票
    ```

2. 使用python指令執行程式或執行`Ticket-Bot.bat`

    ```bash
    python ticket_bot.py service [OPTIONS]
    ```

## 參數

```text
  -h, --help                    show this help message and exit

  -l, --list                    list the tickets

  -a, --auto                    auto buy tickets (train has discount & fastest)

  -locale, --locale             interface language

  -p, --proxy                   proxy

  -d, --debug                   enable debug logging

  -v, --version                 app's version
```

## 更多範例

- 從台灣高鐵訂票

```bash
python ticket_bot.py thsrc
```

## FAQ

- 購票過程中出現任何問題，請上傳截圖和日誌檔案（請提供服務名稱和命令）。

## Appendix
