CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    due_date DATETIME,
    priority TEXT CHECK(priority IN ('high', 'medium', 'low')),
    status TEXT CHECK(status IN ('pending', 'complete')) DEFAULT 'pending',
    created_at DATETIME DEFAULT (datetime('now', 'localtime')),
    completed_at DATETIME,
    updated_at DATETIME DEFAULT (datetime('now', 'localtime'))
);

CREATE INDEX IF NOT EXISTS idx_reminders_status ON reminders(status);
CREATE INDEX IF NOT EXISTS idx_reminders_due_date ON reminders(due_date);
CREATE INDEX IF NOT EXISTS idx_reminders_created_at ON reminders(created_at);

CREATE TABLE IF NOT EXISTS conversations(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE,
    title TEXT,
    created_at DATETIME DEFAULT (datetime('now', 'localtime')),
    updated_at DATETIME DEFAULT (datetime('now', 'localtime')),
    message_count INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);

CREATE TABLE IF NOT EXISTS messages(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    role TEXT CHECK(role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT (datetime('now', 'localtime')),  -- 使用本地时间
,
    tool_used TEXT
);

CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);