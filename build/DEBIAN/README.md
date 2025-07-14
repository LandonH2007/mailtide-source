# Mailtide v1.0.0

A lightweight Python-based CLI email client. Mailtide allows you to browse and manage IMAP inboxes via terminal aswell as send emails.

## Features

- View and browse folders from major IMAP providers
- Compose and send emails with attachments
- Move emails between folders
- Download attachments to disk
- Works with most major email providers:
    - Gmail, Yahoo, Outlook, iCloud, ProtonMail, Zoho, GMX, Yandex, FastMail, and more
- Terminal User Interface powered by 'curses'
- Plain text and HTML parsing support

---

## Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/mailtide.git
cd mailtide

# Install the .deb package
sudo dpkg -i mailtide_v1.0.0.deb

# If any dependencies are missing, fix them
sudo apt --fix-broken install
```

Then run it:
```bash
mailtide
```

## Controls
### Main Menu
| Key        | Action              |
|------------|-------------------------------|
| `Shift+S`        | Sign in                       |
| `Shift+O`        | Sign out                      |
| `Shift+F`        | Enter folder                  |
| `Shift+E`        | Load and list messages        |
| `Shift+R`        | Read email                    |
| `Shift+M`        | Move email                    |
| `Shift+D`        | Download attachments          |
| `Shift+C`        | Compose message               |
| `Shift+Q`        | Quit                          |
| `Shift+r`        | Refresh current folder        |
| `Shift+V` / `Shift+T`  | Page down / up                |

### Composition

| Key   | Action                      |
|--------------|-----------------------------|
| `^s`         | Save as draft               |
| `^l`         | Load draft                  |
| `^g`         | Send email                  |
| `^a`         | Attach file                 |
| `^x`         | Exit compose mode           |
| `↑` / `↓`    | Navigate message lines      |
| `Enter`      | New line                    |
| `Tab`        | Insert tab character        |

## App Passwords & Security
If you're using Gmail, Yahoo, or other services with 2FA, you may need to generate an app-specific password and use it instead of your normal password.
Your password is not saved between sessions.

## License
This project is licensed under the [MIT License](https://mit-license.org/).

## Contributing
Pull requests and feedback are welcome.

## Author
### Landon Haught
Made with a lot of frustration and trial & error,
