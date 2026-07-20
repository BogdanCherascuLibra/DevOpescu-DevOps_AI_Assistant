const state = {
    username: "",
    conversationId: null,
    conversations: []
};

const elements = {
    usernameInput: document.getElementById("username-input"),
    loginButton: document.getElementById("login-button"),

    newConversationButton: document.getElementById(
        "new-conversation-button"
    ),

    conversationList: document.getElementById("conversation-list"),

    conversationTitle: document.getElementById("conversation-title"),
    conversationStatus: document.getElementById("conversation-status"),

    messagesContainer: document.getElementById("messages-container"),

    messageInput: document.getElementById("message-input"),
    sendButton: document.getElementById("send-button"),

    exportButton: document.getElementById("export-button"),
    deleteButton: document.getElementById("delete-button"),

    importFile: document.getElementById("import-file"),

    inputTokens: document.getElementById("input-tokens"),
    outputTokens: document.getElementById("output-tokens"),
    totalCost: document.getElementById("total-cost"),

    notification: document.getElementById("notification")
};


async function apiRequest(url, options = {}) {
    const response = await fetch(url, options);

    if (!response.ok) {
        let message = "A apărut o eroare.";

        try {
            const data = await response.json();
            message = data.detail || message;
        } catch {
            message = `Eroare HTTP: ${response.status}`;
        }

        throw new Error(message);
    }

    return response;
}


function showNotification(message, type = "success") {
    elements.notification.textContent = message;
    elements.notification.className = `notification visible ${type}`;

    window.clearTimeout(showNotification.timeoutId);

    showNotification.timeoutId = window.setTimeout(() => {
        elements.notification.className = "notification";
    }, 3000);
}


function encodePath(value) {
    return encodeURIComponent(value);
}


function setConversationControls(enabled) {
    elements.messageInput.disabled = !enabled;
    elements.sendButton.disabled = !enabled;
    elements.exportButton.disabled = !enabled;
    elements.deleteButton.disabled = !enabled;
}


function resetAnalytics() {
    elements.inputTokens.textContent = "0";
    elements.outputTokens.textContent = "0";
    elements.totalCost.textContent = "$0.000000";
}


function displayWelcomeMessage() {
    elements.messagesContainer.innerHTML = `
        <div class="welcome-card">
            <div class="welcome-icon">&gt;_</div>

            <h3>Salut, sunt DevOpescu</h3>

            <p>
                Te pot ajuta cu Docker, Linux, servicii,
                rețelistică, CI/CD și diagnosticare DevOps.
            </p>
        </div>
    `;
}


function formatDate(value) {
    if (!value) {
        return "";
    }

    const date = new Date(
        value.endsWith("Z") ? value : `${value}Z`
    );

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString("ro-RO", {
        dateStyle: "short",
        timeStyle: "short"
    });
}


function renderConversations() {
    elements.conversationList.innerHTML = "";

    if (state.conversations.length === 0) {
        elements.conversationList.innerHTML = `
            <p class="empty-list">
                Nu există conversații.
            </p>
        `;

        return;
    }

    for (const conversation of state.conversations) {
        const button = document.createElement("button");

        button.className = "conversation-item";

        if (conversation.id === state.conversationId) {
            button.classList.add("active");
        }

        const title = document.createElement("span");
        title.className = "conversation-item-title";
        title.textContent = conversation.title;

        const date = document.createElement("span");
        date.className = "conversation-item-date";
        date.textContent = formatDate(conversation.updated_at);

        button.append(title, date);

        button.addEventListener("click", () => {
            openConversation(conversation.id);
        });

        elements.conversationList.appendChild(button);
    }
}


function addMessage(role, content) {
    const wrapper = document.createElement("div");
    wrapper.className = `message ${role}`;

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";

    const roleLabel = document.createElement("span");
    roleLabel.className = "message-role";
    roleLabel.textContent = role === "user"
        ? state.username
        : "DevOpescu";

    const text = document.createElement("div");

    if (role === "assistant") {
        const rawHtml = marked.parse(content);

        text.innerHTML = DOMPurify.sanitize(rawHtml, {
        USE_PROFILES: { html: true }
            });
    } else {
        text.textContent = content;
    }

    bubble.append(roleLabel, text);
    wrapper.appendChild(bubble);

    elements.messagesContainer.appendChild(wrapper);

    elements.messagesContainer.scrollTop =
        elements.messagesContainer.scrollHeight;

    return wrapper;
}


function addTypingIndicator() {
    const wrapper = addMessage(
        "assistant",
        "Analizez problema..."
    );

    wrapper.classList.add("typing-message");

    return wrapper;
}


async function login() {
    const username = elements.usernameInput.value.trim();

    if (!username) {
        showNotification(
            "Introdu un username.",
            "warning"
        );

        return;
    }

    state.username = username;
    state.conversationId = null;

    localStorage.setItem(
        "devopescu_username",
        username
    );

    elements.newConversationButton.disabled = false;

    setConversationControls(false);
    resetAnalytics();
    displayWelcomeMessage();

    elements.conversationTitle.textContent = "DevOps Assistant";
    elements.conversationStatus.textContent =
        `Conectat ca ${username}`;

    try {
        await loadConversations();

        showNotification(
            `Bun venit, ${username}.`
        );
    } catch (error) {
        showNotification(
            error.message,
            "error"
        );
    }
}


async function loadConversations() {
    const response = await apiRequest(
        `/users/${encodePath(state.username)}/conversations`
    );

    state.conversations = await response.json();

    renderConversations();
}


