/**
 * AI Project Manager OS - Main Application
 */

// API Base URL
const API_BASE = '/api';

// Application State
const AppState = {
    currentProject: null,
    currentView: 'dashboard',
    notifications: [],
    projects: []
};

// Initialize Application
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Project Manager OS initialized');
    initializeNavigation();
    loadProjects();
    loadNotifications();
});

// Navigation
function initializeNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const view = this.dataset.view;
            navigateTo(view);
        });
    });
}

function navigateTo(view) {
    AppState.currentView = view;
    
    // Update active state
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.view === view) {
            item.classList.add('active');
        }
    });
    
    // Load view content
    loadView(view);
}

function loadView(view) {
    const contentDiv = document.getElementById('view-content');
    if (!contentDiv) return;
    
    switch(view) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'projects':
            loadProjectsView();
            break;
        case 'chat':
            loadChatView();
            break;
        case 'factory':
            loadFactoryView();
            break;
        case 'builder':
            loadBuilderView();
            break;
        case 'timeline':
            loadTimelineView();
            break;
        case 'notifications':
            loadNotificationsView();
            break;
        default:
            contentDiv.innerHTML = '<p>View not found</p>';
    }
}

// Projects
async function loadProjects() {
    try {
        const response = await fetch(`${API_BASE}/projects`);
        const data = await response.json();
        AppState.projects = data.projects || [];
        renderProjectsList();
    } catch (error) {
        console.error('Failed to load projects:', error);
    }
}

function renderProjectsList() {
    const container = document.getElementById('projects-list');
    if (!container) return;
    
    if (AppState.projects.length === 0) {
        container.innerHTML = '<p>No projects yet. Create your first project!</p>';
        return;
    }
    
    container.innerHTML = AppState.projects.map(project => `
        <div class="card" onclick="selectProject('${project.id}')">
            <div class="card-header">
                <h3 class="card-title">${escapeHtml(project.name)}</h3>
                <span class="badge badge-${project.status === 'active' ? 'success' : 'secondary'}">${project.status}</span>
            </div>
            <p>${escapeHtml(project.description || 'No description')}</p>
            <div style="margin-top: 1rem;">
                <span class="badge badge-info">Layer 2: ${project.layer2_status || 'not_started'}</span>
                <span class="badge badge-info">Layer 3: ${project.layer3_status || 'not_started'}</span>
            </div>
        </div>
    `).join('');
}

async function createProject(name, description) {
    try {
        const response = await fetch(`${API_BASE}/projects`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description })
        });
        
        if (response.ok) {
            await loadProjects();
            return true;
        }
        return false;
    } catch (error) {
        console.error('Failed to create project:', error);
        return false;
    }
}

function selectProject(projectId) {
    AppState.currentProject = projectId;
    navigateTo('chat');
}

// Notifications
async function loadNotifications() {
    try {
        const response = await fetch(`${API_BASE}/notifications`);
        const data = await response.json();
        AppState.notifications = data.notifications || [];
        renderNotifications();
    } catch (error) {
        console.error('Failed to load notifications:', error);
    }
}

function renderNotifications() {
    const container = document.getElementById('notifications-list');
    if (!container) return;
    
    const unreadCount = AppState.notifications.filter(n => !n.is_read).length;
    document.getElementById('notification-count').textContent = unreadCount;
    
    if (AppState.notifications.length === 0) {
        container.innerHTML = '<p>No notifications</p>';
        return;
    }
    
    container.innerHTML = AppState.notifications.slice(0, 10).map(notif => `
        <div class="notification ${!notif.is_read ? 'unread' : ''}">
            <div>
                <strong>${escapeHtml(notif.title)}</strong>
                <p>${escapeHtml(notif.message)}</p>
                <small>${notif.created_at}</small>
            </div>
        </div>
    `).join('');
}

// Dashboard
function loadDashboard() {
    const contentDiv = document.getElementById('view-content');
    if (!contentDiv) return;
    
    contentDiv.innerHTML = `
        <div class="header">
            <h1>Dashboard</h1>
            <button class="btn btn-primary" onclick="showCreateProjectModal()">+ New Project</button>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
            <div class="card">
                <h3>Total Projects</h3>
                <p style="font-size: 2rem; font-weight: bold;">${AppState.projects.length}</p>
            </div>
            <div class="card">
                <h3>Active Builds</h3>
                <p style="font-size: 2rem; font-weight: bold;">0</p>
            </div>
            <div class="card">
                <h3>Pending Reviews</h3>
                <p style="font-size: 2rem; font-weight: bold;">0</p>
            </div>
            <div class="card">
                <h3>Notifications</h3>
                <p style="font-size: 2rem; font-weight: bold;">${AppState.notifications.filter(n => !n.is_read).length}</p>
            </div>
        </div>
        
        <div class="card">
            <h3>Recent Projects</h3>
            <div id="projects-list">${renderProjectsList()}</div>
        </div>
    `;
    
    renderProjectsList();
}

function loadProjectsView() {
    const contentDiv = document.getElementById('view-content');
    if (!contentDiv) return;
    
    contentDiv.innerHTML = `
        <div class="header">
            <h1>Projects</h1>
            <button class="btn btn-primary" onclick="showCreateProjectModal()">+ New Project</button>
        </div>
        <div class="card">
            <div id="projects-list"></div>
        </div>
    `;
    
    renderProjectsList();
}

