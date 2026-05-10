# Memo

A lightweight, secure, and cross-platform memo/note-taking application built with Python and Tkinter. It features a system tray integration, local SQLite storage, AES/RSA encryption for sensitive data, and an optional blockchain data-persistence layer.

## Features

- **System Tray Integration**: Runs quietly in the background with a system tray icon.
- **Local Storage**: Automatically saves your memos to a local SQLite database (`memo.db`).
- **Data Encryption**: Support for AES (Fernet) and RSA encryption. You can selectively encrypt specific parts of your memos.
- **Optional Blockchain Upload**: Persist your memos on-chain (using Web3) for tamper-proof storage.
- **Cross-Platform**: Works on both Windows and Linux.

## Installation

### 1. Basic Installation

Clone the repository and install it as a standard PyPI package:

```bash
git clone https://github.com/kyle-meng/Memo.git
cd Memo
pip install .
```

### 2. With Blockchain Support

If you want to use the blockchain upload features, install the optional dependencies:

```bash
pip install .[blockchain]
```

## Configuration

The application requires a `.env` file in the directory where you run it. You can copy the provided `.env sample` to `.env`:

```bash
cp ".env sample" .env
```

**Configuration options:**
- `FOLD_TIME`: Time interval (in minutes) for folding/refreshing historical memos.
- `KEY_FILE`: Path to your encryption key file.
- `ENC_METHOD`: Encryption method to use (e.g., `AES` or `RSA`).
- `STRING_LENGTH`: Maximum string length allowed before skipping blockchain upload.
- `TO_BLOCKCHAIN`: Set to `True` to enable blockchain upload, or `False` to disable.

## Usage

Start the application by running the following command in your terminal:

```bash
memo
```

*(Note: Ensure your Python `Scripts` or `bin` directory is in your system's PATH).*

### Keyboard Shortcuts

When the application window is focused, you can use the following hotkeys:

- <kbd>Ctrl</kbd> + <kbd>S</kbd> : 保存 (Save the current memo)
- <kbd>Ctrl</kbd> + <kbd>F</kbd> : 搜索 (Search through historical memos)
- <kbd>Ctrl</kbd> + <kbd>L</kbd> : 列出所有 (List all historical memos)
- <kbd>Ctrl</kbd> + <kbd>R</kbd> : 加密 (Insert `<ENC><DEC>` tags to encrypt specific text)
- <kbd>Ctrl</kbd> + <kbd>B</kbd> : 退出 (Exit the application completely)
- <kbd>Alt</kbd> + <kbd>M</kbd> : 最小化 (Minimize to system tray)

### Encryption Workflow
When editing a memo, you can press <kbd>Ctrl</kbd> + <kbd>R</kbd> to insert `<ENC><DEC>`. Any text placed between these tags (e.g., `<ENC>My Secret<DEC>`) will be encrypted automatically upon saving using your configured `ENC_METHOD`. When you view historical memos, you can click on the encrypted text to enter your password and decrypt it.

## License
MIT License
