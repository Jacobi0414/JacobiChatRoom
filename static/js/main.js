// 建立Socket.IO连接
const socket = io();

// DOM元素
const messageForm = document.getElementById('messageForm');
const messageInput = document.getElementById('messageInput');
const messageArea = document.getElementById('messageArea');
const userList = document.getElementById('userList');
const imageInput = document.getElementById('imageInput');

// 当前用户名（将由服务器分配）
let currentUsername = '';

// 处理连接事件
socket.on('connect', () => {
    console.log('Connected to server');
    // 加载历史消息
    loadChatHistory();
});

// 处理断开连接事件
socket.on('disconnect', () => {
    console.log('Disconnected from server');
    addSystemMessage('与服务器断开连接，正在尝试重新连接...');
});

// 处理用户加入事件
socket.on('user_joined', (data) => {
    addSystemMessage(`${data.username} 加入了聊天室`);
});

// 处理用户离开事件
socket.on('user_left', (data) => {
    addSystemMessage(`${data.username} 离开了聊天室`);
});

// 处理用户列表更新
socket.on('update_users', (data) => {
    updateUserList(data.users);
});

// 处理新消息
socket.on('message', (data) => {
    addMessage(data);
});

// 处理错误消息
socket.on('error', (data) => {
    addSystemMessage(`错误: ${data.message}`);
});

// 添加重连功能
socket.on('reconnect', (attemptNumber) => {
    console.log('Reconnected to server');
    addSystemMessage('重新连接成功！');
    // 重新加载消息历史和用户列表
    loadChatHistory();
});

socket.on('reconnect_error', (error) => {
    console.error('Reconnection error:', error);
    addSystemMessage('重新连接失败，请刷新页面重试');
});

// 发送消息
messageForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (message) {
        try {
            messageInput.disabled = true;
            socket.emit('message', { message: message });
            messageInput.value = '';
        } catch (error) {
            console.error('Error sending message:', error);
            addSystemMessage('消息发送失败，请重试');
        } finally {
            messageInput.disabled = false;
            messageInput.focus();
        }
    }
});

// 处理图片上传
imageInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // 检查文件类型
    if (!file.type.startsWith('image/')) {
        addSystemMessage('只能上传图片文件');
        return;
    }

    // 检查文件大小（最大16MB）
    if (file.size > 16 * 1024 * 1024) {
        addSystemMessage('图片大小不能超过16MB');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('上传失败');
        }

        const data = await response.json();
        // 发送图片消息
        socket.emit('image_message', { url: data.url });
        
        // 清除input
        imageInput.value = '';
    } catch (error) {
        console.error('Error uploading image:', error);
        addSystemMessage('图片上传失败');
    }
});

// 消息输入增强
messageInput.addEventListener('keydown', (e) => {
    // Ctrl+Enter 插入换行
    if (e.ctrlKey && e.key === 'Enter') {
        e.preventDefault();
        const start = messageInput.selectionStart;
        const end = messageInput.selectionEnd;
        messageInput.value = messageInput.value.substring(0, start) + '\n' + messageInput.value.substring(end);
        messageInput.selectionStart = messageInput.selectionEnd = start + 1;
        return;
    }
    
    // Enter键发送消息，Shift+Enter换行
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        messageForm.dispatchEvent(new Event('submit'));
        return;
    }
    
    // Tab键插入4个空格
    if (e.key === 'Tab') {
        e.preventDefault();
        const start = messageInput.selectionStart;
        const end = messageInput.selectionEnd;
        messageInput.value = messageInput.value.substring(0, start) + '    ' + messageInput.value.substring(end);
        messageInput.selectionStart = messageInput.selectionEnd = start + 4;
    }
});

// 添加粘贴图片支持
messageInput.addEventListener('paste', async (e) => {
    const items = (e.clipboardData || e.originalEvent.clipboardData).items;
    
    for (const item of items) {
        if (item.type.indexOf('image') === 0) {
            e.preventDefault();
            const file = item.getAsFile();
            
            // 检查文件大小
            if (file.size > 16 * 1024 * 1024) {
                addSystemMessage('图片大小不能超过16MB');
                return;
            }
            
            try {
                const formData = new FormData();
                formData.append('file', file);
                
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error('上传失败');
                }
                
                const data = await response.json();
                socket.emit('image_message', { url: data.url });
            } catch (error) {
                console.error('Error uploading pasted image:', error);
                addSystemMessage('图片上传失败');
            }
            break;
        }
    }
});

// 添加拖放图片支持
messageArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.stopPropagation();
    messageArea.classList.add('drag-over');
});

messageArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    e.stopPropagation();
    messageArea.classList.remove('drag-over');
});

messageArea.addEventListener('drop', async (e) => {
    e.preventDefault();
    e.stopPropagation();
    messageArea.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    
    for (const file of files) {
        if (file.type.startsWith('image/')) {
            if (file.size > 16 * 1024 * 1024) {
                addSystemMessage('图片大小不能超过16MB');
                continue;
            }
            
            try {
                const formData = new FormData();
                formData.append('file', file);
                
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error('上传失败');
                }
                
                const data = await response.json();
                socket.emit('image_message', { url: data.url });
            } catch (error) {
                console.error('Error uploading dropped image:', error);
                addSystemMessage('图片上传失败');
            }
        }
    }
});

// 加载聊天历史
async function loadChatHistory() {
    try {
        const response = await fetch('/history');
        const messages = await response.json();
        messages.forEach(addMessage);
        scrollToBottom();
    } catch (error) {
        console.error('Error loading chat history:', error);
        addSystemMessage('无法加载聊天历史');
    }
}

// 添加消息到聊天区域
function addMessage(data) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${data.username === currentUsername ? 'sent' : 'received'}`;
    
    const usernameDiv = document.createElement('div');
    usernameDiv.className = 'username';
    usernameDiv.textContent = data.username;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    // 使用marked处理Markdown语法
    contentDiv.innerHTML = marked.parse(data.message);
    
    const timestampDiv = document.createElement('div');
    timestampDiv.className = 'timestamp';
    timestampDiv.textContent = data.timestamp;
    
    messageDiv.appendChild(usernameDiv);
    messageDiv.appendChild(contentDiv);
    messageDiv.appendChild(timestampDiv);
    
    messageArea.appendChild(messageDiv);
    scrollToBottom();
}

// 添加系统消息
function addSystemMessage(message) {
    const systemDiv = document.createElement('div');
    systemDiv.className = 'system-message';
    systemDiv.textContent = message;
    messageArea.appendChild(systemDiv);
    scrollToBottom();
}

// 更新用户列表
function updateUserList(users) {
    userList.innerHTML = '';
    users.forEach(username => {
        const userItem = document.createElement('div');
        userItem.className = 'list-group-item';
        userItem.textContent = username;
        userList.appendChild(userItem);
    });
}

// 滚动到底部
function scrollToBottom() {
    messageArea.scrollTop = messageArea.scrollHeight;
}

// 防止XSS攻击的辅助函数
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// 初始化marked配置
marked.setOptions({
    breaks: true,
    sanitize: true
}); 