-- Migration 001: Add learning carousel columns
-- Date: 2026-03-28
-- Description: Add learning_topic and learning_card for carousel feature

ALTER TABLE users ADD COLUMN learning_topic VARCHAR(20);
ALTER TABLE users ADD COLUMN learning_card INTEGER DEFAULT 1;
