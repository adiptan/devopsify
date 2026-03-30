-- Migration 002: Add auto training columns
-- Date: 2026-03-28
-- Description: Add auto_training_enabled and auto_training_frequency

ALTER TABLE users ADD COLUMN auto_training_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN auto_training_frequency VARCHAR(20) DEFAULT 'hourly';
-- Варианты: 'hourly', 'daily', 'twice_daily', 'thrice_daily'
