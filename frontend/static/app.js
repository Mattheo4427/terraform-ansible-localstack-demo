const list = document.getElementById("todo-list");
const statusInd = document.getElementById("status-indicator");
const createBtn = document.getElementById("create-btn");
const newTitleInput = document.getElementById("new-title");

let isLoading = false;
let editingId = null;
let retryCount = 0;
const maxRetries = 10;

function setStatus(text, type = "") {
    statusInd.innerHTML = type === "loading" 
        ? `<span class="spinner"></span> ${text}`
        : type === "connecting"
        ? `<span class="spinner"></span> ${text}`
        : text;
    statusInd.className = type;
}

async function api(endpoint, method = "GET", body = null) {
    const url = window.backendUrl ? `${window.backendUrl}${endpoint}` : endpoint;
    try {
        const opts = { 
            method, 
            headers: { "Content-Type": "application/json" },
            mode: "cors"
        };
        if (body) opts.body = JSON.stringify(body);
        const res = await fetch(url, opts);
        
        if (!res.ok) {
            throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        }
        
        // Reset retry count on success
        retryCount = 0;
        
        if (method === "DELETE" || res.status === 204) {
            return true;
        }
        
        const text = await res.text();
        return text ? JSON.parse(text) : true;
    } catch (err) {
        console.error("API Error:", err);
        
        // Show connecting message with retry info
        if (retryCount < maxRetries) {
            retryCount++;
            setStatus(`Connecting to backend... (attempt ${retryCount}/${maxRetries})`, "connecting");
            
            // Retry after delay
            await new Promise(resolve => setTimeout(resolve, 2000));
            return api(endpoint, method, body);
        } else {
            setStatus("Connection failed - Backend unavailable", "error");
        }
        return null;
    }
}

function renderEmptyState() {
    list.innerHTML = `
        <div class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                <path d="M9 14l2 2 4-4"/>
            </svg>
            <p>No tasks yet. Add one above!</p>
        </div>
    `;
}

function createTaskElement(todo) {
    const li = document.createElement("li");
    li.className = todo.done ? "done" : "";
    li.dataset.id = todo.id;
    
    // Checkbox
    const label = document.createElement("label");
    label.className = "custom-checkbox";
    
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = todo.done;
    checkbox.onchange = () => toggleDone(todo);
    
    const checkmark = document.createElement("span");
    checkmark.className = "checkmark";
    
    label.append(checkbox, checkmark);
    
    // Text (editable)
    const text = document.createElement("span");
    text.className = "text";
    text.textContent = todo.title || "Untitled task";
    text.ondblclick = () => startEdit(todo, text, li);
    
    // Action buttons
    const actions = document.createElement("div");
    actions.className = "actions";
    
    const editBtn = document.createElement("button");
    editBtn.className = "edit-btn";
    editBtn.title = "Edit task";
    editBtn.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
        </svg>
    `;
    editBtn.onclick = (e) => {
        e.stopPropagation();
        startEdit(todo, text, li);
    };
    
    const delBtn = document.createElement("button");
    delBtn.className = "delete-btn";
    delBtn.title = "Delete task";
    delBtn.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2m3 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6h14z"/>
        </svg>
    `;
    delBtn.onclick = (e) => {
        e.stopPropagation();
        remove(todo.id, li);
    };
    
    actions.append(editBtn, delBtn);
    li.append(label, text, actions);
    
    return li;
}

function startEdit(todo, textElement, liElement) {
    if (editingId) return; // Already editing something
    
    editingId = todo.id;
    liElement.classList.add("editing");
    
    const input = document.createElement("input");
    input.type = "text";
    input.className = "edit-input";
    input.value = todo.title;
    input.maxLength = 200;
    
    const saveEdit = async () => {
        const newTitle = input.value.trim();
        if (newTitle && newTitle !== todo.title) {
            await updateTask(todo.id, newTitle, todo.done);
        } else {
            cancelEdit(textElement, liElement, todo.title);
        }
    };
    
    input.onblur = saveEdit;
    input.onkeydown = (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            saveEdit();
        } else if (e.key === "Escape") {
            cancelEdit(textElement, liElement, todo.title);
        }
    };
    
    textElement.replaceWith(input);
    input.focus();
    input.select();
}

function cancelEdit(textElement, liElement, originalTitle) {
    editingId = null;
    liElement.classList.remove("editing");
    
    const text = document.createElement("span");
    text.className = "text";
    text.textContent = originalTitle;
    
    const input = liElement.querySelector(".edit-input");
    if (input) {
        input.replaceWith(text);
    }
}

async function updateTask(id, title, done) {
    setStatus("Saving...", "loading");
    const result = await api(`/api/todos/${id}`, "PUT", { title, done });
    editingId = null;
    if (result) {
        render();
    }
}

async function toggleDone(todo) {
    const result = await api(`/api/todos/${todo.id}`, "PUT", { 
        title: todo.title, 
        done: !todo.done 
    });
    if (result) {
        render();
    }
}

async function remove(id, liElement) {
    if (liElement) {
        liElement.classList.add("removing");
        await new Promise(r => setTimeout(r, 200));
    }
    
    const result = await api(`/api/todos/${id}`, "DELETE");
    if (result) {
        render();
    }
}

async function create() {
    const title = newTitleInput.value.trim();
    if (!title || isLoading) return;
    
    isLoading = true;
    createBtn.disabled = true;
    setStatus("Adding...", "loading");
    
    const result = await api("/api/todos", "POST", { title });
    
    isLoading = false;
    createBtn.disabled = false;
    
    if (result) {
        newTitleInput.value = "";
        render();
    }
}

async function render() {
    if (editingId) return; // Don't refresh while editing
    
    setStatus("Syncing...", "loading");
    
    const todos = await api("/api/todos");
    if (todos === null) return;
    
    if (!Array.isArray(todos) || todos.length === 0) {
        setStatus("All clear!", "success");
        renderEmptyState();
        return;
    }
    
    // Sort: incomplete first, then by title
    todos.sort((a, b) => {
        if (a.done !== b.done) return a.done ? 1 : -1;
        return (a.title || "").localeCompare(b.title || "");
    });
    
    const doneCount = todos.filter(t => t.done).length;
    const totalCount = todos.length;
    
    if (doneCount === totalCount) {
        setStatus(`All ${totalCount} done!`, "success");
    } else {
        setStatus(`${doneCount}/${totalCount} completed`, "");
    }
    
    list.innerHTML = "";
    todos.forEach(todo => {
        list.appendChild(createTaskElement(todo));
    });
}

// Event listeners
createBtn.onclick = create;
newTitleInput.onkeypress = e => {
    if (e.key === "Enter") {
        e.preventDefault();
        create();
    }
};

// Initial load
render();

// Auto-refresh every 30 seconds (but not while editing)
setInterval(() => {
    if (!editingId) render();
}, 30000);