function loadChatView() {
    const contentDiv = document.getElementById('view-content');
    if (!contentDiv) return;
    
    contentDiv.innerHTML = `
        <div class="header">
            <h1>AI Chat</h1>
            ${AppState.currentProject ? `<span class="badge badge-info">Project: ${AppState.currentProject}</span>` : ''}
        </div>
        <div class="card">
            <div class="chat-container">
                <div class="chat-messages" id="chat-messages">
                    <p class="chat-message assistant">Hello! How can I help you with your project today?</p>
                </div>
                <div class="chat-input">
                    <textarea id="chat-input-text" placeholder="Type your message..." rows="3"></textarea>
                    <button class="btn btn-primary" onclick="sendChatMessage()">Send</button>
                </div>
            </div>
        </div>
    `;
}

function loadFactoryView() {
    const contentDiv = document.getElementById('view-content');
    if (!contentDiv) return;
    
    contentDiv.innerHTML = `
        <div class="header">
            <h1>Project Factory (Layer 2)</h1>
        </div>
        <div class="card">
            <h3>Generate Specification Documents</h3>
            <p>The Factory generates 22 specification documents from your project idea and references.</p>
            <form id="factory-form" style="margin-top: 1rem;">
                <div class="form-group">
                    <label class="form-label">Project Idea</label>
                    <textarea class="form-input form-textarea" id="factory-idea" placeholder="Describe your project idea..."></textarea>
                </div>
                <div class="form-group">
                    <label class="form-label">References (optional)</label>
                    <input type="file" class="form-input" multiple id="factory-references">
                </div>
                <button type="submit" class="btn btn-primary">Start Factory</button>
            </form>
        </div>
    `;
    
    document.getElementById('factory-form').addEventListener('submit', handleFactorySubmit);
}

function loadBuilderView() {
    const contentDiv = document.getElementById('view-content');
    if (!contentDiv) return;
    
    contentDiv.innerHTML = `
        <div class="header">
            <h1>Project Builder (Layer 3)</h1>
        </div>
        <div class="card">
            <h3>Build from Specification</h3>
            <p>Select a project with frozen specification to generate source code.</p>
            <button class="btn btn-primary" onclick="startBuild()">Start Build</button>
        </div>
    `;
}

function loadTimelineView() {
    const contentDiv = document.getElementById('view-content');
    if (!contentDiv) return;
    
    contentDiv.innerHTML = `
        <div class="header">
            <h1>Timeline</h1>
        </div>
        <div class="card">
            <p>Project activity timeline will appear here.</p>
        </div>
    `;
}

function loadNotificationsView() {
    const contentDiv = document.getElementById('view-content');
    if (!contentDiv) return;
    
    contentDiv.innerHTML = `
        <div class="header">
            <h1>Notifications</h1>
            <button class="btn btn-outline" onclick="markAllRead()">Mark All Read</button>
        </div>
        <div class="card">
            <div id="notifications-list"></div>
        </div>
    `;
    
    renderNotifications();
}

// Chat Functions
async function sendChatMessage() {
    const input = document.getElementById('chat-input-text');
    const messagesDiv = document.getElementById('chat-messages');
    
    if (!input.value.trim()) return;
    
    // Add user message
    const userMsg = document.createElement('div');
    userMsg.className = 'chat-message user';
    userMsg.textContent = input.value;
    messagesDiv.appendChild(userMsg);
    
    // Send to API
    try {
        const response = await fetch(`${API_BASE}/chats`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                project_id: AppState.currentProject,
                message: input.value
            })
        });
        
        // For now, show placeholder response
        const assistantMsg = document.createElement('div');
        assistantMsg.className = 'chat-message assistant';
        assistantMsg.textContent = 'Response will appear here when AI is connected.';
        messagesDiv.appendChild(assistantMsg);
        
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    } catch (error) {
        console.error('Failed to send message:', error);
    }
    
    input.value = '';
}

// Factory Functions
async function handleFactorySubmit(e) {
    e.preventDefault();
    
    const idea = document.getElementById('factory-idea').value;
    
    if (!idea.trim()) {
        alert('Please enter a project idea');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/factory/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                project_name: 'New Project',
                idea: idea
            })
        });
        
        if (response.ok) {
            alert('Factory job started! Check the timeline for progress.');
        } else {
            alert('Failed to start factory job');
        }
    } catch (error) {
        console.error('Factory error:', error);
        alert('Error starting factory job');
    }
}

// Builder Functions
async function startBuild() {
    if (!AppState.currentProject) {
        alert('Please select a project first');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/builder/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                project_id: AppState.currentProject
            })
        });
        
        if (response.ok) {
            alert('Build started! Check the timeline for progress.');
        } else {
            alert('Failed to start build');
        }
    } catch (error) {
        console.error('Build error:', error);
        alert('Error starting build');
    }
}

// Utilities
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showCreateProjectModal() {
    const name = prompt('Enter project name:');
    if (!name) return;
    
    const description = prompt('Enter project description (optional):') || '';
    
    createProject(name, description).then(success => {
        if (success) {
            alert('Project created successfully!');
        } else {
            alert('Failed to create project');
        }
    });
}

function markAllRead() {
    // Implementation pending
    alert('Mark all as read - coming soon');
}
