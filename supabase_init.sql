-- Create necessary enums
CREATE TYPE risk_level_enum AS ENUM ('low', 'medium', 'high');
CREATE TYPE moderation_action_enum AS ENUM ('none', 'deleted', 'reported', 'whitelisted');

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR NOT NULL UNIQUE,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- YouTube integration
    youtube_token TEXT,
    youtube_refresh_token TEXT,
    youtube_token_expires TIMESTAMP WITH TIME ZONE,
    youtube_channel_id VARCHAR,
    youtube_channel_name VARCHAR,
    
    -- User preferences
    preferences JSONB
);

-- Comments table for storing YouTube comments and their spam classification
CREATE TABLE IF NOT EXISTS comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    
    -- YouTube specific
    youtube_comment_id VARCHAR NOT NULL UNIQUE,
    youtube_video_id VARCHAR NOT NULL,
    youtube_channel_id VARCHAR NOT NULL,
    content TEXT NOT NULL,
    author_name VARCHAR NOT NULL,
    author_channel_id VARCHAR NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Spam classification
    spam_probability FLOAT NOT NULL DEFAULT 0.0,
    risk_level risk_level_enum NOT NULL DEFAULT 'low',
    is_spam BOOLEAN DEFAULT FALSE,
    detection_features JSONB,  -- Store features used in detection
    
    -- Actions
    is_deleted BOOLEAN DEFAULT FALSE,
    is_whitelisted BOOLEAN DEFAULT FALSE,
    is_auto_moderated BOOLEAN DEFAULT FALSE,
    moderation_action moderation_action_enum DEFAULT 'none',
    moderated_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indices for faster querying
CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_comments_youtube_video_id ON comments(youtube_video_id);
CREATE INDEX idx_comments_risk_level ON comments(risk_level);
CREATE INDEX idx_comments_is_spam ON comments(is_spam);

-- ML Settings table for storing user preferences for spam detection
CREATE TABLE IF NOT EXISTS ml_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id),
    
    -- Spam detection settings
    sensitivity INTEGER DEFAULT 75,  -- 0-100 scale
    keywords JSONB DEFAULT '[]'::jsonb,  -- List of spam keywords
    bot_patterns JSONB DEFAULT '[]'::jsonb,  -- List of regex patterns for bot detection
    auto_delete BOOLEAN DEFAULT FALSE,  -- Auto-delete high confidence spam
    
    -- Additional settings
    high_risk_threshold FLOAT DEFAULT 0.8,  -- Probability threshold for high risk
    medium_risk_threshold FLOAT DEFAULT 0.4,  -- Probability threshold for medium risk
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add Row Level Security (RLS) policies
-- Users can only see and modify their own data

-- Enable RLS on tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE ml_settings ENABLE ROW LEVEL SECURITY;

-- User policies
CREATE POLICY users_select ON users 
    FOR SELECT USING (auth.uid() = id);
    
CREATE POLICY users_update ON users 
    FOR UPDATE USING (auth.uid() = id);

-- Comments policies
CREATE POLICY comments_select ON comments 
    FOR SELECT USING (auth.uid() = user_id);
    
CREATE POLICY comments_insert ON comments 
    FOR INSERT WITH CHECK (auth.uid() = user_id);
    
CREATE POLICY comments_update ON comments 
    FOR UPDATE USING (auth.uid() = user_id);
    
CREATE POLICY comments_delete ON comments 
    FOR DELETE USING (auth.uid() = user_id);

-- ML Settings policies
CREATE POLICY ml_settings_select ON ml_settings 
    FOR SELECT USING (auth.uid() = user_id);
    
CREATE POLICY ml_settings_insert ON ml_settings 
    FOR INSERT WITH CHECK (auth.uid() = user_id);
    
CREATE POLICY ml_settings_update ON ml_settings 
    FOR UPDATE USING (auth.uid() = user_id);

-- Create triggers to update the updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_comments_updated_at
    BEFORE UPDATE ON comments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ml_settings_updated_at
    BEFORE UPDATE ON ml_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Additional tables that might be useful:

-- Videos table to store information about YouTube videos
CREATE TABLE IF NOT EXISTS videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    youtube_video_id VARCHAR NOT NULL UNIQUE,
    title VARCHAR NOT NULL,
    description TEXT,
    published_at TIMESTAMP WITH TIME ZONE NOT NULL,
    thumbnail_url VARCHAR,
    view_count INTEGER,
    like_count INTEGER,
    comment_count INTEGER,
    
    -- Spam metrics
    spam_comment_count INTEGER DEFAULT 0,
    spam_percentage FLOAT DEFAULT 0.0,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on videos table
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;

-- Videos policies
CREATE POLICY videos_select ON videos 
    FOR SELECT USING (auth.uid() = user_id);
    
CREATE POLICY videos_insert ON videos 
    FOR INSERT WITH CHECK (auth.uid() = user_id);
    
CREATE POLICY videos_update ON videos 
    FOR UPDATE USING (auth.uid() = user_id);

CREATE TRIGGER update_videos_updated_at
    BEFORE UPDATE ON videos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comment keywords table to track frequency of spam keywords
CREATE TABLE IF NOT EXISTS comment_keywords (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    keyword VARCHAR NOT NULL,
    count INTEGER DEFAULT 1,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, keyword)
);

-- Enable RLS on comment_keywords table
ALTER TABLE comment_keywords ENABLE ROW LEVEL SECURITY;

-- Comment keywords policies
CREATE POLICY comment_keywords_select ON comment_keywords 
    FOR SELECT USING (auth.uid() = user_id);
    
CREATE POLICY comment_keywords_insert ON comment_keywords 
    FOR INSERT WITH CHECK (auth.uid() = user_id);
    
CREATE POLICY comment_keywords_update ON comment_keywords 
    FOR UPDATE USING (auth.uid() = user_id);

CREATE TRIGGER update_comment_keywords_updated_at
    BEFORE UPDATE ON comment_keywords
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Channel authors table to track spammers by channel
CREATE TABLE IF NOT EXISTS channel_authors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    author_channel_id VARCHAR NOT NULL,
    author_name VARCHAR NOT NULL,
    spam_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 1,
    last_comment_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, author_channel_id)
);

-- Enable RLS on channel_authors table
ALTER TABLE channel_authors ENABLE ROW LEVEL SECURITY;

-- Channel authors policies
CREATE POLICY channel_authors_select ON channel_authors 
    FOR SELECT USING (auth.uid() = user_id);
    
CREATE POLICY channel_authors_insert ON channel_authors 
    FOR INSERT WITH CHECK (auth.uid() = user_id);
    
CREATE POLICY channel_authors_update ON channel_authors 
    FOR UPDATE USING (auth.uid() = user_id);

CREATE TRIGGER update_channel_authors_updated_at
    BEFORE UPDATE ON channel_authors
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 