async function createConversation() {
    if (!state.username) {
        return;
    }

    const title = window.prompt(
        "Titlul conversației:",
        "New conversation"
    );

    if (title === null) {
        return;
    }

    const normalizedTitle = title.trim() || "New conversation";

    try {
        const response = await apiRequest(
            `/users/${encodePath(state.username)}/conversations`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    title: normalizedTitle
                })
            }
        );

        const data = await response.json();

        await loadConversations();
        await openConversation(data.conversation_id);

        showNotification(
            "Conversația a fost creată."
        );
    } catch (error) {
        showNotification(
            error.message,
            "error"
        );
    }
}


async function openConversation(conversationId) {
    try {
        const response = await apiRequest(
            `/users/${encodePath(state.username)}` +
            `/conversations/${encodePath(conversationId)}`
        );

        const data = await response.json();

        state.conversationId = conversationId;

        elements.conversationTitle.textContent =
            data.conversation.title;

        elements.conversationStatus.textContent =
            `Actualizată: ${formatDate(
                data.conversation.updated_at
            )}`;

        elements.messagesContainer.innerHTML = "";

        if (data.messages.length === 0) {
            displayWelcomeMessage();
        } else {
            for (const message of data.messages) {
                addMessage(
                    message.role,
                    message.content
                );
            }
        }

        setConversationControls(true);
        updateAnalytics(data.usage);
        renderConversations();

        elements.messageInput.focus();
    } catch (error) {
        showNotification(
            error.message,
            "error"
        );
    }
}


async function sendMessage() {
    const message = elements.messageInput.value.trim();

    if (
        !message ||
        !state.username ||
        !state.conversationId
    ) {
        return;
    }

    elements.messageInput.value = "";
    autoResizeTextarea();

    elements.sendButton.disabled = true;
    elements.messageInput.disabled = true;

    const welcomeCard = elements.messagesContainer.querySelector(
        ".welcome-card"
    );

    if (welcomeCard) {
        welcomeCard.remove();
    }

    addMessage("user", message);

    const typingIndicator = addTypingIndicator();

    try {
        const response = await apiRequest(
            `/users/${encodePath(state.username)}` +
            `/conversations/${encodePath(state.conversationId)}` +
            "/messages",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message
                })
            }
        );

        const data = await response.json();

        typingIndicator.remove();

        addMessage(
            "assistant",
            data.response
        );

        updateAnalytics(data.usage);

        await loadConversations();
    } catch (error) {
        typingIndicator.remove();

        addMessage(
            "assistant",
            `Eroare: ${error.message}`
        );

        showNotification(
            error.message,
            "error"
        );
    } finally {
        elements.sendButton.disabled = false;
        elements.messageInput.disabled = false;
        elements.messageInput.focus();
    }
}


function updateAnalytics(usage) {
    if (!usage) {
        return;
    }

    elements.inputTokens.textContent =
        usage.input_tokens ?? 0;

    elements.outputTokens.textContent =
        usage.output_tokens ?? 0;

    const cost = Number(
        usage.total_cost ?? 0
    );

    elements.totalCost.textContent =
        `$${cost.toFixed(6)}`;
}


async function deleteConversation() {
    if (!state.conversationId) {
        return;
    }

    const confirmed = window.confirm(
        "Sigur vrei să ștergi conversația?"
    );

    if (!confirmed) {
        return;
    }

    try {
        await apiRequest(
            `/users/${encodePath(state.username)}` +
            `/conversations/${encodePath(state.conversationId)}`,
            {
                method: "DELETE"
            }
        );

        state.conversationId = null;

        setConversationControls(false);
        resetAnalytics();
        displayWelcomeMessage();

        elements.conversationTitle.textContent =
            "DevOps Assistant";

        elements.conversationStatus.textContent =
            "Conversația a fost ștearsă.";

        await loadConversations();

        showNotification(
            "Conversația a fost ștearsă."
        );
    } catch (error) {
        showNotification(
            error.message,
            "error"
        );
    }
}


function exportConversation() {
    if (!state.conversationId) {
        return;
    }

    const url =
        `/users/${encodePath(state.username)}` +
        `/conversations/${encodePath(state.conversationId)}` +
        "/export";

    window.location.href = url;
}


async function importConversation(file) {
    if (!state.username || !file) {
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await apiRequest(
            `/users/${encodePath(state.username)}` +
            "/conversations/import",
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        await loadConversations();
        await openConversation(data.conversation_id);

        showNotification(
            "Conversația a fost importată."
        );
    } catch (error) {
        showNotification(
            error.message,
            "error"
        );
    } finally {
        elements.importFile.value = "";
    }
}


function autoResizeTextarea() {
    elements.messageInput.style.height = "auto";

    elements.messageInput.style.height =
        `${Math.min(
            elements.messageInput.scrollHeight,
            170
        )}px`;
}


elements.loginButton.addEventListener(
    "click",
    login
);

elements.usernameInput.addEventListener(
    "keydown",
    event => {
        if (event.key === "Enter") {
            login();
        }
    }
);

elements.newConversationButton.addEventListener(
    "click",
    createConversation
);

elements.sendButton.addEventListener(
    "click",
    sendMessage
);

elements.messageInput.addEventListener(
    "input",
    autoResizeTextarea
);

elements.messageInput.addEventListener(
    "keydown",
    event => {
        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {
            event.preventDefault();
            sendMessage();
        }
    }
);

elements.deleteButton.addEventListener(
    "click",
    deleteConversation
);

elements.exportButton.addEventListener(
    "click",
    exportConversation
);

elements.importFile.addEventListener(
    "change",
    event => {
        const [file] = event.target.files;
        importConversation(file);
    }
);


const savedUsername = localStorage.getItem(
    "devopescu_username"
);

if (savedUsername) {
    elements.usernameInput.value = savedUsername;
}