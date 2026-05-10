-- Smart Task Management System — Database Schema
-- PostgreSQL 14+
-- Run: psql -U postgres -d taskmanager -f schema.sql

-- Drop existing tables (for clean reinstall)
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS users;

-- Users table
CREATE TABLE users (
    id            SERIAL       PRIMARY KEY,
    username      VARCHAR(80)  UNIQUE NOT NULL,
    email         VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Tasks table
CREATE TABLE tasks (
    id          SERIAL      PRIMARY KEY,
    user_id     INTEGER     NOT NULL
                    REFERENCES users(id) ON DELETE CASCADE,
    title       VARCHAR(200) NOT NULL,
    description TEXT,
    priority    VARCHAR(10)  NOT NULL DEFAULT 'medium'
                    CHECK (priority IN ('low', 'medium', 'high')),
    status      VARCHAR(20)  NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'in_progress', 'done')),
    created_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Indexes for common query patterns
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status  ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
