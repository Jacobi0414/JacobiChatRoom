# 🌟 JacobiChatRoom

> A real-time web chat room application based on Flask and WebSocket. Users can join the chat without login, and the system will automatically assign random usernames.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![WebSocket](https://img.shields.io/badge/WebSocket-Enabled-brightgreen.svg)](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

<div align="center">
    <img src="https://raw.githubusercontent.com/Jacobi0414/JacobiChatRoom/main/screenshots/preview.png" alt="Preview" width="600">
</div>

## ✨ Features

- 🚀 Built with Python 3.11 and Flask framework
- 💬 Real-time chat functionality using Flask-SocketIO
- 👤 Automatic random username assignment
- 📝 Chat history storage
- 👥 Online users list display
- 📱 Responsive web design
- 🖼️ Image sharing support
- ✍️ Full Markdown syntax support in chat

## 🛠️ Tech Stack

### Backend
- **Python 3.11**
- **Flask** - Web framework
- **Flask-SocketIO** - WebSocket support
- **SQLite** - Message history storage
- **Markdown** - Chat content formatting

### Frontend
- **HTML5**
- **CSS3**
- **JavaScript**
- **Socket.IO Client**
- **Bootstrap 5** - Responsive design

## 📁 Project Structure

\`\`\`
chatroom/
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── templates/
│   └── index.html
├── data/
│   ├── chat_history.db
│   └── names.txt
├── main.py
├── config.py
├── requirements.txt
└── README.md
\`\`\`

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Installation

1. Clone the repository:
   \`\`\`bash
   git clone https://github.com/Jacobi0414/JacobiChatRoom.git
   cd JacobiChatRoom
   \`\`\`

2. Install dependencies:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. Run the application:
   \`\`\`bash
   python main.py
   \`\`\`

4. Access the application:
   Open your browser and visit \`http://localhost:5000\`

## ⚙️ Configuration

Key configuration items in \`config.py\`:

| Configuration | Description | Default |
|--------------|-------------|---------|
| HOST | Server host | 0.0.0.0 |
| PORT | Server port | 5000 |
| DEBUG | Debug mode | True |
| SECRET_KEY | Flask secret key | your-secret-key-here |
| MAX_CONTENT_LENGTH | Max upload size | 16MB |

## 📝 Usage Guide

1. **Joining the Chat**
   - Open the webpage
   - A random username will be automatically assigned
   - Start chatting immediately

2. **Sending Messages**
   - Type your message in the input box
   - Press Enter to send
   - Use Shift+Enter or Ctrl+Enter for new line

3. **Markdown Support**
   ```markdown
   # Heading 1
   ## Heading 2
   **Bold text**
   *Italic text*
   - List item
   1. Numbered item
   > Quote
   \`\`\`python
   print("Code block")
   \`\`\`
   ```

4. **Image Sharing**
   - Click the image button
   - Drag and drop images
   - Paste images from clipboard
   - Supported formats: PNG, JPG, JPEG, GIF

## 🎯 Random Username System

The system assigns unique usernames from a predefined pool including:
- Poetry characters
- Historical figures
- Nature elements

> Each username is guaranteed to be unique in the current session.

## 🗺️ Development Roadmap

- [x] Basic chat functionality
- [x] Random username system
- [x] Message history storage
- [x] Online users list
- [x] UI enhancement
- [x] Emoji support
- [x] Image sharing
- [x] Markdown support
- [ ] User authentication (optional)
- [ ] Private messaging
- [ ] Room management
- [ ] File sharing

## ⚠️ Important Notes

1. Security Considerations
   - No user authentication system
   - Recommended for use in controlled environments
   - Regular database cleanup recommended

2. Performance Tips
   - Clean database periodically
   - Monitor WebSocket connections
   - Optimize image uploads

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create your feature branch (\`git checkout -b feature/AmazingFeature\`)
3. Commit your changes (\`git commit -m 'Add some AmazingFeature'\`)
4. Push to the branch (\`git push origin feature/AmazingFeature\`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flask and its extensions
- Socket.IO
- Bootstrap team
- All contributors

---

<div align="center">
    Made with ❤️ by <a href="https://github.com/Jacobi0414">Jacobi</a>
</div>
