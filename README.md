# Ticket-Bot

[![zh](https://img.shields.io/badge/lang-中文-blue)](https://github.com/wayneclub/Subtitle-Downloader/blob/main/README.zh-Hant.md) [![python](https://img.shields.io/badge/python-3.8-blue)](https://www.python.org/downloads/)

**NON-COMMERCIAL USE ONLY**

Ticket Bot supports auto buying ticket from [THSRC](https://irs.thsrc.com.tw/IMINT/?utm_source=thsrc&utm_medium=textlink&utm_term=booking).

## DESCRIPTION

Ticket-Bot is a command-line program which could auto buy tickets from websites. It requires [Python 3.8+](https://www.python.org/downloads/), and [NodeJS](https://nodejs.org/en/download). It should work on Linux, on Windows or on macOS. This project is only for personal research and language learning.

## INSTALLATION

- Linux, macOS:

```bash
pip install -r requriements
```

- Windows: Execute `install_requirements.bat`

## USAGE

### Online **_(Colab environment is in the US, if you want to use in other region please execute on local)_**

1. Save a copy in Drive
2. Connect Colab
3. Install the requirements (Click 1st play button)
4. Depend on the service modify the text field.
5. Cick the play button, and start buying tickets.

<a href="https://colab.research.google.com/drive/1NUeypohFO___pW9Ou6lvOPUfn_tCoF9N?usp=sharing" target="_blank"><img src="https://colab.research.google.com/assets/colab-badge.svg" title="Open this file in Google Colab" alt="Colab"/></a>

### Local

1. Depend on the service and modify `Ticket-Bot/user_config.toml`

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

2. Execute the program with command line or `Ticket-Bot.bat`

    ```bash
    python ticket_bot.py service [OPTIONS]
    ```

## OPTIONS

```text
  -h, --help                    show this help message and exit

  -l, --list                    list the tickets

  -a, --auto                    auto buy tickets (train has discount & fastest)

  -locale, --locale             interface language

  -p, --proxy                   proxy

  -d, --debug                   enable debug logging

  -v, --version                 app's version
```

## More Examples

- Buy ticket from THSRC

```bash
python ticket_bot.py thsrc
```

## FAQ

- Any issue during buying tickets, upload the screenshots and log files (Please provide service name and the command).


## Appendix

