CREATE TABLE IF NOT EXISTS t_p12699901_blue_site_submission.applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram TEXT NOT NULL,
    minecraft_nick TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    token TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);